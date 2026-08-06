# Agentic System Debugger for Production (ASDP)

## The Real Problem and Who It Affects
Developers of agentic AI systems face significant challenges when debugging their applications in production, especially when issues are read-only and cannot be easily reproduced in development or staging environments. This often leads to "black box" scenarios where the internal state, reasoning, and tool interactions of an agent are opaque, making root cause analysis difficult and time-consuming. This directly impacts resolution times, system reliability, and the ability to maintain critical agentic applications.

This tool is for anyone building and operating agentic AI systems, from individual developers to SRE teams, who need better visibility into their agents' runtime behavior to diagnose and resolve production incidents efficiently.

## Why This Project Shape/Stack Was Chosen
This prototype is a simple Python CLI tool designed for clarity, ease of use, and quick integration into existing observability pipelines. Python is a common language in the AI/ML community, making it accessible. The CLI nature allows for flexible integration: it can be run manually, piped output from agent logs, or integrated into CI/CD or incident response workflows.

The core idea is to provide a structured way to ingest agent trace data (e.g., agent thoughts, observations, tool calls, LLM inputs/outputs) and then enable querying and basic analysis of this data. We prioritize a provider-agnostic approach by defining a clear data schema for agent traces and working with fixture data by default.

## Setup and Usage Instructions (Zero API Keys)

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd agentic-system-debugger
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    ```

3.  **Run with fixture data:**
    The tool comes with pre-defined `trace_fixtures.json` to demonstrate its functionality without any API keys or live agent systems.

    To list all available traces:
    ```bash
    python asdp.py list
    ```

    To view a specific trace (e.g., `trace_001`):
    ```bash
    python asdp.py view trace_001
    ```

    To query traces for specific events (e.g., tool calls):
    ```bash
    python asdp.py query --type TOOL_CALL
    ```

    To query for specific content within steps (e.g., steps containing "error"):
    ```bash
    python asdp.py query --content error
    ```

    To query for steps by agent role (e.g., steps where "Planner" was the agent):
    ```bash
    python asdp.py query --agent Planner
    ```

    You can combine queries, e.g., finding tool calls made by "Planner":
    ```bash
    python asdp.py query --type TOOL_CALL --agent Planner
    ```

## Optional Real-LLM Adapter
This prototype explicitly does *not* include a real-LLM adapter. The problem addressed is *debugging* agentic systems, which involves analyzing their behavior *after* LLM interactions have occurred, not performing new LLM calls. The focus is on ingesting and querying existing trace data, making LLM API keys irrelevant to the core functionality.
