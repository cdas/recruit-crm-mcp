# Security Policy

## API Token Safety

- **Never** commit your `RECRUIT_CRM_API_TOKEN` to version control
- Store the token in the `env` block of `claude_desktop_config.json` (see SETUP.md) or in a `.env` file that is listed in `.gitignore`
- Rotate your token immediately in Recruit CRM Admin Settings if you suspect it has been exposed

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

Open a GitHub Issue with the label **security**. Please include:
- A description of the vulnerability
- Steps to reproduce
- Potential impact

Do not include your actual API token or any credentials in the report.
