# Design Write-Up: ResearchPilot

### Design Decisions
ResearchPilot implements a modular, state-driven agent architecture. Instead of relying on a monolithic ReAct loop, it uses an explicit **Plan-and-Execute** workflow. This fulfills the requirement for a visible planning trace and guarantees predictable execution. The LLM acts as the orchestrator (planning, tool argument generation, synthesis), while Python handles the deterministic control flow (retries, validation, error handling).

The architecture separates concerns:
- **Planner:** Maps goals to a structured JSON plan.
- **Executor:** Manages the tool loop, invoking LLM just for argument generation.
- **Validators:** Python-level assertions against tool output to catch schema mismatches.
- **Tools:** Deterministic functions (no arbitrary LLM code execution).

### Agentic Behavior
The agent begins by creating a `Plan` consisting of multiple `Steps`. It then executes these steps sequentially. For each step, it feeds the previous findings into the LLM to contextually generate the tool arguments. This allows later steps (like a calculator operation) to depend on the output of earlier steps (like web search).

### Tool Strategy
Tools are designed to be deterministic and safe. For example, `CalculatorTool` uses Python's `ast` module to evaluate mathematical expressions rather than using the dangerous `eval()` function or relying on the LLM's inherently flawed math capabilities. The `WebSearchTool` uses `duckduckgo-search` to fetch live data without API friction, addressing the "no dataset" constraint. 

### Reliability
Robustness is achieved via a dedicated Failure Detection and Recovery loop:
- **Validation:** Tool outputs are checked against expected schemas.
- **Bounded Retries:** If a tool fails (e.g., timeout, malformed data), the executor catches the exception, logs it, and retries up to a configured `MAX_RETRIES` (default 2) with an exponential/linear backoff.
- **Controlled Injection:** The `FailureSimulatorTool` proves this by deliberately emitting malformed JSON on its first invocation, triggering a recovery cycle.

### Limitations
- **Sequential Execution:** The agent executes steps one by one. Independent steps (like researching multiple competitors) cannot run in parallel.
- **Context Window Exhaustion:** The executor passes `previous_findings` into the LLM context. While truncated, heavy webpage payloads could still overflow the context window on long tasks.
- **Rigid Planning:** The agent cannot easily add new steps mid-execution if it discovers it needs more information, as the plan is fixed upfront.

### What I Would Improve With More Time
1. **Dynamic Replanning:** Allow the agent to inject new steps into its plan if a tool reveals that more information is needed.
2. **Parallel Tool Execution:** Use `asyncio` to run independent searches concurrently.
3. **Advanced RAG for Web Fetching:** Instead of truncating webpages, chunk them and use a lightweight vector search or embedding step to extract the most relevant paragraphs.
4. **Persistent Memory:** Add a vector database (e.g., ChromaDB) across sessions so the agent remembers facts from previous research runs.
5. **Human-in-the-Loop:** Pause before executing high-risk tools and ask the user for approval via a CLI prompt.
