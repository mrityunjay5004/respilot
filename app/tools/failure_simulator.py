import time
from .base import BaseTool
from app.state import ToolResult

class FailureSimulatorTool(BaseTool):
    name = "failure_simulator"
    description = "A testing tool that simulates a failure on the first execution, and succeeds on the second."

    def __init__(self, mode: str = "malformed_response"):
        self.mode = mode
        self.attempt_count = 0

    def run(self, **kwargs) -> ToolResult:
        start_time = time.time()
        self.attempt_count += 1
        
        # Simulate failure on first attempt
        if self.attempt_count == 1:
            if self.mode == "malformed_response":
                # Return success=True but completely malformed data structure to break validators
                return ToolResult(
                    success=True,
                    tool_name=self.name,
                    data={"malformed": "data", "missing_required_fields": True},
                    metadata={"latency_ms": int((time.time() - start_time) * 1000), "attempt": self.attempt_count}
                )
            elif self.mode == "timeout":
                time.sleep(1) # simulate delay
                return self._create_error_result("TimeoutError", "Simulated tool timeout.", start_time)
            elif self.mode == "network_error":
                return self._create_error_result("NetworkError", "Simulated connection reset by peer.", start_time)
            
        # Succeed on subsequent attempts
        data = {
            "status": "recovered",
            "message": "Failure simulated successfully and recovered on retry.",
            "original_kwargs": kwargs
        }
        
        return self._create_success_result(data, start_time)
