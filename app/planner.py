import json
from typing import List
from app.state import Plan, Step
from app.utils.llm import call_llm_json

class Planner:
    def __init__(self, available_tools: List[str]):
        self.available_tools = available_tools

    def create_plan(self, goal: str) -> Plan:
        system_prompt = (
            "You are an expert planning agent for a research system.\n"
            "Given a user goal, break it down into a logical sequence of steps.\n"
            f"Available tools: {self.available_tools}\n"
            "Do NOT include internal reasoning in the output. Just output the JSON plan.\n"
            "The JSON must have this schema:\n"
            "{\n"
            "  \"goal\": \"<normalized goal>\",\n"
            "  \"steps\": [\n"
            "    {\"step\": 1, \"description\": \"<what to do>\", \"tool\": \"<tool_name>\"},\n"
            "    ... \n"
            "  ]\n"
            "}\n"
            "Include a final step with tool='synthesize' to combine the findings, although 'synthesize' is an internal capability."
        )

        response_dict = call_llm_json(prompt=goal, system_prompt=system_prompt)
        
        steps = []
        for s in response_dict.get("steps", []):
            steps.append(Step(
                step=s.get("step"),
                description=s.get("description"),
                tool=s.get("tool")
            ))
            
        return Plan(
            goal=response_dict.get("goal", goal),
            steps=steps
        )
