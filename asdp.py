import json
from enum import Enum
from pathlib import Path
from typing import List, Optional, Dict, Any

import typer
from pydantic import BaseModel, Field
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

app = typer.Typer(help="Agentic System Debugger for Production (ASDP)")
console = Console()

class StepType(str, Enum):
    LLM_INPUT = "LLM_INPUT"
    LLM_OUTPUT = "LLM_OUTPUT"
    TOOL_CALL = "TOOL_CALL"
    TOOL_OUTPUT = "TOOL_OUTPUT"
    AGENT_THOUGHT = "AGENT_THOUGHT"
    OBSERVATION = "OBSERVATION"
    ERROR = "ERROR"
    CUSTOM = "CUSTOM"

class TraceStep(BaseModel):
    timestamp: str
    agent_id: str = "UnknownAgent"
    step_type: StepType
    content: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)

class AgentTrace(BaseModel):
    trace_id: str
    steps: List[TraceStep]
    start_time: str
    end_time: Optional[str] = None
    status: str = "COMPLETED"

TRACE_FIXTURES_PATH = Path(__file__).parent / "trace_fixtures.json"

def load_traces() -> Dict[str, AgentTrace]:
    """Loads agent traces from the fixture file."""
    if not TRACE_FIXTURES_PATH.exists():
        console.log(f"Error: Fixture file not found at {TRACE_FIXTURES_PATH}", style="red")
        return {}
    try:
        with open(TRACE_FIXTURES_PATH, 'r') as f:
            data = json.load(f)
        return {t['trace_id']: AgentTrace(**t) for t in data}
    except json.JSONDecodeError as e:
        console.log(f"Error decoding JSON from {TRACE_FIXTURES_PATH}: {e}", style="red")
        return {}
    except Exception as e:
        console.log(f"An unexpected error occurred while loading traces: {e}", style="red")
        return {}

@app.command()
def list():
    """Lists all available agent traces."""
    traces = load_traces()
    if not traces:
        console.print("No traces found.", style="dim")
        return

    table = Table(title="Available Agent Traces", show_header=True, header_style="bold magenta")
    table.add_column("Trace ID", style="cyan", no_wrap=True)
    table.add_column("Start Time", style="green")
    table.add_column("End Time", style="green")
    table.add_column("Status", style="yellow")
    table.add_column("Steps", justify="right")

    for trace_id, trace in traces.items():
        table.add_row(trace.trace_id, trace.start_time, trace.end_time or "N/A", trace.status, str(len(trace.steps)))
    console.print(table)

@app.command()
def view(trace_id: str):
    """Views the detailed steps of a specific agent trace."""
    traces = load_traces()
    trace = traces.get(trace_id)
    if not trace:
        console.print(f"Error: Trace '{trace_id}' not found.", style="red")
        raise typer.Exit(code=1)

    console.print(Panel(f"[bold blue]Trace ID:[/bold blue] {trace.trace_id}\n"
                        f"[bold blue]Start Time:[/bold blue] {trace.start_time}\n"
                        f"[bold blue]End Time:[/bold blue] {trace.end_time or 'N/A'}\n"
                        f"[bold blue]Status:[/bold blue] {trace.status}",
                        title="[bold green]Trace Overview[/bold green]", expand=False))

    for i, step in enumerate(trace.steps):
        step_title = Text(f"Step {i + 1}", style="bold yellow")
        step_title.append(f" - {step.timestamp}", style="dim")
        step_title.append(f" - {step.step_type.value}", style="bold magenta")
        if step.step_type == StepType.ERROR:
            step_title.append(" [ERROR]", style="bold red reverse")

        console.print(Panel(f"[bold magenta]Agent:[/bold magenta] {step.agent_id}\n"
                            f"[bold cyan]Content:[/bold cyan]\n",
                            title=step_title, title_align="left", expand=False))
        syntax = Syntax(json.dumps(step.content, indent=2), "json", theme="monokai", line_numbers=True)
        console.print(syntax)
        if step.metadata:
            console.print(Panel(f"[bold blue]Metadata:[/bold blue]\n", title_align="left", expand=False))
            metadata_syntax = Syntax(json.dumps(step.metadata, indent=2), "json", theme="monokai", line_numbers=True)
            console.print(metadata_syntax)
        console.print("\n") # Add a newline for separation

@app.command()
def query(
    trace_id: Optional[str] = typer.Option(None, "--trace-id", "-t", help="Filter by a specific trace ID."),
    agent: Optional[str] = typer.Option(None, "--agent", "-a", help="Filter steps by agent ID."),
    step_type: Optional[StepType] = typer.Option(None, "--type", "-T", help="Filter steps by type (e.g., TOOL_CALL, ERROR)."),
    content: Optional[str] = typer.Option(None, "--content", "-c", help="Filter steps by content substring (case-insensitive)."),
):
    """
    Queries agent traces and steps based on various criteria.
    """
    traces = load_traces()
    if not traces:
        console.print("No traces loaded to query.", style="dim")
        return

    filtered_traces: Dict[str, AgentTrace] = {}
    if trace_id:
        if trace_id in traces:
            filtered_traces[trace_id] = traces[trace_id]
        else:
            console.print(f"No trace found with ID '{trace_id}'.", style="red")
            return
    else:
        filtered_traces = traces

    results_found = False
    for current_trace_id, trace in filtered_traces.items():
        matching_steps = []
        for i, step in enumerate(trace.steps):
            match = True
            if agent and agent.lower() not in step.agent_id.lower():
                match = False
            if step_type and step_type != step.step_type:
                match = False
            if content and content.lower() not in json.dumps(step.content).lower():
                match = False

            if match:
                matching_steps.append((i, step))

        if matching_steps:
            results_found = True
            console.print(Panel(f"[bold blue]Trace ID:[/bold blue] {current_trace_id}\n"
                                f"[bold blue]Start Time:[/bold blue] {trace.start_time}",
                                title="[bold green]Query Results[/bold green]", expand=False))
            for i, step in matching_steps:
                step_title = Text(f"Step {i + 1}", style="bold yellow")
                step_title.append(f" - {step.timestamp}", style="dim")
                step_title.append(f" - {step.step_type.value}", style="bold magenta")
                if step.step_type == StepType.ERROR:
                    step_title.append(" [ERROR]", style="bold red reverse")

                console.print(Panel(f"[bold magenta]Agent:[/bold magenta] {step.agent_id}\n"
                                    f"[bold cyan]Content:[/bold cyan]\n",
                                    title=step_title, title_align="left", expand=False))
                syntax = Syntax(json.dumps(step.content, indent=2), "json", theme="monokai", line_numbers=True)
                console.print(syntax)
                if step.metadata:
                    console.print(Panel(f"[bold blue]Metadata:[/bold blue]\n", title_align="left", expand=False))
                    metadata_syntax = Syntax(json.dumps(step.metadata, indent=2), "json", theme="monokai", line_numbers=True)
                    console.print(metadata_syntax)
                console.print("\n")

    if not results_found:
        console.print("No matching steps found for the given criteria.", style="dim")


if __name__ == "__main__":
    app()
