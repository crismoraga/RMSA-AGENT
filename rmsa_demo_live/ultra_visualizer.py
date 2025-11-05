"""Immersive Rich + Plotly visualizer for the 6-agent RMSA Battle Royale."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from rich import box
from rich.console import Console, Group
from rich.layout import Layout
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.text import Text


AGENT_COLOR_MAP = {
    "CONTROL": "blue",
    "OPTIMIZED": "green",
    "DEEP-QOT": "cyan",
    "ADAPTIVE": "magenta",
    "SPECTRAL-MASTER": "bright_yellow",
    "META-LEARNER": "bright_white",
}


@dataclass
class AgentSnapshot:
    """Snapshot of a single agent's state at a given timestep."""

    name: str
    step: int
    shaped_reward: float
    metrics: Dict[str, float]
    last_action: str = ""
    color: Optional[str] = None

    def resolve_color(self) -> str:
        base = self.color or AGENT_COLOR_MAP.get(self.name.upper(), "white")
        return base


@dataclass
class BattleSnapshot:
    """Aggregated view of the entire Battle Royale at a timestep."""

    episode: int
    request_id: int
    topology: str
    connection_label: str
    agents: List[AgentSnapshot]
    highlight_agent: Optional[str] = None
    scoreboard: Optional[Dict[str, float]] = None
    significance: Optional[str] = None


def _get_color_for_value(value: float, metric_type: str) -> str:
    """Return color code based on qualitative assessment of ``value``."""

    if metric_type in {"blocking", "fragmentation", "decision_latency_ms"}:
        if value < 0.05:
            return "green"
        if value < 0.15:
            return "yellow"
        return "red"

    if metric_type in {"spectral_efficiency", "acceptance", "qot"}:
        if value > 0.85:
            return "green"
        if value > 0.65:
            return "yellow"
        return "red"

    if metric_type == "cumulative_reward":
        if value > 0:
            return "green"
        if value > -10:
            return "yellow"
        return "red"

    return "cyan"


def _format_metric(key: str, value: float) -> str:
    color = _get_color_for_value(value, key)
    if key in {"blocking", "acceptance"}:
        return f"[{color}]{value*100:.1f}%[/{color}]"
    if key == "decision_latency_ms":
        return f"[{color}]{value:.1f} ms[/{color}]"
    return f"[{color}]{value:.3f}[/{color}]"


def _metric_table(snapshot: AgentSnapshot) -> Panel:
    table = Table(
        title=f"[{snapshot.resolve_color()}]{snapshot.name}[/{snapshot.resolve_color()}]",
        box=box.ROUNDED,
        show_header=False,
        border_style=snapshot.resolve_color(),
    )
    metric_order = [
        "blocking",
        "acceptance",
        "spectral_efficiency",
        "qot",
        "fragmentation",
        "load_balance",
        "cumulative_reward",
        "decision_latency_ms",
    ]
    for metric in metric_order:
        if metric in snapshot.metrics:
            table.add_row(
                metric.replace("_", " ").title(),
                _format_metric(metric, snapshot.metrics[metric]),
            )

    table.add_row("Steps", f"{snapshot.metrics.get('steps', snapshot.step):,}")
    reward_color = "green" if snapshot.shaped_reward >= 0 else "red"
    table.add_row("Reward", f"[{reward_color}]{snapshot.shaped_reward:.2f}[/{reward_color}]")
    if snapshot.last_action:
        table.add_row("Last Action", snapshot.last_action)
    return Panel(table, border_style=snapshot.resolve_color())


