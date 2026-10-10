# ResPilot Write-up

## Design Decisions
- **Plan-and-Execute Architecture**: I chose a "Plan-and-Execute" architecture over a reactive ReAct loop. Planning first provides a transparent trace for the user and prevents the agent from entering chaotic, unpredictable loops. It breaks down the problem distinctly, satisfying the problem decomposition requirement effectively.
- **Deterministic Tools**: Instead of giving the LLM unrestricted Python `eval()`, I built safe, deterministic tools (like an AST-based calculator and a focused webpage fetcher). The LLM's only job is to provide JSON arguments to these tools.
- **Explicit Validation and Recovery**: Rather than relying on the LLM to implicitly realize it failed, I implemented an explicit Output Validator. If a tool fails or the output schema is invalid, the execution engine intercepts it and enters a bounded retry loop, feeding the exact error back to the LLM. This prevents infinite loops and ensures robustness.
- **Custom Orchestration**: I built a custom, lightweight state machine (`agent.py` and `executor.py`) instead of using heavy frameworks like LangGraph. This ensures no unnecessary bloat, precise control over the retry/recovery mechanisms, and extreme transparency for the evaluation criteria.

## Limitations
- **Sequential Execution**: The current planner creates a linear sequence of steps. It does not support parallel tool execution (e.g., searching two different topics simultaneously), which limits execution speed on complex tasks.
- **Fixed Plan Blindness**: Because the plan is generated upfront, if the agent discovers halfway through that the goal requires a fundamentally different approach, it cannot dynamically rewrite the overarching plan. It can only retry the current failing step.
- **Context Window Exhaustion**: As intermediate findings grow (e.g., fetching multiple large webpages), they are appended to the state. This could eventually exceed the LLM's context limit since there is no intermediate summarization mechanism.

## Future Improvements
- **Dynamic Replanning**: Allow the agent to emit a "Replan" signal during the validation phase if it detects the current path is a dead end, enabling it to discard the rest of the plan and start fresh.
- **Parallel Execution**: Implement an async DAG execution engine for steps that do not depend on the output of previous steps.
- **Memory & Summarization**: Introduce a lightweight local vector store or intermediate summarization steps for retrieved context to prevent context window bloat and reduce latency on redundant queries.
- **Sandboxed Code Execution**: Add a real code-interpreter sandbox (e.g., using a secure Docker container) for tasks that require complex data analysis beyond simple arithmetic.
