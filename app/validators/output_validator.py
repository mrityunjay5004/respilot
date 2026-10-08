from typing import Any, Dict, Tuple
from app.state import ToolResult

def validate_tool_output(tool_name: str, result: ToolResult) -> Tuple[bool, str]:
    """
    Validates that a tool's output matches the expected schema and semantic requirements.
    Returns (is_valid, error_message).
    """
    if not result.success:
        return False, f"Tool reported failure: {result.error}"

    if not result.data:
        return False, "Tool returned empty data."

    if tool_name == "web_search":
        if not isinstance(result.data, list):
            return False, "Web search results must be a list."
        for item in result.data:
            if not isinstance(item, dict):
                return False, "Web search result items must be dictionaries."
            if "title" not in item or "url" not in item or "snippet" not in item:
                return False, "Web search result missing required fields (title, url, snippet)."

    elif tool_name == "webpage_fetcher":
        if not isinstance(result.data, dict):
            return False, "Webpage fetcher result must be a dictionary."
        if "url" not in result.data or "text" not in result.data:
            return False, "Webpage fetcher missing required fields (url, text)."

    elif tool_name == "calculator":
        if not isinstance(result.data, dict):
            return False, "Calculator result must be a dictionary."
        if "result" not in result.data:
            return False, "Calculator missing result field."
            
    elif tool_name == "failure_simulator":
        # The simulator is designed to return bad data on its first attempt if mode is malformed_response
        if isinstance(result.data, dict) and "malformed" in result.data:
            return False, "Malformed response detected from tool."

    return True, ""