def _scoreboard_panel(snapshot: BattleSnapshot) -> Panel:
    table = Table(box=box.SIMPLE_HEAVY)
    table.add_column("Rank", justify="center", style="bold white")
    table.add_column("Agente", style="bold")
    table.add_column("Blocking", justify="right")
    table.add_column("Reward", justify="right")

    # Rank agents by blocking probability (lower better)
    sorted_agents = sorted(
        snapshot.agents,
        key=lambda agent: agent.metrics.get("blocking", 1.0),
    )
    for idx, agent in enumerate(sorted_agents, 1):
        blocking = agent.metrics.get("blocking", 1.0)
        reward = agent.metrics.get("cumulative_reward", agent.shaped_reward)
        table.add_row(
            f"#{idx}",
            f"[{agent.resolve_color()}]{agent.name}[/{agent.resolve_color()}]",
            _format_metric("blocking", blocking),
            _format_metric("cumulative_reward", reward),
        )

    footer = Text()
    footer.append("Highlight: ", style="bold yellow")
    highlight = snapshot.highlight_agent or sorted_agents[0].name
    footer.append(highlight, style=AGENT_COLOR_MAP.get(highlight.upper(), "white"))
    if snapshot.significance:
        footer.append(f"  |  {snapshot.significance}", style="bold green")

    return Panel(Group(table, footer), title="Battle Ranking", border_style="yellow")


def _create_banner(snapshot: BattleSnapshot) -> Panel:
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="center")
    grid.add_column(justify="right")
    grid.add_row(
        f"[bold cyan]Episode {snapshot.episode}[/bold cyan]",
        f"[bold magenta]{snapshot.topology}[/bold magenta]",
        f"[bold yellow]Request #{snapshot.request_id}[/bold yellow]",
    )
    grid.add_row("", snapshot.connection_label, "")
    return Panel(grid, title="🌐 RMSA Battle Royale", border_style="blue")


def _create_grid(snapshot: BattleSnapshot) -> Layout:
    layout = Layout()
    layout.split_column(
        Layout(name="row1"),
        Layout(name="row2"),
        Layout(name="row3"),
    )

    panels = [_metric_table(agent) for agent in snapshot.agents]
    # Ensure exactly 6 panels (pad if necessary)
    while len(panels) < 6:
        panels.append(Panel("Pending data", border_style="dim"))

    layout["row1"].split_row(Layout(panels[0]), Layout(panels[1]))
    layout["row2"].split_row(Layout(panels[2]), Layout(panels[3]))
    layout["row3"].split_row(Layout(panels[4]), Layout(panels[5]))
    return layout


def render_battle_layout(snapshot: BattleSnapshot) -> Layout:
    overall = Layout()
    overall.split_column(
        Layout(_create_banner(snapshot), name="header", size=5),
        Layout(name="body"),
        Layout(_scoreboard_panel(snapshot), name="scoreboard", size=8),
    )
    overall["body"].split_row(
        Layout(_create_grid(snapshot), name="agents"),
        Layout(Panel("Plotly dashboard en ventana externa", border_style="dim"), size=40),
    )
    return overall


class UltraVisualizer:
    """High-impact terminal visualizer for the six-agent Battle Royale."""

    def __init__(self, refresh_hz: float = 8.0) -> None:
        self.refresh_hz = refresh_hz
        self.console = Console()
        self._live = None

    def __enter__(self):
        """Context manager entry."""
        self._live = Live(
            refresh_per_second=self.refresh_hz,
            screen=True,
            console=self.console,
        )
        self._live.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if self._live:
            self._live.__exit__(exc_type, exc_val, exc_tb)
        return False

    def update(self, snapshot: BattleSnapshot) -> None:
        """Update the live display with a new snapshot."""
        if self._live:
            self._live.update(render_battle_layout(snapshot))

    def show_banner(self) -> None:
        banner = """
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║        🚀 RMSA ULTRA-VANGUARDISTA - AGENTES EN TIEMPO REAL 🚀       ║
║                                                                      ║
║      6 agentes luchando por dominar el enrutamiento óptico WDM       ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝
        """
        self.console.print(banner, style="bold bright_white", justify="center")

    def run(self, stream: Iterable[BattleSnapshot]) -> None:
        self.show_banner()
        with Live(
            refresh_per_second=self.refresh_hz,
            screen=True,
            console=self.console,
        ) as live:
            for snapshot in stream:
                live.update(render_battle_layout(snapshot))

    def warmup_message(self, message: str) -> None:
        progress = Progress(SpinnerColumn(), TextColumn("{task.description}"))
        with progress:
            progress.add_task(message, total=None)
            import time

            time.sleep(2.0)


# Backwards compatibility alias
LiveVisualizer = UltraVisualizer
