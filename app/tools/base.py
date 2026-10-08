from abc import ABC, abstractmethod
from typing import Any
import time
from app.state import ToolResult

class BaseTool(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, **kwargs) -> ToolResult:
        pass
    
    def _create_success_result(self, data: Any, start_time: float) -> ToolResult:
        return ToolResult(
            success=True,
            tool_name=self.name,
            data=data,
            metadata={"latency_ms": int((time.time() - start_time) * 1000)}
        )

    def _create_error_result(self, error_type: str, message: str, start_time: float) -> ToolResult:
        return ToolResult(
            success=False,
            tool_name=self.name,
            error={"type": error_type, "message": message},
            metadata={"latency_ms": int((time.time() - start_time) * 1000)}
        )
