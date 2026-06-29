"""HTML report generation for AgentLens AI."""

from __future__ import annotations

from html import escape
from pathlib import Path
from typing import Any

from agentlens_ai.reporting.summary import summarize_events

DEFAULT_REPORT_PATH = Path(".agentlens/reports/latest.html")


def _format_duration(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{float(value):.2f} ms"
    except (TypeError, ValueError):
        return "-"


def _render_event_rows(events: list[dict[str, Any]]) -> str:
    if not events:
        return '<tr><td colspan="6">No events found.</td></tr>'

    rows: list[str] = []
    for event in events:
        error = event.get("error") or ""
        status = "error" if error else "ok"
        rows.append(
            "<tr>"
            f"<td>{escape(str(event.get('run_id', '')))}</td>"
            f"<td>{escape(str(event.get('timestamp', '')))}</td>"
            f"<td>{escape(str(event.get('event_type', '')))}</td>"
            f"<td>{escape(str(event.get('name', '')))}</td>"
            f"<td>{escape(_format_duration(event.get('duration_ms')))}</td>"
            f"<td class=\"{status}\">{escape(error or 'ok')}</td>"
            "</tr>"
        )
    return "\n".join(rows)


def generate_html_report(
    events: list[dict[str, Any]],
    output_path: Path | str = DEFAULT_REPORT_PATH,
) -> Path:
    """Generate a local HTML report and return the output path."""

    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    summary = summarize_events(events)
    rows = _render_event_rows(events)

    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>AgentLens Report</title>
  <style>
    body {{
      margin: 0;
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      background: #0f172a;
      color: #e2e8f0;
    }}
    header {{
      padding: 32px;
      background: linear-gradient(135deg, #111827, #1e293b);
      border-bottom: 1px solid #334155;
    }}
    h1 {{ margin: 0 0 8px 0; font-size: 32px; }}
    p {{ color: #94a3b8; }}
    main {{ padding: 32px; }}
    .cards {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 16px;
      margin-bottom: 32px;
    }}
    .card {{
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      padding: 18px;
    }}
    .metric {{ font-size: 28px; font-weight: 700; color: #f8fafc; }}
    .label {{ color: #94a3b8; font-size: 13px; margin-top: 4px; }}
    table {{
      width: 100%;
      border-collapse: collapse;
      background: #111827;
      border: 1px solid #334155;
      border-radius: 14px;
      overflow: hidden;
    }}
    th, td {{
      padding: 12px 14px;
      border-bottom: 1px solid #1f2937;
      text-align: left;
      vertical-align: top;
      font-size: 14px;
    }}
    th {{ background: #1e293b; color: #cbd5e1; }}
    tr:last-child td {{ border-bottom: none; }}
    .ok {{ color: #86efac; }}
    .error {{ color: #fca5a5; }}
    .section-title {{ margin: 0 0 16px 0; font-size: 22px; }}
  </style>
</head>
<body>
  <header>
    <h1>AgentLens Report</h1>
    <p>Local trace summary for AI agent runs.</p>
  </header>
  <main>
    <section class="cards">
      <div class="card"><div class="metric">{summary['runs']}</div><div class="label">Runs</div></div>
      <div class="card"><div class="metric">{summary['events']}</div><div class="label">Events</div></div>
      <div class="card"><div class="metric">{summary['errors']}</div><div class="label">Errors</div></div>
      <div class="card"><div class="metric">{summary['tool_calls']}</div><div class="label">Tool calls</div></div>
      <div class="card"><div class="metric">{summary['avg_duration_ms']}</div><div class="label">Avg duration ms</div></div>
    </section>

    <section>
      <h2 class="section-title">Event timeline</h2>
      <table>
        <thead>
          <tr>
            <th>Run ID</th>
            <th>Timestamp</th>
            <th>Event</th>
            <th>Name</th>
            <th>Duration</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </section>
  </main>
</body>
</html>
"""

    path.write_text(html, encoding="utf-8")
    return path
