# ResearchPilot — Autonomous Competitive Intelligence Agent

ResearchPilot is an autonomous AI agent capable of planning and executing multi-step research goals using live internet data. It breaks down complex user goals, fetches real-time data, performs calculations, recovers from unexpected tool failures, and synthesizes findings into structured reports.

## Features
- **Visible Planning Trace**: The agent builds and displays a JSON-structured plan before executing any step.
- **Deterministic Tools**: Executes `web_search`, `webpage_fetcher`, and `calculator` safely (e.g. using AST for math, no arbitrary `eval()`).
- **Live Data**: Gathers live information without relying on static datasets.
- **Self-Healing Execution**: Detects malformed tool outputs and automatically recovers using an exponential backoff retry mechanism.
- **Structured Reporting**: Produces comprehensive Markdown reports and JSON execution traces.

## Architecture
The system uses a **Plan-and-Execute** pattern.
An LLM plans the execution steps. An execution engine dynamically feeds intermediate states back to the LLM to construct arguments for deterministic Python tools. Outputs are validated via strict Python logic. 

See [docs/architecture.md](docs/architecture.md) for the detailed flow.

## Installation

**Prerequisites:** Python 3.10+

```bash
git clone <repository_url>
cd researchpilot

# Create a virtual environment
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Unix:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Configuration
Copy `.env.example` to `.env` and configure your API keys.

```bash
cp .env.example .env
```
Edit `.env` to provide your API credentials:
```env
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxx
# MODEL_NAME=gpt-4o-mini
```

## Running the Application

To run the agent in the CLI:
```bash
python main.py --goal "Analyze NVIDIA's competitive position in the AI accelerator market and give me a concise competitive landscape report."
```

### Running the Demo Failure Mode
This mode injects the `failure_simulator` tool which intentionally fails on the first execution to demonstrate the agent's failure recovery mechanisms.
```bash
python main.py --goal "Analyze NVIDIA's competitive position" --demo-failure
```

### Generating JSON or Markdown Output
```bash
python main.py --goal "Compare OpenAI and Google DeepMind" --output report.json
```

## Web Interface

ResearchPilot includes a simple, polished Streamlit frontend for demonstration and easy interaction. The UI allows you to run the agent, view the live execution trace, observe failure recovery, and download the final reports.

1. Install dependencies (`pip install -r requirements.txt`).
2. Configure `.env` with your LLM API keys.
3. Run the Streamlit application:
```bash
streamlit run frontend/streamlit_app.py
```
4. Open the displayed local URL in your browser.
5. Enter a research goal (or use one of the predefined suggestions).
6. Click **Run Agent**.
7. Use **Demo Failure Recovery** to demonstrate the resilience feature right in your browser.

## Running Tests
Tests use Pytest and validate LLM outputs, schemas, and the critical failure-recovery loop using mocks (no network required).
```bash
pytest tests/ -v
```

## Example Transcripts
See the `examples/` directory for sample runs.

## Project Structure
- `app/` - Core application logic (`agent.py`, `planner.py`, `executor.py`)
- `app/tools/` - Deterministic tools (`web_search.py`, `calculator.py`, etc.)
- `tests/` - Pytest suites including end-to-end recovery tests
- `docs/` - Architecture and design writeup
- `main.py` - CLI entry point
