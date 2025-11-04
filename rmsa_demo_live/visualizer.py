"""Rich-powered live dashboard for comparing RMSA agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List

from rich import box
from rich.console import Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table


@dataclass
class AgentSnapshot:
    name: str
    step: int
    shaped_reward: float
    metrics: Dict[str, float]
    last_action: str = ""


@dataclass
class DemoSnapshot:
    episode: int
    request_id: int
    default_agent: AgentSnapshot
    optimized_agent: AgentSnapshot
    connection_label: str


def _metrics_table(snapshot: AgentSnapshot) -> Table:
    table = Table(title=snapshot.name, box=box.SIMPLE_HEAVY)
    table.add_column("Metric", justify="left")
    table.add_column("Value", justify="right")
    for key, value in snapshot.metrics.items():
        if key == "steps":
            continue
        table.add_row(key.replace("_", " ").title(), f"{value:.3f}")
    table.add_row("Steps", str(snapshot.metrics.get("steps", snapshot.step)))
    table.add_row("Reward", f"{snapshot.shaped_reward:.3f}")
    if snapshot.last_action:
        table.add_row("Last Action", snapshot.last_action)
    return table


def _header(snapshot: DemoSnapshot) -> Panel:
    header = Table.grid(expand=True)
    header.add_column(justify="left")
    header.add_column(justify="right")
    header.add_row(
        f"Episode {snapshot.episode} | Request #{snapshot.request_id}",
        snapshot.connection_label,
    )
    return Panel(header, title="RMSA Live Comparison", subtitle="Default vs Optimized")


def _body(snapshot: DemoSnapshot) -> Group:
    default_table = _metrics_table(snapshot.default_agent)
    optimized_table = _metrics_table(snapshot.optimized_agent)
    return Group(default_table, optimized_table)


def render_layout(snapshot: DemoSnapshot) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(_header(snapshot), name="header", size=3),
        Layout(_body(snapshot), name="body"),
    )
    return layout


class LiveVisualizer:
    def __init__(self, refresh_hz: float = 15.0) -> None:
        self.refresh_hz = refresh_hz

    def run(self, stream: Iterable[DemoSnapshot]) -> None:
        with Live(refresh_per_second=self.refresh_hz, screen=True) as live:
            for snapshot in stream:
                live.update(render_layout(snapshot))

    def warmup_message(self, text: str) -> None:
        progress = Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"))
        task_id = progress.add_task(text, start=False)
        progress.start_task(task_id)
        with progress:
            pass
