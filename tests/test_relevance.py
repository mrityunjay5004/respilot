import pytest
from unittest.mock import patch, MagicMock
from app.executor import Executor
from app.state import AgentState, Step
from app.tools.base import BaseTool

class MockTool(BaseTool):
    name = "mock_tool"
    description = "A mock tool"
    def run(self, **kwargs):
        pass

@patch("app.executor.call_llm")
@patch("app.executor.call_llm_json")
def test_relevance_check_rejects_irrelevant_results(mock_call_llm_json, mock_call_llm):
    # Mock LLM generation for kwargs
    mock_call_llm_json.return_value = {"query": "tops"}
    # Mock LLM relevance check to return 'NO'
    mock_call_llm.return_value = "NO"

    mock_search = MagicMock()
    mock_search.run.return_value = MagicMock(success=True, data=[{"title": "Retail Tops", "url": "http", "snippet": "Buy tops"}], metadata={})
    
    executor = Executor(tools={"web_search": mock_search}, max_retries=0)
    state = AgentState(user_goal="Find AI companies")
    step = Step(step=1, tool="web_search", description="Search AI companies")

    # Should return False because relevance check fails and max_retries is 0
    result = executor.execute_step(step, state)
    
    assert not result
    assert "Irrelevant search results" in state.failures[0]["error"]
    
@patch("app.executor.call_llm")
@patch("app.executor.call_llm_json")
def test_fallback_to_wikipedia(mock_call_llm_json, mock_call_llm):
    mock_call_llm_json.return_value = {"query": "test"}
    mock_call_llm.return_value = "NO" # Always reject web_search results

    mock_search = MagicMock()
    mock_search.run.return_value = MagicMock(success=True, data=[{"title": "Bad", "url": "http", "snippet": "Bad"}], metadata={})
    
    mock_wiki = MagicMock()
    mock_wiki.run.return_value = MagicMock(success=True, data=[{"title": "Good", "url": "http", "snippet": "Good"}], metadata={})
    
    # We need to let the relevance check pass when tool is wikipedia, but we mock call_llm globally.
    # Let's make call_llm return YES on the third call (which is attempt=3, tool=wikipedia).
    mock_call_llm.side_effect = ["NO", "NO", "YES"]
    
    executor = Executor(tools={"web_search": mock_search, "wikipedia": mock_wiki}, max_retries=2)
    state = AgentState(user_goal="Find AI companies")
    step = Step(step=1, tool="web_search", description="Search AI companies")

    result = executor.execute_step(step, state)
    
    assert result is True
    assert step.tool == "wikipedia" # Tool should have switched
    assert mock_wiki.run.called
