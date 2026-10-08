import json
import time
from typing import Dict, Any
from app.state import AgentState, Step, ToolResult
from app.tools.base import BaseTool
from app.validators.output_validator import validate_tool_output
from app.utils.logging_utils import log_event
from app.utils.llm import call_llm_json

class Executor:
    def __init__(self, tools: Dict[str, BaseTool], max_retries: int = 2):
        self.tools = tools
        self.max_retries = max_retries

    def _generate_tool_args(self, step: Step, state: AgentState) -> Dict[str, Any]:
        """Use LLM to dynamically generate tool arguments based on context."""
        context = {
            "user_goal": state.user_goal,
            "step_description": step.description,
            "tool_name": step.tool,
            "previous_findings": [str(f)[:500] for f in state.findings] # Limit context size
        }
        
        system_prompt = (
            "You are an intelligent agent configuring a tool call.\n"
            "Given the context, output ONLY a JSON object representing the kwargs for the tool.\n"
            "For 'web_search', provide {'query': '...'}.\n"
            "For 'webpage_fetcher', provide {'url': '...'}.\n"
            "For 'calculator', provide {'expression': '...'}.\n"
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
                
                # Validate output
                is_valid, error_msg = validate_tool_output(step.tool, result)
                
                if is_valid:
                    log_event("TOOL_SUCCESS", f"Step {step.step}", step.tool, "SUCCESS", latency=result.metadata.get("latency_ms", 0), attempt=attempt)
                    step.status = "success"
                    
                    # Store finding and source
                    state.findings.append({"step": step.step, "tool": step.tool, "data": result.data})
                    
                    if step.tool == "web_search":
                        for item in result.data:
                            state.sources.append({"url": item.get("url"), "title": item.get("title")})
                    elif step.tool == "webpage_fetcher":
                        state.sources.append({"url": result.data.get("url"), "title": result.data.get("title")})
                        
                    return True
                else:
                    raise ValueError(error_msg)

            except Exception as e:
                error_str = str(e)
                log_event("TOOL_FAILURE", f"Step {step.step}", step.tool, "FAILED", error=error_str, attempt=attempt)
                state.record_failure(step.step, step.tool, error_str)
                
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
