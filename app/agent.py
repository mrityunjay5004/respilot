import datetime
import json
from colorama import Fore, Style
from app.state import AgentState
from app.planner import Planner
from app.executor import Executor
from app.reporting.report_generator import ReportGenerator
from app.tools import WebSearchTool, WebpageFetcherTool, CalculatorTool, FailureSimulatorTool, WikipediaTool
from app.utils.logging_utils import log_event

class ResearchAgent:
    def __init__(self, demo_failure: bool = False):
        self.state = None
        
        # Initialize tools
        self.tools = {
            "web_search": WebSearchTool(),
            "webpage_fetcher": WebpageFetcherTool(),
            "calculator": CalculatorTool(),
            "wikipedia": WikipediaTool(),
        }
        
        if demo_failure:
            self.tools["failure_simulator"] = FailureSimulatorTool(mode="malformed_response")
            
        self.planner = Planner(available_tools=list(self.tools.keys()) + ["synthesize"])
        self.executor = Executor(tools=self.tools, max_retries=2)
        self.report_generator = ReportGenerator()

    def run(self, user_goal: str) -> AgentState:
        self.state = AgentState(user_goal=user_goal)
        self.state.status = "planning"
        log_event("AGENT_START", status="STARTED")
        
        # 1. Planning
        log_event("PLAN_CREATED", status="IN_PROGRESS")
        self.state.plan = self.planner.create_plan(user_goal)
        
        print("\n" + "="*50)
        print("AGENT PLAN")
        print("="*50)
        print(f"Goal: {self.state.plan.goal}\n")
        print("Plan:")
        for step in self.state.plan.steps:
            print(f"{step.step}. {step.description} (Tool: {step.tool})")
        print("="*50 + "\n")
        
        self.state.status = "executing"
        
        # 2. Execution Loop
        for step in self.state.plan.steps:
            self.state.current_step = step.step
            print(f"\n[STEP {step.step}/{len(self.state.plan.steps)}] {step.description}")
            
            success = self.executor.execute_step(step, self.state)
            
            if success:
                self.state.completed_steps += 1
            else:
                log_event("AGENT_HALTED", f"Step {step.step}", status="FAILED")
                self.state.status = "failed"
                break
                
        # 3. Synthesis
        if self.state.status != "failed":
            self.state.status = "synthesizing"
            log_event("SYNTHESIS_START", status="IN_PROGRESS")
            self.state.final_report = self.report_generator.generate(self.state)
            
            self.state.final_report += "\n\n## Execution Summary\n"
            self.state.final_report += f"- Steps planned: {len(self.state.plan.steps)}\n"
            self.state.final_report += f"- Steps completed: {self.state.completed_steps}\n"
            self.state.final_report += f"- Tools used: {len(set(s.tool for s in self.state.plan.steps if s.tool != 'synthesize'))}\n"
            self.state.final_report += f"- Failures encountered: {len(self.state.failures)}\n"
            self.state.final_report += f"- Recoveries: {len(self.state.recoveries)}\n"
            self.state.final_report += f"- Sources consulted: {len(self.state.sources)}\n"
            
            self.state.status = "completed"
            log_event("AGENT_COMPLETED", status="SUCCESS")

        self.state.end_time = datetime.datetime.now()
        return self.state

    def get_json_report(self) -> str:
        if not self.state:
            return "{}"
            
        data = {
            "goal": self.state.user_goal,
            "status": self.state.status,
            "plan": [s.model_dump() for s in self.state.plan.steps] if self.state.plan else [],
            "steps": [s.model_dump() for s in self.state.plan.steps] if self.state.plan else [],
            "failures": self.state.failures,
            "recoveries": self.state.recoveries,
            "findings": self.state.findings,
            "sources": self.state.sources,
            "final_report": self.state.final_report,
            "metrics": {
                "steps_completed": self.state.completed_steps,
                "tools_used": len(set(s.tool for s in self.state.plan.steps if s.tool != 'synthesize')) if self.state.plan else 0,
                "failures": len(self.state.failures),
                "recoveries": len(self.state.recoveries)
            }
        }
        return json.dumps(data, indent=2)
