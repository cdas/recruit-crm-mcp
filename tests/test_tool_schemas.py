"""Schema validation tests for all 79 MCP tool definitions."""

import pytest

from recruit_crm_mcp.tools import get_tools

_ALL_TOOLS = get_tools()

_VALID_JSON_SCHEMA_TYPES = {"string", "integer", "number", "boolean", "array", "object", "null"}


def test_total_tool_count():
    assert len(_ALL_TOOLS) == 79


def test_tool_names_are_unique():
    names = [t.name for t in _ALL_TOOLS]
    duplicates = [n for n in set(names) if names.count(n) > 1]
    assert not duplicates, f"Duplicate tool names: {duplicates}"


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_tool_has_non_empty_name(tool):
    assert isinstance(tool.name, str) and tool.name.strip()


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_tool_has_non_empty_description(tool):
    assert isinstance(tool.description, str) and len(tool.description) > 10


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_input_schema_is_dict(tool):
    assert isinstance(tool.inputSchema, dict) and tool.inputSchema


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_input_schema_type_is_object(tool):
    assert tool.inputSchema.get("type") == "object"


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_input_schema_properties_is_dict(tool):
    props = tool.inputSchema.get("properties")
    assert isinstance(props, dict), f"{tool.name}: 'properties' must be a dict, got {type(props)}"


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_each_property_has_a_type(tool):
    """Every property in the schema must declare a JSON Schema type."""
    for prop_name, prop_schema in tool.inputSchema.get("properties", {}).items():
        assert "type" in prop_schema, (
            f"{tool.name}.{prop_name}: missing 'type' field"
        )
        assert prop_schema["type"] in _VALID_JSON_SCHEMA_TYPES, (
            f"{tool.name}.{prop_name}: invalid type '{prop_schema['type']}'"
        )


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_required_fields_exist_in_properties(tool):
    """Every field listed in 'required' must have an entry in 'properties'."""
    required = tool.inputSchema.get("required", [])
    properties = tool.inputSchema.get("properties", {})
    missing = [f for f in required if f not in properties]
    assert not missing, (
        f"{tool.name}: required fields missing from properties: {missing}"
    )


@pytest.mark.parametrize("tool", _ALL_TOOLS, ids=lambda t: t.name)
def test_each_property_has_a_description(tool):
    """Properties should document themselves — a missing description is a schema gap."""
    for prop_name, prop_schema in tool.inputSchema.get("properties", {}).items():
        assert "description" in prop_schema, (
            f"{tool.name}.{prop_name}: missing 'description'"
        )
