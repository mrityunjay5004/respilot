import json
from app.state import AgentState
from app.utils.llm import call_llm

class ReportGenerator:
    def generate(self, state: AgentState) -> str:
        prompt = (
            f"User Goal: {state.user_goal}\n"
            f"Plan Steps: {[s.description for s in state.plan.steps if state.plan]}\n"
            f"Findings: {json.dumps(state.findings, indent=2)}\n"
            f"Sources: {json.dumps(state.sources, indent=2)}\n\n"
            "Based on the findings, generate a comprehensive, structured Markdown report answering the user's goal.\n"
            "Include sections:\n"
            "- Executive Summary\n"
            "- Key Findings\n"
            "- Quantitative Comparison (if applicable)\n"
            "- Sources (list the URLs)\n"
            "Format nicely."
        )
        
        system_prompt = "You are an expert analyst writing a final report based on gathered evidence. Be concise, objective, and clear. Do not make up facts not present in the findings."
        
        return call_llm(prompt=prompt, system_prompt=system_prompt)
