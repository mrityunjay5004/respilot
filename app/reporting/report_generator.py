import json
from app.state import AgentState
from app.utils.llm import call_llm

class ReportGenerator:
    def generate(self, state: AgentState) -> str:
        # Truncate findings to prevent token limits
        truncated_findings = []
        for finding in state.findings:
            if isinstance(finding, dict) and 'data' in finding and finding['data']:
                data_str = str(finding['data'])
                if len(data_str) > 1000:
                    finding = finding.copy()
                    finding['data'] = data_str[:1000] + "... [TRUNCATED]"
            truncated_findings.append(finding)

        prompt = (
            f"User Goal: {state.user_goal}\n"
            f"Plan Steps: {[s.description for s in state.plan.steps if state.plan]}\n"
            f"Findings: {json.dumps(truncated_findings, indent=2)}\n"
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
        
        try:
            return call_llm(prompt=prompt, system_prompt=system_prompt)
        except Exception as e:
            # Deterministic report generation fallback if LLM synthesis fails (e.g., token rate limit)
            fallback = "# Final Report\n\n## Executive Summary\n"
            fallback += "The agent successfully gathered findings, but the final LLM report generation failed due to an API error (likely rate limit or context size).\n\n"
            fallback += f"**Error Details:** {str(e)}\n\n"
            fallback += "## Key Findings (Raw Data)\n"
            for f in truncated_findings:
                fallback += f"- **{f.get('tool')} (Step {f.get('step')})**: {str(f.get('data'))[:300]}...\n"
            fallback += "\n## Sources\n"
            for s in state.sources:
                fallback += f"- {s.get('title')} ({s.get('url')})\n"
            return fallback
