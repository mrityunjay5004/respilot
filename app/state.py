from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import datetime

class ToolResult(BaseModel):
    success: bool
    tool_name: str
    data: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class Step(BaseModel):
    step: int
    description: str
    tool: str
    status: str = "pending"  # pending, success, failed
    result: Optional[ToolResult] = None
    retries: int = 0

class Plan(BaseModel):
    goal: str
    steps: List[Step]

class AgentState(BaseModel):
    user_goal: str
    normalized_goal: str = ""
    plan: Optional[Plan] = None
    current_step: int = 1
    completed_steps: int = 0
    failures: List[Dict[str, Any]] = Field(default_factory=list)
    recoveries: List[Dict[str, Any]] = Field(default_factory=list)
    findings: List[Any] = Field(default_factory=list)
    sources: List[Dict[str, str]] = Field(default_factory=list)
    final_report: str = ""
    status: str = "initialized" # initialized, planning, executing, synthesizing, completed, failed
    start_time: datetime.datetime = Field(default_factory=datetime.datetime.now)
    end_time: Optional[datetime.datetime] = None

    def record_failure(self, step_id: int, tool_name: str, error: str):
        self.failures.append({
            "step": step_id,
            "tool": tool_name,
            "error": error,
            "timestamp": datetime.datetime.now().isoformat()
        })

    def record_recovery(self, step_id: int, tool_name: str):
        self.recoveries.append({
            "step": step_id,
            "tool": tool_name,
            "timestamp": datetime.datetime.now().isoformat()
        })
