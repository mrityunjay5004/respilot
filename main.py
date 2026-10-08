import argparse
import sys
import os
from app.agent import ResearchAgent

def main():
    parser = argparse.ArgumentParser(description="ResearchPilot - Autonomous Competitive Intelligence Agent")
    parser.add_argument("--goal", type=str, help="The research goal for the agent.")
    parser.add_argument("--demo-failure", action="store_true", help="Deliberately induce a failure to demonstrate recovery.")
    parser.add_argument("--output", type=str, help="Output file path (e.g. report.md or report.json)")
    
    args = parser.parse_args()
    
    goal = args.goal
    if not goal:
        goal = input("Enter your research goal: ")
        
    if not goal.strip():
        print("Error: Goal cannot be empty.")
        sys.exit(1)
        
    print(f"Starting ResearchPilot with goal: '{goal}'")
    if args.demo_failure:
        print("WARNING: Demo failure mode enabled. The agent will intentionally fail a tool call and recover.")
        
    agent = ResearchAgent(demo_failure=args.demo_failure)
    
    try:
        state = agent.run(goal)
        
        if state.status == "completed":
            print("\n" + "="*50)
            print("FINAL REPORT")
            print("="*50)
            print(state.final_report)
            print("="*50 + "\n")
            
            if args.output:
                if args.output.endswith(".json"):
                    with open(args.output, "w") as f:
                        f.write(agent.get_json_report())
                else:
                    with open(args.output, "w") as f:
                        f.write(state.final_report)
                print(f"Output saved to {args.output}")
        else:
            print(f"\nAgent execution halted with status: {state.status}")
            
    except Exception as e:
        print(f"\nCritical Error during execution: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
