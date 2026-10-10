import json
import time
from typing import Dict, Any
from app.state import AgentState, Step, ToolResult
from app.tools.base import BaseTool
from app.validators.output_validator import validate_tool_output
from app.utils.logging_utils import log_event
from app.utils.llm import call_llm_json, call_llm

class Executor:
    def __init__(self, tools: Dict[str, BaseTool], max_retries: int = 2):
        self.tools = tools
        self.max_retries = max_retries

    def _generate_tool_args(self, step: Step, state: AgentState) -> Dict[str, Any]:
        """Use LLM to dynamically generate tool arguments based on context."""
        step_failures = [f["error"] for f in state.failures if f.get("step") == step.step]
        context = {
            "user_goal": state.user_goal,
            "step_description": step.description,
            "tool_name": step.tool,
            "previous_findings": [str(f)[:500] for f in state.findings], # Limit context size
            "previous_errors": step_failures
        }
        
        system_prompt = (
            "You are an intelligent agent configuring a tool call.\n"
            "If previous_errors indicate irrelevant results or no results, you MUST write a completely different, highly specific search query (e.g., adding 'financial valuation' or 'news').\n"
            "Given the context, output ONLY a JSON object representing the kwargs for the tool.\n"
            "For 'web_search', provide {'query': '...'}.\n"
            "For 'webpage_fetcher', provide {'url': '...'}.\n"
            "For 'calculator', provide {'expression': '...'}.\n"
            "For 'wikipedia', provide {'query': '...'}.\n"
            "For 'failure_simulator', provide {'mode': 'malformed_response'}.\n"
        )
        
        return call_llm_json(prompt=json.dumps(context), system_prompt=system_prompt)

    def execute_step(self, step: Step, state: AgentState) -> bool:
        if step.tool == 'synthesize':
            step.status = "success"
            return True

        if step.tool not in self.tools:
            log_event("TOOL_ERROR", f"Step {step.step}", step.tool, "FAILED", error="Tool not found.")
            step.status = "failed"
            state.record_failure(step.step, step.tool, "Tool not found.")
            return False

        tool = self.tools[step.tool]
        
        while step.retries <= self.max_retries:
            attempt = step.retries + 1
            log_event("TOOL_START", f"Step {step.step}", step.tool, attempt=attempt)
            
            try:
                # Generate arguments
                kwargs = self._generate_tool_args(step, state)
                
                # Execute tool
                result = tool.run(**kwargs)
                step.result = result
                
                # Validate output schema
                is_valid, error_msg = validate_tool_output(step.tool, result)
                
                # Semantic relevance check for search tools
                if is_valid and step.tool in ["web_search", "wikipedia"] and result.data:
                    relevance_prompt = f"Goal: {state.user_goal}\nStep: {step.description}\nSearch Results: {str(result.data)[:1500]}\nAre these search results at least partially relevant to the entities or topics in the goal? (Reject if it's completely irrelevant, e.g., retail clothing when searching for tech companies). Answer EXACTLY 'YES' or 'NO'."
                    relevance_check = call_llm(relevance_prompt, system_prompt="You are a lenient relevance evaluator. Answer ONLY 'YES' or 'NO'.").strip().upper()
                    if "NO" in relevance_check:
                        is_valid = False
                        error_msg = "Irrelevant search results. The retrieved information does not match the intended entities or goal."

                if not is_valid:
                    # Switch to wikipedia if web_search is consistently failing
                    if step.tool == "web_search" and attempt >= 2 and "wikipedia" in self.tools:
                        log_event("TOOL_SWITCH", f"Step {step.step}", "Switching from web_search to wikipedia for alternative data source")
                        step.tool = "wikipedia"
                        tool = self.tools["wikipedia"]
                    raise ValueError(error_msg)
                
                log_event("TOOL_SUCCESS", f"Step {step.step}", step.tool, "SUCCESS", latency=result.metadata.get("latency_ms", 0), attempt=attempt)
                step.status = "success"
                
                # Store finding and source
                # Truncate to prevent token limit exhaustion
                truncated_data = str(result.data)[:1000] if result.data else None
                state.findings.append({"step": step.step, "tool": step.tool, "data": truncated_data})
                
                if step.tool == "web_search" or step.tool == "wikipedia":
                    for item in result.data:
                        state.sources.append({"url": item.get("url"), "title": item.get("title")})
                elif step.tool == "webpage_fetcher":
                    state.sources.append({"url": result.data.get("url"), "title": result.data.get("title")})
                    
                return True

            except Exception as e:
                error_str = str(e)
                log_event("TOOL_FAILURE", f"Step {step.step}", step.tool, "FAILED", error=error_str, attempt=attempt)
                state.record_failure(step.step, step.tool, error_str)
                
                # Check for permanent errors that should not be retried
                permanent_errors = ["division by zero", "Tool not found"]
                if any(pe in error_str for pe in permanent_errors):
                    log_event("RECOVERY_FAILED", f"Step {step.step}", step.tool, "PERMANENT_ERROR_HALTED")
                    step.status = "failed"
                    return False

                step.retries += 1
                if step.retries <= self.max_retries:
                    log_event("RECOVERY_START", f"Step {step.step}", step.tool, attempt=attempt+1)
                    time.sleep(1) # Simple backoff
                    state.record_recovery(step.step, step.tool)
                else:
                    log_event("RECOVERY_FAILED", f"Step {step.step}", step.tool, "FAILED")
                    step.status = "failed"
                    return False
        
        return False
