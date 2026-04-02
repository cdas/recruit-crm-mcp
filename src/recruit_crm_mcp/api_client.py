"""Recruit CRM API Client with rate limiting and comprehensive endpoint support."""

from __future__ import annotations

import asyncio
import os
import time
from typing import Any

import httpx


class RecruitCRMError(Exception):
    """Exception raised for Recruit CRM API errors."""

    def __init__(self, message: str, status_code: int | None = None, details: dict | None = None):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class RateLimiter:
    """Simple token bucket rate limiter for 60 requests per minute."""

    def __init__(self, requests_per_minute: int = 60):
        self.requests_per_minute = requests_per_minute
        self.tokens = requests_per_minute
        self.last_refill = time.monotonic()
        self._lock = asyncio.Lock()

    async def acquire(self):
        """Acquire a token, waiting if necessary."""
        async with self._lock:
            now = time.monotonic()
            elapsed = now - self.last_refill

            # Refill tokens based on elapsed time
            refill = elapsed * (self.requests_per_minute / 60.0)
            self.tokens = min(self.requests_per_minute, self.tokens + refill)
            self.last_refill = now

            if self.tokens < 1:
                # Wait until we have a token
                wait_time = (1 - self.tokens) * (60.0 / self.requests_per_minute)
                await asyncio.sleep(wait_time)
                self.tokens = 0
            else:
                self.tokens -= 1


