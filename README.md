# 🚀 ResPilot

> **An autonomous, self-healing competitive intelligence agent that plans and executes complex multi-step research goals using live web data.**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

ResPilot is not just another wrapper around an LLM. It is an **autonomous agent** capable of breaking down complex user goals, safely executing deterministic tools (like web search and mathematical calculations), recovering from unexpected failures, and synthesizing its findings into highly structured, comprehensive reports.

---

## ✨ Key Features

- 🧠 **Visible Planning Trace**: The agent builds and displays a structured JSON plan *before* executing any steps, so you know exactly what it's going to do.
- 🛡️ **Deterministic & Safe Tools**: Executes `web_search`, `webpage_fetcher`, and `calculator` safely (e.g., using Python AST for math, ensuring no arbitrary `eval()` exploits).
- 🌍 **Live Internet Data**: Gathers up-to-date information dynamically, escaping the constraints of static LLM training data.
- ⚕️ **Self-Healing Execution**: Intelligently detects malformed tool outputs and automatically recovers using an exponential backoff retry mechanism.
- 📊 **Structured Reporting**: Produces comprehensive Markdown reports and JSON execution traces.
- 🖥️ **Streamlit Web UI**: Comes with a polished, out-of-the-box web interface for an excellent user experience.

---

## 🏗️ Architecture: Plan-and-Execute

ResPilot leverages a robust **Plan-and-Execute** pattern:
1. **Planning**: An LLM orchestrates the workflow by determining the sequential steps required to achieve the user's goal.
2. **Execution**: An execution engine dynamically feeds intermediate states back to the LLM to construct precise arguments for deterministic Python tools.
3. **Validation**: Outputs are validated via strict Python logic, guaranteeing reliability before proceeding to the next step.

> 📖 *For a deep dive into the system's architecture, check out [docs/architecture.md](docs/architecture.md).*

---

## 🚀 Getting Started

### Prerequisites
- **Python:** 3.10 or higher
- **API Key:** An active LLM API key (e.g., OpenAI)

### 1️⃣ Installation

Clone the repository and install the required dependencies:

```bash
git clone <repository_url>
cd respilot

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
.\venv\Scripts\activate
# On Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2️⃣ Configuration

ResPilot uses environment variables for configuration. Set up your `.env` file:

```bash
cp .env.example .env
```

Edit the `.env` file to include your API credentials:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxx...
# Optional: Change the model name
# MODEL_NAME=gpt-4o-mini
```

---

## 💻 Usage

ResPilot can be run either via a Command Line Interface (CLI) or a Web Interface.

### 🖥️ Option A: Command Line Interface (CLI)

Run the agent directly from your terminal:

```bash
python main.py --goal "Analyze NVIDIA's competitive position in the AI accelerator market and give me a concise competitive landscape report."
```

#### Saving the Output
You can save the final report as Markdown or JSON:
```bash
python main.py --goal "Compare OpenAI and Google DeepMind" --output report.json
```

#### Demo Failure Recovery
Want to see the self-healing feature in action? This mode injects a `failure_simulator` tool that intentionally fails on the first attempt to demonstrate the agent's robust recovery mechanism:
```bash
python main.py --goal "Analyze NVIDIA's competitive position" --demo-failure
```

### 🌐 Option B: Streamlit Web Interface

ResPilot includes a beautiful Streamlit frontend for easy interaction, live execution tracing, and report downloading.

```bash
streamlit run frontend/streamlit_app.py
```
*Open the provided local URL (usually `http://localhost:8501`) in your browser to interact with the agent.*

---

## 🧪 Running Tests

ResPilot is fully tested. The test suite uses `pytest` and validates LLM outputs, schemas, and the critical failure-recovery loop using mocks (no network required).

```bash
pytest tests/ -v
```

---

## 📂 Project Structure

```text
respilot/
├── app/                  # Core application logic (agent, planner, executor)
│   ├── tools/            # Deterministic tools (web search, calculator)
│   └── validators/       # Output validation logic
├── docs/                 # Architecture and design documentation
├── examples/             # Example execution transcripts (Sample runs)
├── frontend/             # Streamlit web interface application
├── tests/                # Pytest suites (End-to-End & Recovery tests)
├── main.py               # CLI entry point
└── requirements.txt      # Python dependencies
```

---

## 📈 Example Run

Curious what a ResPilot execution looks like? 

**Goal:** *Compare OpenAI and Google DeepMind based on their latest publicly available AI developments, and calculate the percentage difference between 175B and 1.76T parameters.*

```text
[STEP 1/4] Search for recent OpenAI models.
INFO | TOOL_SUCCESS | Step 1 | web_search | SUCCESS

[STEP 2/4] Search for recent Google DeepMind models.
INFO | TOOL_SUCCESS | Step 2 | web_search | SUCCESS

[STEP 3/4] Calculate the percentage difference...
INFO | TOOL_SUCCESS | Step 3 | calculator | SUCCESS

[STEP 4/4] Synthesize findings into a final report.
INFO | SYNTHESIS_START | IN_PROGRESS
INFO | AGENT_COMPLETED | SUCCESS
```
> *Check the `examples/` directory for full transcripts of this and other runs!*
