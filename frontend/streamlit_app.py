import sys
import os
import streamlit as st
import json
import time

# Ensure the root directory is in the sys path to import the app
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agent import ResearchAgent
from dotenv import load_dotenv

load_dotenv()

# --- PAGE CONFIG ---
st.set_page_config(
    page_title="ResPilot Dashboard", 
    page_icon="🚀", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS ---
st.markdown("""
<style>
    .reportview-container .main .block-container{
        padding-top: 2rem;
    }
    .hero-title {
        font-size: 3rem;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B2B, #FF416C);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0rem;
        padding-bottom: 0rem;
    }
    .hero-subtitle {
        font-size: 1.2rem;
        color: #888;
        margin-top: 0rem;
        padding-top: 0rem;
    }
    .stat-box {
        background-color: #1E1E1E;
        padding: 1rem;
        border-radius: 8px;
        border: 1px solid #333;
    }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR ---
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/artificial-intelligence.png", width=64)
    st.markdown("## ResPilot")
    st.caption("v1.0.0 | Autonomous Agent Engine")
    
    st.divider()
    
    st.subheader("⚙️ Configuration")
    provider = os.getenv("LLM_PROVIDER", "Not Configured").upper()
    model = os.getenv("MODEL_NAME", "Default")
    
    st.metric("LLM Provider", provider)
    st.metric("Model Engine", model)
    
    st.divider()
    
    st.subheader("🛠️ Available Tools")
    st.markdown("""
    - 🔍 **Web Search** (DuckDuckGo)
    - 📚 **Wikipedia** (Wiki Search & Fetch)
    - 📄 **Page Fetcher** (BS4)
    - 🧮 **Calculator** (Safe AST)
    - 🧨 **Failure Simulator**
    """)
    
    # API checks
    if provider == "GROQ" and not os.getenv("GROQ_API_KEY"):
        st.error("Missing GROQ_API_KEY in .env")
    elif provider == "OPENAI" and not os.getenv("OPENAI_API_KEY"):
        st.error("Missing OPENAI_API_KEY in .env")
    else:
        st.success("✅ API Configured")

# --- MAIN UI ---
st.markdown('<p class="hero-title">ResPilot</p>', unsafe_allow_html=True)
st.markdown('<p class="hero-subtitle">Your Autonomous Competitive Intelligence Agent</p>', unsafe_allow_html=True)
st.markdown("---")

# Input Section
st.subheader("🎯 What would you like to research?")

# Predefined goals in a more modern layout
st.write("**Quick Start Ideas:**")
col1, col2, col3 = st.columns(3)
if col1.button("📉 Analyze NVIDIA's Position", use_container_width=True):
    st.session_state.goal_input = "Analyze NVIDIA's competitive position in the AI accelerator market."
if col2.button("🤖 OpenAI vs DeepMind", use_container_width=True):
    st.session_state.goal_input = "Compare OpenAI and Google DeepMind based on their latest AI developments."
if col3.button("📰 Latest AI News", use_container_width=True):
    st.session_state.goal_input = "Research the top 3 AI developments from the last week."

goal = st.text_area(
    "Research Goal:",
    value=st.session_state.get("goal_input", ""),
    placeholder="Type your complex, multi-step research request here...",
    height=120,
    label_visibility="collapsed"
)

# Action Buttons
action_col1, action_col2, _ = st.columns([2, 2, 4])
run_clicked = action_col1.button("🚀 Launch Agent", type="primary", use_container_width=True)
demo_clicked = action_col2.button("🧨 Demo Self-Healing", use_container_width=True, help="Injects a deliberate failure to show agent recovery.")

if run_clicked or demo_clicked:
    if not goal.strip():
        st.warning("⚠️ Please provide a research goal to begin.")
    else:
        st.divider()
        
        # Fancy Spinner
        with st.status("🤖 Agent is working on your task...", expanded=True) as status:
            st.write("1. 🧠 Analyzing goal and creating plan...")
            time.sleep(0.5) # purely for visual pacing
            st.write("2. 🔍 Executing deterministic tools and fetching live data...")
            st.write("3. 🛡️ Validating outputs and recovering if necessary...")
            st.write("4. 📝 Synthesizing findings into structured report...")
            
            try:
                agent = ResearchAgent(demo_failure=demo_clicked)
                state = agent.run(goal)
                
                if state.status == "completed":
                    status.update(label="✅ Task Completed Successfully!", state="complete", expanded=False)
                else:
                    status.update(label=f"❌ Task Halted: {state.status}", state="error", expanded=True)
                    
            except Exception as e:
                status.update(label="❌ Critical Error Encountered", state="error", expanded=True)
                st.exception(e)
                st.stop()

        # Display Results if completed
        if state.status == "completed":
            
            # Key Metrics row
            st.subheader("📊 Execution Dashboard")
            m1, m2, m3, m4 = st.columns(4)
            total_steps = len(state.plan.steps) if state.plan else 0
            tools_used = len(set(s.tool for s in state.plan.steps if s.tool != "synthesize")) if state.plan else 0
            recoveries = len(state.recoveries)
            sources = len(state.sources)
            
            m1.metric("Steps Executed", total_steps)
            m2.metric("Tools Utilized", tools_used)
            m3.metric("Failures Recovered", recoveries, delta=f"{recoveries} auto-fixed" if recoveries else None, delta_color="off")
            m4.metric("Sources Scanned", sources)
            
            st.markdown("---")
            
            # TABS for organized viewing
            tab1, tab2, tab3, tab4 = st.tabs(["📄 Final Report", "⚙️ Execution Trace", "🛠️ Agent Plan", "🗂️ Raw Data"])
            
            with tab1:
                st.markdown(state.final_report)
                
                if state.sources:
                    st.divider()
                    st.subheader("📚 References")
                    for idx, src in enumerate(state.sources):
                        url = src.get("url", "#")
                        title = src.get("title", url)
                        st.markdown(f"- [{title}]({url})")
            
            with tab2:
                st.markdown("### Step-by-Step Trace")
                if state.plan:
                    for step in state.plan.steps:
                        if step.tool == "synthesize": continue
                        
                        icon = "🟢" if step.status == "success" else "🔴"
                        with st.expander(f"{icon} Step {step.step}: {step.tool.replace('_', ' ').title()}", expanded=False):
                            st.write(f"**Intent:** {step.description}")
                            
                            # Show failures
                            step_failures = [f for f in state.failures if f.get("step") == step.step]
                            if step_failures:
                                for f in step_failures:
                                    st.error(f"**Tool Error ({f.get('tool')}):** {f.get('error')}")
                                    st.warning("Self-healing triggered. Retrying...")
                            
                            if step.result and step.result.metadata:
                                st.caption(f"⏱️ Latency: {step.result.metadata.get('latency_ms', 'N/A')}ms | 🔄 Attempts: {step.retries + 1}")
                else:
                    st.info("No trace available.")
                    
            with tab3:
                st.markdown("### Strategic Plan")
                if state.plan:
                    st.json([{"step": s.step, "action": s.description, "tool": s.tool} for s in state.plan.steps])
                else:
                    st.info("No plan generated.")
                    
            with tab4:
                st.markdown("### Raw Execution JSON")
                st.json(agent.get_json_report())
                
            st.divider()
            
            # Export Section
            st.subheader("💾 Export Results")
            d1, d2 = st.columns(2)
            d1.download_button("⬇️ Download Report (.md)", data=state.final_report, file_name="report.md", mime="text/markdown", use_container_width=True)
            d2.download_button("⬇️ Download Trace (.json)", data=agent.get_json_report(), file_name="trace.json", mime="application/json", use_container_width=True)
