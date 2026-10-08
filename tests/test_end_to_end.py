import pytest
from unittest.mock import patch, MagicMock
from app.state import AgentState, Step, ToolResult, Plan
from app.tools import CalculatorTool, FailureSimulatorTool, WebSearchTool
from app.validators.output_validator import validate_tool_output
from app.agent import ResearchAgent

def test_calculator_tool():
    tool = CalculatorTool()
    res = tool.run(expression="10 + 5 * 2")
    assert res.success
    assert res.data["result"] == 20

    res2 = tool.run(expression="invalid format")
    assert not res2.success
    assert res2.error["type"] == "SyntaxError"

def test_failure_simulator_tool():
    tool = FailureSimulatorTool(mode="malformed_response")
    # First attempt should return malformed data
    res1 = tool.run()
    assert res1.success
    is_valid, _ = validate_tool_output("failure_simulator", res1)
    assert not is_valid
    
    # Second attempt should succeed properly
    res2 = tool.run()
    assert res2.success
    is_valid, _ = validate_tool_output("failure_simulator", res2)
    assert is_valid

def test_web_search_validation():
    # Valid output
    res = ToolResult(success=True, tool_name="web_search", data=[{"title": "t", "url": "u", "snippet": "s"}])
    is_valid, _ = validate_tool_output("web_search", res)
    assert is_valid

    # Missing field
    res_bad = ToolResult(success=True, tool_name="web_search", data=[{"title": "t", "url": "u"}])
    is_valid, _ = validate_tool_output("web_search", res_bad)
    assert not is_valid

@patch("app.planner.call_llm_json")
def test_planner(mock_call_llm_json):
    mock_call_llm_json.return_value = {
        "goal": "Test goal",
        "steps": [
            {"step": 1, "description": "Do X", "tool": "web_search"}
        ]
    }
    from app.planner import Planner
    planner = Planner(available_tools=["web_search"])
    plan = planner.create_plan("Test goal")
    assert len(plan.steps) == 1
    assert plan.steps[0].tool == "web_search"

@patch("app.executor.call_llm_json")
@patch("app.tools.web_search.WebSearchTool.run")
def test_executor_retry_and_recovery(mock_web_search, mock_llm_json):
    from app.executor import Executor
    
    mock_llm_json.return_value = {"query": "test"}
    
    # Simulate a failure on the first run, success on the second
    mock_web_search.side_effect = [
        ToolResult(success=False, tool_name="web_search", error={"type": "Test", "message": "fail"}, metadata={}),
        ToolResult(success=True, tool_name="web_search", data=[{"title": "t", "url": "u", "snippet": "s"}], metadata={})
    ]
    
    tools = {"web_search": WebSearchTool()}
    executor = Executor(tools=tools, max_retries=2)
    
    state = AgentState(user_goal="test")
    step = Step(step=1, description="test", tool="web_search")
    
    success = executor.execute_step(step, state)
    
    assert success
    assert step.retries == 1
    assert len(state.failures) == 1
    assert len(state.recoveries) == 1

@patch("app.executor.call_llm_json")
def test_agent_recovers_from_malformed_tool_response(mock_llm_json):
    """
    MANDATORY FAILURE TEST
    Tests that the agent detects a malformed response from failure_simulator, 
    retries, recovers, and completes the step.
    """
    mock_llm_json.return_value = {"mode": "malformed_response"}
    
    agent = ResearchAgent(demo_failure=True)
    # Mock planner and synthesizer to avoid LLM calls
    agent.planner.create_plan = MagicMock(return_value=Plan(
        goal="Test", 
        steps=[Step(step=1, description="Simulate failure", tool="failure_simulator")]
    ))
    agent.report_generator.generate = MagicMock(return_value="# Final Report")
    
    state = agent.run("Test recovery")
    
    assert state.status == "completed"
    assert len(state.failures) == 1
    assert len(state.recoveries) == 1
    assert state.completed_steps == 1