class RecruitCRMClient:
    """Client for interacting with the Recruit CRM API."""

    BASE_URL = "https://api.recruitcrm.io/v1"

    def __init__(self, api_token: str | None = None):
        self.api_token = api_token or os.environ.get("RECRUIT_CRM_API_TOKEN")
        if not self.api_token:
            raise RecruitCRMError("API token is required. Set RECRUIT_CRM_API_TOKEN environment variable.")

        self._client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            headers={
                "Authorization": f"Bearer {self.api_token}",
                "Accept": "application/json",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )
        self._rate_limiter = RateLimiter(requests_per_minute=60)

    async def close(self):
        """Close the HTTP client."""
        await self._client.aclose()

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        json_data: dict[str, Any] | None = None,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        """Make an API request with rate limiting and retry logic."""
        last_error = None

        for attempt in range(max_retries):
            # Acquire rate limit token
            await self._rate_limiter.acquire()

            try:
                response = await self._client.request(
                    method=method,
                    url=endpoint,
                    params=params,
                    json=json_data,
                )

                # Handle rate limit with retry
                if response.status_code == 429:
                    retry_after = int(response.headers.get("Retry-After", 60))
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_after)
                        continue
                    raise RecruitCRMError(
                        "Rate limit exceeded. Please wait before making more requests.",
                        429
                    )

                # Handle authentication error
                if response.status_code == 401:
                    raise RecruitCRMError(
                        "API token is invalid or expired. Check your RECRUIT_CRM_API_TOKEN.",
                        401
                    )

                # Handle not found
                if response.status_code == 404:
                    raise RecruitCRMError(
                        "Resource not found. Please verify the slug/ID is correct.",
                        404
                    )

                # Handle validation errors
                if response.status_code == 422:
                    error_data = {}
                    try:
                        error_data = response.json()
                    except Exception:
                        pass
                    raise RecruitCRMError(
                        f"Validation error: {error_data.get('message', response.text)}",
                        422,
                        error_data
                    )

                # Handle other errors
                if response.status_code >= 400:
                    error_msg = response.text
                    try:
                        error_data = response.json()
                        error_msg = error_data.get("message", error_msg)
                    except Exception:
                        pass
                    raise RecruitCRMError(f"API error: {error_msg}", response.status_code)

                # Handle no content
                if response.status_code == 204:
                    return {"success": True}

                return response.json()

            except httpx.RequestError as e:
                last_error = RecruitCRMError(f"Request failed: {str(e)}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue
                raise last_error

        raise last_error or RecruitCRMError("Request failed after retries")

    # =========================================================================
    # CANDIDATES - Basic CRUD (existing)
    # =========================================================================

    async def list_candidates(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all candidates with pagination."""
        return await self._request("GET", "/candidates", params={"page": page, "limit": limit})

    async def search_candidates(self, query: str, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search candidates by query string."""
        return await self._request("GET", "/candidates/search", params={"q": query, "page": page, "limit": limit})

    async def get_candidate(self, candidate_slug: str) -> dict[str, Any]:
        """Get a specific candidate by slug."""
        return await self._request("GET", f"/candidates/{candidate_slug}")

    async def create_candidate(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new candidate."""
        return await self._request("POST", "/candidates", json_data=data)

    async def update_candidate(self, candidate_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing candidate."""
        return await self._request("PUT", f"/candidates/{candidate_slug}", json_data=data)

    async def delete_candidate(self, candidate_slug: str) -> dict[str, Any]:
        """Delete a candidate."""
        return await self._request("DELETE", f"/candidates/{candidate_slug}")

    # =========================================================================
    # CANDIDATES - Pipeline & Pitch (Priority 1)
    # =========================================================================

    async def assign_candidate_to_job(
        self, candidate_slug: str, job_slug: str, hiring_stage_id: int = 1
    ) -> dict[str, Any]:
        """Assign a candidate to a job pipeline."""
        return await self._request(
            "POST",
            f"/candidates/{candidate_slug}/assign",
            json_data={"job_slug": job_slug, "hiring_stage_id": hiring_stage_id}
        )

    async def unassign_candidate_from_job(self, candidate_slug: str, job_slug: str) -> dict[str, Any]:
        """Remove a candidate from a job pipeline."""
        return await self._request("DELETE", f"/candidates/{candidate_slug}/assign/{job_slug}")

    async def update_hiring_stage(
        self, candidate_slug: str, job_slug: str, hiring_stage_id: int
    ) -> dict[str, Any]:
        """Update the hiring stage for a candidate in a job."""
        return await self._request(
            "PUT",
            f"/candidates/{candidate_slug}/hiring-stage",
            json_data={"job_slug": job_slug, "hiring_stage_id": hiring_stage_id}
        )

    async def get_candidate_history(self, candidate_slug: str) -> dict[str, Any]:
        """Get the hiring stage history of a candidate."""
        return await self._request("GET", f"/candidates/{candidate_slug}/history")

    async def get_candidate_jobs(self, candidate_slug: str) -> dict[str, Any]:
        """Get all jobs a candidate is assigned to."""
        return await self._request("GET", f"/candidates/{candidate_slug}/jobs")

    async def get_job_candidates(self, job_slug: str, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all candidates in a job pipeline."""
        return await self._request(
            "GET", f"/jobs/{job_slug}/candidates",
            params={"page": page, "limit": limit}
        )

    async def pitch_candidate(
        self, candidate_slug: str, contact_slug: str, job_slug: str, message: str = ""
    ) -> dict[str, Any]:
        """Pitch a candidate to a contact for a job."""
        return await self._request(
            "POST",
            f"/candidates/{candidate_slug}/pitch",
            json_data={
                "contact_slug": contact_slug,
                "job_slug": job_slug,
                "message": message
            }
        )

    async def get_candidate_pitches(self, candidate_slug: str) -> dict[str, Any]:
        """Get all contacts a candidate has been pitched to."""
        return await self._request("GET", f"/candidates/{candidate_slug}/pitched-contacts")

    async def get_offlimit_candidates(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all off-limit candidates."""
        return await self._request("GET", "/candidates/offlimit", params={"page": page, "limit": limit})

    async def get_candidate_questions(self, candidate_slug: str) -> dict[str, Any]:
        """Get screening questions and answers for a candidate."""
        return await self._request("GET", f"/candidates/{candidate_slug}/questions")

    async def update_candidate_visibility(
        self, candidate_slug: str, job_slug: str, visible: bool
    ) -> dict[str, Any]:
        """Update candidate visibility in a job."""
        return await self._request(
            "PUT",
            f"/candidates/{candidate_slug}/visibility",
            json_data={"job_slug": job_slug, "visible": visible}
        )

    # =========================================================================
    # COMPANIES - Basic CRUD (existing)
    # =========================================================================

    async def list_companies(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all companies with pagination."""
        return await self._request("GET", "/companies", params={"page": page, "limit": limit})

    async def get_company(self, company_slug: str) -> dict[str, Any]:
        """Get a specific company by slug."""
        return await self._request("GET", f"/companies/{company_slug}")

    async def create_company(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new company."""
        return await self._request("POST", "/companies", json_data=data)

    async def update_company(self, company_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing company."""
        return await self._request("PUT", f"/companies/{company_slug}", json_data=data)

    async def delete_company(self, company_slug: str) -> dict[str, Any]:
        """Delete a company."""
        return await self._request("DELETE", f"/companies/{company_slug}")

    async def search_companies(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search companies with filters."""
        return await self._request(
            "POST", "/companies/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # CONTACTS - Basic CRUD (existing)
    # =========================================================================

    async def list_contacts(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all contacts with pagination."""
        return await self._request("GET", "/contacts", params={"page": page, "limit": limit})

    async def get_contact(self, contact_slug: str) -> dict[str, Any]:
        """Get a specific contact by slug."""
        return await self._request("GET", f"/contacts/{contact_slug}")

    async def create_contact(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new contact."""
        return await self._request("POST", "/contacts", json_data=data)

    async def update_contact(self, contact_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing contact."""
        return await self._request("PUT", f"/contacts/{contact_slug}", json_data=data)

    async def delete_contact(self, contact_slug: str) -> dict[str, Any]:
        """Delete a contact."""
        return await self._request("DELETE", f"/contacts/{contact_slug}")

    async def search_contacts(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search contacts with filters."""
        return await self._request(
            "POST", "/contacts/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # JOBS - Basic CRUD (existing)
    # =========================================================================

    async def list_jobs(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all jobs with pagination."""
        return await self._request("GET", "/jobs", params={"page": page, "limit": limit})

    async def get_job(self, job_slug: str) -> dict[str, Any]:
        """Get a specific job by slug."""
        return await self._request("GET", f"/jobs/{job_slug}")

    async def create_job(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new job."""
        return await self._request("POST", "/jobs", json_data=data)

    async def update_job(self, job_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing job."""
        return await self._request("PUT", f"/jobs/{job_slug}", json_data=data)

    async def delete_job(self, job_slug: str) -> dict[str, Any]:
        """Delete a job."""
        return await self._request("DELETE", f"/jobs/{job_slug}")

    async def search_jobs(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search jobs with filters."""
        return await self._request(
            "POST", "/jobs/search",
            json_data={**data, "page": page, "limit": limit}
        )

    async def get_job_associated_fields(self, job_slug: str) -> dict[str, Any]:
        """Get associated fields for a job."""
        return await self._request("GET", f"/jobs/{job_slug}/associated-fields")

    async def update_job_associated_fields(self, job_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update associated fields for a job."""
        return await self._request("PUT", f"/jobs/{job_slug}/associated-fields", json_data=data)

    # =========================================================================
    # DEALS - Revenue Tracking (Priority 2)
    # =========================================================================

    async def list_deals(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all deals with pagination."""
        return await self._request("GET", "/deals", params={"page": page, "limit": limit})

    async def get_deal(self, deal_slug: str) -> dict[str, Any]:
        """Get a specific deal by slug."""
        return await self._request("GET", f"/deals/{deal_slug}")

    async def create_deal(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new deal."""
        return await self._request("POST", "/deals", json_data=data)

    async def update_deal(self, deal_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing deal."""
        return await self._request("PUT", f"/deals/{deal_slug}", json_data=data)

    async def delete_deal(self, deal_slug: str) -> dict[str, Any]:
        """Delete a deal."""
        return await self._request("DELETE", f"/deals/{deal_slug}")

    async def search_deals(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search deals with filters."""
        return await self._request(
            "POST", "/deals/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # NOTES - Activity Documentation (Priority 2)
    # =========================================================================

    async def list_notes(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all notes with pagination."""
        return await self._request("GET", "/notes", params={"page": page, "limit": limit})

    async def get_note(self, note_slug: str) -> dict[str, Any]:
        """Get a specific note by slug."""
        return await self._request("GET", f"/notes/{note_slug}")

    async def create_note(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new note. Can be linked to candidate, contact, company, job, or deal."""
        return await self._request("POST", "/notes", json_data=data)

    async def update_note(self, note_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing note."""
        return await self._request("PUT", f"/notes/{note_slug}", json_data=data)

    async def delete_note(self, note_slug: str) -> dict[str, Any]:
        """Delete a note."""
        return await self._request("DELETE", f"/notes/{note_slug}")

    async def search_notes(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search notes with filters."""
        return await self._request(
            "POST", "/notes/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # TASKS - Follow-up Management (Priority 2)
    # =========================================================================

    async def list_tasks(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all tasks with pagination."""
        return await self._request("GET", "/tasks", params={"page": page, "limit": limit})

    async def get_task(self, task_slug: str) -> dict[str, Any]:
        """Get a specific task by slug."""
        return await self._request("GET", f"/tasks/{task_slug}")

    async def create_task(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new task."""
        return await self._request("POST", "/tasks", json_data=data)

    async def update_task(self, task_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing task."""
        return await self._request("PUT", f"/tasks/{task_slug}", json_data=data)

    async def delete_task(self, task_slug: str) -> dict[str, Any]:
        """Delete a task."""
        return await self._request("DELETE", f"/tasks/{task_slug}")

    async def search_tasks(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search tasks with filters."""
        return await self._request(
            "POST", "/tasks/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # MEETINGS (Priority 2)
    # =========================================================================

    async def list_meetings(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all meetings with pagination."""
        return await self._request("GET", "/meetings", params={"page": page, "limit": limit})

    async def get_meeting(self, meeting_slug: str) -> dict[str, Any]:
        """Get a specific meeting by slug."""
        return await self._request("GET", f"/meetings/{meeting_slug}")

    async def create_meeting(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new meeting."""
        return await self._request("POST", "/meetings", json_data=data)

    async def update_meeting(self, meeting_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing meeting."""
        return await self._request("PUT", f"/meetings/{meeting_slug}", json_data=data)

    async def delete_meeting(self, meeting_slug: str) -> dict[str, Any]:
        """Delete a meeting."""
        return await self._request("DELETE", f"/meetings/{meeting_slug}")

    # =========================================================================
    # CALL LOGS (Priority 2)
    # =========================================================================

    async def list_call_logs(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all call logs with pagination."""
        return await self._request("GET", "/calllogs", params={"page": page, "limit": limit})

    async def get_call_log(self, call_log_slug: str) -> dict[str, Any]:
        """Get a specific call log by slug."""
        return await self._request("GET", f"/calllogs/{call_log_slug}")

    async def create_call_log(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new call log."""
        return await self._request("POST", "/calllogs", json_data=data)

    async def update_call_log(self, call_log_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing call log."""
        return await self._request("PUT", f"/calllogs/{call_log_slug}", json_data=data)

    # =========================================================================
    # HOTLISTS - Curated Lists (Priority 2)
    # =========================================================================

    async def list_hotlists(self, page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Get all hotlists with pagination."""
        return await self._request("GET", "/hotlists", params={"page": page, "limit": limit})

    async def get_hotlist(self, hotlist_slug: str) -> dict[str, Any]:
        """Get a specific hotlist by slug."""
        return await self._request("GET", f"/hotlists/{hotlist_slug}")

    async def create_hotlist(self, data: dict[str, Any]) -> dict[str, Any]:
        """Create a new hotlist."""
        return await self._request("POST", "/hotlists", json_data=data)

    async def update_hotlist(self, hotlist_slug: str, data: dict[str, Any]) -> dict[str, Any]:
        """Update an existing hotlist."""
        return await self._request("PUT", f"/hotlists/{hotlist_slug}", json_data=data)

    async def delete_hotlist(self, hotlist_slug: str) -> dict[str, Any]:
        """Delete a hotlist."""
        return await self._request("DELETE", f"/hotlists/{hotlist_slug}")

    async def add_record_to_hotlist(self, hotlist_slug: str, record_slug: str) -> dict[str, Any]:
        """Add a record (candidate/contact/company) to a hotlist."""
        return await self._request(
            "POST", f"/hotlists/{hotlist_slug}/records",
            json_data={"record_slug": record_slug}
        )

    async def remove_record_from_hotlist(self, hotlist_slug: str, record_slug: str) -> dict[str, Any]:
        """Remove a record from a hotlist."""
        return await self._request("DELETE", f"/hotlists/{hotlist_slug}/records/{record_slug}")

    async def search_hotlists(self, data: dict[str, Any], page: int = 1, limit: int = 25) -> dict[str, Any]:
        """Search hotlists with filters."""
        return await self._request(
            "POST", "/hotlists/search",
            json_data={**data, "page": page, "limit": limit}
        )

    # =========================================================================
    # METADATA & CONFIGURATION (Priority 3)
    # =========================================================================

    async def list_users(self) -> dict[str, Any]:
        """Get all team members/users."""
        return await self._request("GET", "/users")

    async def get_hiring_stages(self) -> dict[str, Any]:
        """Get all global hiring stages."""
        return await self._request("GET", "/hiring-stages")

    async def get_job_hiring_stages(self, job_slug: str) -> dict[str, Any]:
        """Get hiring stages for a specific job."""
        return await self._request("GET", f"/hiring-stages/{job_slug}")

    async def get_custom_fields(self) -> dict[str, Any]:
        """Get all custom fields with their types."""
        return await self._request("GET", "/custom-fields")

    # =========================================================================
    # WEBHOOKS / SUBSCRIPTIONS (Priority 4)
    # =========================================================================

    async def list_subscriptions(self) -> dict[str, Any]:
        """Get all webhook subscriptions."""
        return await self._request("GET", "/subscriptions")

    async def create_subscription(self, url: str, events: list[str]) -> dict[str, Any]:
        """Create a new webhook subscription."""
        return await self._request(
            "POST", "/subscriptions",
            json_data={"url": url, "events": events}
        )

    async def delete_subscription(self, subscription_id: str) -> dict[str, Any]:
        """Delete a webhook subscription."""
        return await self._request("DELETE", f"/subscriptions/{subscription_id}")
