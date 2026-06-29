"""AgentLens command-line interface."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from agentlens_ai.evals.runner import run_static_eval_file
from agentlens_ai.reporting.html import DEFAULT_REPORT_PATH, generate_html_report
from agentlens_ai.reporting.summary import summarize_events
from agentlens_ai.storage.sqlite_store import SQLiteTraceStore

app = typer.Typer(help="AgentLens AI: observability and regression testing for AI agents")
console = Console()


@app.command()
def init() -> None:
    """Initialize AgentLens in the current project."""

    Path(".agentlens").mkdir(exist_ok=True)
    config_path = Path(".agentlens/config.yml")
    if not config_path.exists():
        config_path.write_text("project: agentlens-demo\nstore: sqlite\n", encoding="utf-8")
    SQLiteTraceStore()
    console.print("[green]Initialized AgentLens in .agentlens/[/green]")


@app.command("list-runs")
def list_runs() -> None:
    """List traced agent runs."""

    store = SQLiteTraceStore()
    runs = store.list_runs()

    table = Table(title="AgentLens Runs")
    table.add_column("Run ID", style="cyan")

    for run_id in runs:
        table.add_row(run_id)

    if not runs:
        console.print("No runs found. Run an instrumented agent first.")
        return

    console.print(table)


@app.command()
def show(run_id: str) -> None:
    """Show the ordered event timeline for one run."""

    store = SQLiteTraceStore()
    events = store.fetch_events(run_id=run_id)

    if not events:
        console.print(f"No events found for run id: {run_id}")
        raise typer.Exit(code=1)

    table = Table(title=f"AgentLens Timeline: {run_id}")
    table.add_column("Time")
    table.add_column("Event")
    table.add_column("Name")
    table.add_column("Duration")
    table.add_column("Status")

    for event in events:
        duration = "-" if event.get("duration_ms") is None else f"{event['duration_ms']:.2f} ms"
        status = "error" if event.get("error") else "ok"
        table.add_row(
            str(event.get("timestamp", "")),
            str(event.get("event_type", "")),
            str(event.get("name", "")),
            duration,
            status,
        )

    console.print(table)


@app.command()
def report(
    html: bool = typer.Option(False, "--html", help="Generate a local HTML report."),
    output: Path = typer.Option(DEFAULT_REPORT_PATH, "--output", "-o", help="HTML report path."),
) -> None:
    """Show a basic local trace report."""

    store = SQLiteTraceStore()
    events = store.fetch_events()
    summary = summarize_events(events)

    console.print("[bold]AgentLens Report[/bold]")
    console.print(f"Total runs: {summary['runs']}")
    console.print(f"Total events: {summary['events']}")
    console.print(f"Errors: {summary['errors']}")
    console.print(f"Tool calls: {summary['tool_calls']}")
    console.print(f"Agent runs: {summary['agent_runs']}")
    console.print(f"Avg recorded duration: {summary['avg_duration_ms']} ms")

    if html:
        report_path = generate_html_report(events, output)
        console.print(f"[green]HTML report written to {report_path}[/green]")


@app.command()
def eval(path: Path) -> None:  # noqa: A001 - CLI command name is intentionally eval
    """Run a YAML regression eval file."""

    results = run_static_eval_file(path)
    failed = [result for result in results if not result.passed]

    table = Table(title="AgentLens Eval Results")
    table.add_column("Name")
    table.add_column("Status")
    table.add_column("Reason")

    for result in results:
        status = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        table.add_row(result.name, status, result.reason)

    console.print(table)

    if failed:
        raise typer.Exit(code=1)
