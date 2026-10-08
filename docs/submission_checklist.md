# Submission Checklist

| Assignment Requirement | Implementation | Evidence | Status |
|---|---|---|---|
| Natural language goal | CLI accepts goal via `--goal` or prompt | `main.py` | PASS |
| Visible planning trace | `Planner` maps goal to `Plan`, logged to console | `app/agent.py` | PASS |
| Two distinct tools | Built 4 tools: web_search, webpage_fetcher, calculator, failure_simulator | `app/tools/` | PASS |
| Step-by-step execution | `Executor` processes plan sequentially | `app/executor.py` | PASS |
| Deliberate failure | `FailureSimulatorTool` triggers malformed response | `app/tools/failure_simulator.py`, `--demo-failure` flag | PASS |
| Recovery | `Executor` validates tool output, retries with backoff | `app/executor.py` | PASS |
| Structured output | Markdown output + JSON output via `--output` | `app/agent.py` | PASS |
| README | Complete GitHub-quality README | `README.md` | PASS |
| Architecture diagram | Mermaid diagram | `docs/architecture.md` | PASS |
| 2–3 transcripts | 3 complete logs | `examples/` | PASS |
| One-page write-up | Concise architecture write-up | `docs/design_writeup.md` | PASS |

### Rubric Mapping
- **Planning (20%)**: Visible explicit JSON planning block before any action happens. Handled by `app/planner.py`.
- **Tool Orchestration (20%)**: LLM dynamically fills arguments contextually for tools. Done in `app/executor.py`. 
- **Robustness (20%)**: Pydantic typing, schema validation on tool outputs, deliberate backoff-retry loop for failures.
- **Code Quality (15%)**: Clean modular structure (`app/tools`, `app/validators`), robust typing, Pytest test suite covering core edge cases.
- **Documentation (15%)**: Clear README with specific commands, architecture diagram, design constraints and limitations noted.
- **Creativity (10%)**: Structured, colorized CLI logs; detailed execution metrics output; custom AST-based secure `calculator` (no eval); configurable mock failure injector.
