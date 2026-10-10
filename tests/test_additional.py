import pytest
from unittest.mock import patch, MagicMock
from app.agent import ResearchAgent
from app.state import ToolResult, Plan, Step

@patch("app.tools.web_search.DDGS.text")
def test_web_search_execution(mock_search):
    from app.tools.web_search import WebSearchTool
    
    mock_search.return_value = [{"title": "Test Title", "href": "http://test.com", "body": "Test Snippet"}]
    
    tool = WebSearchTool()
    res = tool.run("test query")
    
    assert res.success
    assert len(res.data) == 1
    assert res.data[0]["title"] == "Test Title"
    assert res.data[0]["url"] == "http://test.com"

@patch("app.planner.call_llm_json")
@patch("app.executor.call_llm_json")
@patch("app.tools.web_search.WebSearchTool.run")
@patch("app.reporting.report_generator.call_llm")
def test_e2e_successful_run(mock_report_llm, mock_ws_run, mock_exec_llm, mock_plan_llm):
    # Mock Planner
    mock_plan_llm.return_value = {
        "goal": "Find latest AI news",
        "steps": [
            {"step": 1, "description": "Search AI news", "tool": "web_search"}
        ]
    }
    
    # Mock Executor
    mock_exec_llm.return_value = {"query": "latest AI news"}
    mock_ws_run.return_value = ToolResult(
        success=True, 
        tool_name="web_search", 
        data=[{"title": "AI News", "url": "https://news.ai", "snippet": "Lots of news"}],
        metadata={"latency_ms": 100}
    )
    
    # Mock Report Generator
    mock_report_llm.return_value = "# Final Report\nAI is advancing."
    
    agent = ResearchAgent()
    state = agent.run("Find latest AI news")
    
    assert state.status == "completed"
    assert state.completed_steps == 1
    assert "AI is advancing." in state.final_report
    assert len(state.failures) == 0

@patch("app.planner.call_llm_json")
@patch("app.executor.call_llm_json")
@patch("app.tools.calculator.CalculatorTool.run")
def test_retry_exhaustion_graceful_failure(mock_calc_run, mock_exec_llm, mock_plan_llm):
    # Mock Planner
    mock_plan_llm.return_value = {
        "goal": "Calculate something impossible",
        "steps": [
            {"step": 1, "description": "Do math", "tool": "calculator"}
        ]
    }
    
    # Mock Executor arg generation
    mock_exec_llm.return_value = {"expression": "invalid_syntax"}
    
    # Always fail
    mock_calc_run.return_value = ToolResult(
        success=False,
        tool_name="calculator",
        error={"type": "SyntaxError", "message": "Bad math"},
        metadata={}
    )
    
    agent = ResearchAgent()
    state = agent.run("Calculate something impossible")
    
    assert state.status == "failed"
    assert state.completed_steps == 0
    # Should retry a few times (max_retries is 2, so 3 attempts total)
    assert len(state.failures) == 3

def test_report_generation():
    from app.state import AgentState, Plan, Step
    agent = ResearchAgent()
    agent.state = AgentState(user_goal="Test report")
    agent.state.status = "completed"
    agent.state.plan = Plan(goal="Test report", steps=[
        Step(step=1, description="Step 1", tool="calculator")
    ])
    agent.state.completed_steps = 1
    agent.state.final_report = "# Generated Report\nContent here."
    
    json_report = agent.get_json_report()
    import json
    parsed = json.loads(json_report)
    assert parsed["goal"] == "Test report"
    assert parsed["status"] == "completed"
    assert "Generated Report" in parsed["final_report"]
    assert parsed["metrics"]["steps_completed"] == 1
