# ResPilot Architecture

```mermaid
graph TD
    User([User]) -->|Natural Language Goal| CLI[CLI / main.py]
    CLI --> Agent[ResearchAgent]
    Agent --> State[AgentState]
    Agent --> Planner[Planner]
    Planner -->|call_llm_json| LLM((LLM))
    Planner -->|Plan Generated| State
    Agent --> Executor[Executor]
    
    Executor -->|Fetch arguments via LLM| LLM
    Executor -->|Step 1..N| ToolSelection{Tool Selection}
    
    ToolSelection -->|web_search| WebSearch[WebSearchTool]
    ToolSelection -->|webpage_fetcher| WebFetcher[WebpageFetcherTool]
    ToolSelection -->|calculator| Calculator[CalculatorTool]
    ToolSelection -->|failure_simulator| Simulator[FailureSimulatorTool]
    
    WebSearch --> Validator[Output Validator]
    WebFetcher --> Validator
    Calculator --> Validator
    Simulator --> Validator
    
    Validator -->|Valid| StateUpdate[Update State & Findings]
    Validator -->|Invalid / Error| FailureDetect[Failure Detection]
    
    FailureDetect -->|Retry count <= max| RetryLog[Log & Wait]
    RetryLog --> ToolSelection
    
    FailureDetect -->|Retry exhausted| Halt[Halt & Fail]
    
    StateUpdate -->|All steps complete| Reporter[ReportGenerator]
    Reporter -->|call_llm| LLM
    Reporter --> FinalOutput([Markdown & JSON Report])
```

## Description
The diagram demonstrates the flow of control and data inside ResPilot. The agent explicitly plans its steps before executing them. Tools are invoked dynamically. When a tool fails or returns invalid data (e.g. simulated by the FailureSimulator), the Validator triggers the Failure Detection flow which loops back to Tool Execution with a retry counter.
