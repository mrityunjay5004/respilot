import sys
import os
import streamlit as st
import json

# Ensure the root directory is in the sys path to import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import ResearchAgent
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="ResearchPilot", page_icon="🤖", layout="wide")

st.title("ResearchPilot")
st.subheader("Autonomous Competitive Intelligence Agent")
st.markdown("Give ResearchPilot a high-level research goal. The agent will plan the task, use tools, validate results, recover from failures, and generate a structured report.")

# --- SIDEBAR ---
with st.sidebar:
    st.header("Agent Configuration")
    
    provider = os.getenv("LLM_PROVIDER", "Not Configured")
    model = os.getenv("MODEL_NAME", "Not Configured")
    
    st.text(f"LLM Provider: {provider}")
    st.text(f"Model: {model}")
    st.text("Max Retries: 2")
    
    st.markdown("**Available Tools:**")
    st.markdown("- Web Search")
    st.markdown("- Webpage Fetcher")
    st.markdown("- Calculator")
    st.markdown("- Failure Simulator (Demo Mode)")
    
    # Simple check for API key
    if provider.lower() == "groq" and not os.getenv("GROQ_API_KEY"):
        st.error("GROQ API key is not configured. Add it to .env before running the agent.")
    elif provider.lower() == "openai" and not os.getenv("OPENAI_API_KEY"):
        st.error("OPENAI API key is not configured. Add it to .env before running the agent.")

# --- MAIN INPUT SECTION ---
st.markdown("### Research Goal")

# Predefined goals
col1, col2, col3 = st.columns(3)
if col1.button("Analyze NVIDIA's competitive position"):
    st.session_state.goal_input = "Analyze NVIDIA's competitive position in the AI accelerator market."
if col2.button("Compare OpenAI and Google DeepMind"):
    st.session_state.goal_input = "Compare OpenAI and Google DeepMind based on their latest AI developments."
if col3.button("Top AI developments of the week"):
    st.session_state.goal_input = "Research the top 3 AI developments from the last week."

goal = st.text_area(
    "Enter your research goal:",
    value=st.session_state.get("goal_input", ""),
    placeholder="e.g., Analyze NVIDIA's competitive position in the AI accelerator market.",
    height=100,
    label_visibility="collapsed"
)

col_run, col_demo = st.columns([1, 1])
run_clicked = col_run.button("Run Agent", type="primary", use_container_width=True)
demo_clicked = col_demo.button("Demo Failure Recovery", use_container_width=True)

if run_clicked or demo_clicked:
    if not goal.strip():
        st.warning("Please enter a research goal first.")
    else:
        st.markdown("---")
        st.markdown("### Agent Status")
        
        status_text = st.empty()
        status_text.info("Initializing Agent...")
        
        try:
            agent = ResearchAgent(demo_failure=demo_clicked)
            
            # We run the agent. Since it's a synchronous blocking call right now, 
            # we just show a spinner. For a real streaming UI we would use callbacks, 
            # but the assignment asks for a thin presentation layer over the existing backend.
            with st.spinner("Agent is running... (Planning → Executing → Validating → Synthesizing)"):
                state = agent.run(goal)
            
            if state.status == "completed":
                status_text.success("● Planning → ● Executing → ● Validating → ● Synthesizing → ● Completed")
            else:
                status_text.error(f"Agent execution halted with status: {state.status}")

            st.markdown("---")
            
            # --- 1. AGENT PLAN ---
            with st.expander("1. Agent Plan", expanded=True):
                if state.plan:
                    for s in state.plan.steps:
                        st.markdown(f"**{s.step}.** {s.description} *(Tool: {s.tool})*")
                else:
                    st.write("No plan generated.")

            # --- 2. EXECUTION TRACE ---
            with st.expander("2. Execution Trace", expanded=True):
                if state.plan:
                    for step in state.plan.steps:
                        if step.tool == "synthesize":
                            continue # skip internal capability
                            
                        # Determine icon based on final status
                        icon = "✓" if step.status == "success" else "❌"
                        
                        st.markdown(f"**{icon} STEP {step.step}** — `{step.tool}` — {step.status.upper()}")
                        
                        # Show failures and recoveries for this step if any
                        step_failures = [f for f in state.failures if f.get("step") == step.step]
                        step_recoveries = [r for r in state.recoveries if r.get("step") == step.step]
                        
                        if step_failures:
                            for f in step_failures:
                                st.error(f"**FAILURE DETECTED**\n\n**Tool:** {f.get('tool')}\n\n**Error:** {f.get('error')}")
                        if step_recoveries:
                            st.warning(f"**RECOVERY**\n\nRetrying with validated input... Recovery successful.")
                        
                        # Show latency
                        if step.result and step.result.metadata:
                            latency = step.result.metadata.get("latency_ms", "N/A")
                            st.caption(f"Latency: {latency}ms | Attempts: {step.retries + 1}")
                        st.markdown("---")
                else:
                    st.write("No execution trace available.")

            # --- TOOLS USED ---
            with st.expander("Tools Activity", expanded=False):
                if state.plan:
                    tool_counts = {}
                    for step in state.plan.steps:
                        if step.tool == "synthesize": continue
                        if step.tool not in tool_counts:
                            tool_counts[step.tool] = {"calls": 0, "success": 0}
                        
                        tool_counts[step.tool]["calls"] += (1 + step.retries)
                        if step.status == "success":
                            tool_counts[step.tool]["success"] += 1
                            
                    for t, stats in tool_counts.items():
                        st.markdown(f"**{t}** | {stats['calls']} calls | {stats['success']} successful steps")

            # --- 3. FINAL REPORT ---
            st.markdown("### 3. Final Report")
            st.markdown(state.final_report)
            
            # --- SOURCES ---
            with st.expander("Sources", expanded=False):
                if state.sources:
                    for idx, src in enumerate(state.sources):
                        url = src.get("url", "#")
                        title = src.get("title", url)
                        if not title: title = url
                        st.markdown(f"{idx+1}. [{title}]({url})")
                else:
                    st.write("No external sources were recorded.")
                    
            # --- DOWNLOADS ---
            st.markdown("---")
            col_md, col_json, _ = st.columns([1, 1, 2])
            
            col_md.download_button(
                label="Download Markdown Report",
                data=state.final_report,
                file_name="researchpilot_report.md",
                mime="text/markdown"
            )
            
            col_json.download_button(
                label="Download JSON Result",
                data=agent.get_json_report(),
                file_name="researchpilot_result.json",
                mime="application/json"
            )

        except Exception as e:
            status_text.error("Agent could not complete the request.")
            with st.expander("Technical details"):
                st.exception(e)
