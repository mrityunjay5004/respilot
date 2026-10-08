# Sample Run 2: Failure Recovery (Demo Mode)

**Command:**
`python main.py --goal "Analyze NVIDIA's competitive position" --demo-failure`

**Transcript:**
```
Starting ResearchPilot with goal: 'Analyze NVIDIA's competitive position'
WARNING: Demo failure mode enabled. The agent will intentionally fail a tool call and recover.
2026-10-08 17:20:00 | INFO | AGENT_START | STARTED
2026-10-08 17:20:01 | INFO | PLAN_CREATED | IN_PROGRESS

==================================================
AGENT PLAN
==================================================
Goal: Analyze NVIDIA's competitive position

Plan:
1. Simulate a failure to verify recovery mechanism. (Tool: failure_simulator)
2. Gather initial competitor information. (Tool: web_search)
3. Synthesize findings. (Tool: synthesize)
==================================================

[STEP 1/3] Simulate a failure to verify recovery mechanism.
2026-10-08 17:20:03 | INFO | TOOL_START | Step 1 | failure_simulator | attempt:1
2026-10-08 17:20:04 | ERROR | TOOL_FAILURE | Step 1 | failure_simulator | FAILED | error: Malformed response detected from tool. | attempt:1
2026-10-08 17:20:05 | INFO | RECOVERY_START | Step 1 | failure_simulator | attempt:2
2026-10-08 17:20:06 | INFO | TOOL_START | Step 1 | failure_simulator | attempt:2
2026-10-08 17:20:07 | INFO | TOOL_SUCCESS | Step 1 | failure_simulator | SUCCESS | 1005ms | attempt:2

[STEP 2/3] Gather initial competitor information.
2026-10-08 17:20:07 | INFO | TOOL_START | Step 2 | web_search | attempt:1
2026-10-08 17:20:10 | INFO | TOOL_SUCCESS | Step 2 | web_search | SUCCESS | 2800ms | attempt:1

[STEP 3/3] Synthesize findings.

2026-10-08 17:20:10 | INFO | SYNTHESIS_START | IN_PROGRESS
2026-10-08 17:20:18 | INFO | AGENT_COMPLETED | SUCCESS

==================================================
FINAL REPORT
==================================================
# Report

## Executive Summary
NVIDIA holds a dominant market share in AI hardware. The simulated failure step successfully executed on the second attempt, proving that the agent can recover from malformed data automatically.

## Execution Summary
- Steps planned: 3
- Steps completed: 3
- Tools used: 2
- Failures encountered: 1
- Recoveries: 1
- Sources consulted: 2
==================================================
```
