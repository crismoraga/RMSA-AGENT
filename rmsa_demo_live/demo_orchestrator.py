"""🎬 Demo Orchestrator - RMSA Battle Royale Ultra-Vanguardista.

Orquesta la demo épica de 10 minutos comparando 6 agentes de RL optimizando RMSA.
"""
from __future__ import annotations

import argparse
import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich.text import Text
from stable_baselines3 import PPO

from config import BATTLE_AGENT_CONFIGS, BATTLE_TRAINING_CONFIGS, ENVIRONMENT, DEMO
from environment import EnvironmentFactory
from metrics import MetricsTracker
from metrics_engine import AgentHistory, BattleMetrics, EpisodeRecord, record_from_info
from reward_engineering import build_ultra_reward_function
from reward_functions import build_reward_function
from topology_manager import build_default_topology_manager, TopologyManager
from ultra_visualizer import AgentSnapshot, BattleSnapshot, UltraVisualizer

console = Console()


@dataclass
class AgentState:
    """Estado completo de un agente durante la demo."""
    name: str
    model: PPO
    env: any
    tracker: MetricsTracker
    history: AgentHistory
    total_reward: float = 0.0
    total_latency_ms: float = 0.0
    requests_processed: int = 0


class DemoOrchestrator:
    """Orquestador principal de la demo Battle Royale."""
    
    def __init__(
        self,
        agents_to_load: List[str],
        episodes: int = 200,
        topology: str = "NSFNET",
        seed: int = 31415,
    ):
        self.agents_to_load = agents_to_load
        self.episodes = episodes
        self.topology_name = topology
        self.seed = seed
        self.topology_manager = build_default_topology_manager()
        self.factory = EnvironmentFactory(base_kwargs={**ENVIRONMENT.as_dict(), "topology": topology})
        self.agents: Dict[str, AgentState] = {}
        self.current_episode = 0
        self.live_data_file = Path("live_battle_data.json")
        
    def _write_live_data(self) -> None:
        """Escribe datos en tiempo real al archivo JSON para el dashboard."""
        data = {
            'current_episode': self.current_episode,
            'total_episodes': self.episodes,
            'agents': {}
        }
        
        for name, agent_state in self.agents.items():
            history = agent_state.history
            
            # Extraer métricas desde los records (usar nombres correctos de EpisodeRecord)
            episodes = list(range(1, len(history.records) + 1))
            rewards = [r.cumulative_reward for r in history.records]
            blocking = [r.blocking_probability * 100 for r in history.records]
            spectral = [r.spectral_efficiency * 100 for r in history.records]
            qot = [r.qot for r in history.records]
            latency = [r.decision_latency_ms for r in history.records]
            
            data['agents'][name] = {
                'episodes': episodes,
                'rewards': rewards,
                'blocking': blocking,
                'spectral_efficiency': spectral,
                'qot': qot,
                'latency': latency
            }
        
        # Escribir atomically
        temp_file = self.live_data_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(data, f)
        temp_file.replace(self.live_data_file)
        
    def _load_agent(self, name: str) -> Optional[AgentState]:
        """Carga un agente entrenado desde disco."""
        config = BATTLE_AGENT_CONFIGS.get(name)
        training = BATTLE_TRAINING_CONFIGS.get(name)
        
        if not config or not training:
            console.print(f"[red]✗ Agent {name} not found in configs[/red]")
            return None
        
        model_path = Path(training.save_path)
        if not model_path.exists():
            console.print(f"[yellow]⚠ Model {model_path} not found. Skipping {name}.[/yellow]")
            return None
        
        try:
            # Build reward function
            try:
                reward_fn = build_ultra_reward_function(config.reward_id, weights={})
            except ValueError:
                from config import REWARD_WEIGHTS
                weights = REWARD_WEIGHTS.get(config.reward_id, {})
                reward_fn = build_reward_function(config.reward_id, weights)
            
            # Create environment
            env = self.factory.make(seed=self.seed)
            
            # Load model
            model = PPO.load(str(model_path), env=env)
            
            tracker = MetricsTracker()
            history = AgentHistory(name=config.name)
            
            console.print(f"[green]✓ Loaded {config.name}[/green]")
            
            return AgentState(
                name=config.name,
                model=model,
                env=env,
                tracker=tracker,
                history=history,
            )
        except Exception as e:
            console.print(f"[red]✗ Error loading {name}: {e}[/red]")
            return None
    
    def _intro_banner(self) -> None:
        """Banner de introducción épico."""
        banner = Text()
        banner.append("╔═══════════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
        banner.append("║                                                                       ║\n", style="bold cyan")
        banner.append("║         🚀 RMSA BATTLE ROYALE - DEEP RL SHOWDOWN 🚀                  ║\n", style="bold yellow")
        banner.append("║                                                                       ║\n", style="bold cyan")
        banner.append("║   6 Ultra-Modern Agents | 6 Network Topologies | 5 Reward Functions  ║\n", style="bold white")
        banner.append("║                                                                       ║\n", style="bold cyan")
        banner.append("║         Ryzen 7 5700X3D | PyTorch 2.5.1 | Stable-Baselines3         ║\n", style="bold green")
        banner.append("║                                                                       ║\n", style="bold cyan")
        banner.append("╚═══════════════════════════════════════════════════════════════════════╝\n", style="bold cyan")
        
        console.print(Panel(banner, border_style="bold magenta"))
        time.sleep(2)
    
    def _loading_agents(self) -> None:
        """Carga dramática de agentes con progress bar."""
        console.print("\n[bold cyan]📦 Loading Battle Royale Agents...[/bold cyan]\n")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(),
            console=console,
        ) as progress:
            task = progress.add_task("[cyan]Loading agents...", total=len(self.agents_to_load))
            
            for name in self.agents_to_load:
                progress.update(task, description=f"[cyan]Loading {name}...")
                agent = self._load_agent(name)
                if agent:
                    self.agents[name] = agent
                progress.advance(task)
                time.sleep(0.3)  # Dramatic pause
        
        console.print(f"\n[bold green]✓ {len(self.agents)}/{len(self.agents_to_load)} agents loaded successfully![/bold green]\n")
        time.sleep(1)
    
    def _run_episode(self, episode_num: int) -> BattleSnapshot:
        """Ejecuta un episodio para todos los agentes simultáneamente."""
        # Reset all agents
        observations = {}
        for name, agent in self.agents.items():
            obs, _ = agent.env.reset(seed=self.seed + episode_num)
            observations[name] = obs
            agent.tracker.reset()
        
        # Simulate single step (for demo purposes, we'll do 1 request per episode)
        snapshots = {}
        
        for name, agent in self.agents.items():
            obs = observations[name]
            
            # Predict action
            start_time = time.perf_counter()
            action, _ = agent.model.predict(obs, deterministic=True)
            latency_ms = (time.perf_counter() - start_time) * 1000
            
            # Step environment
            next_obs, reward, terminated, truncated, info = agent.env.step(action)
            done = terminated or truncated
            
            # Update metrics
            agent.tracker.update(info)
            agent.total_reward += reward
            agent.total_latency_ms += latency_ms
            agent.requests_processed += 1
            
            # Record episode
            record = record_from_info(
                episode=episode_num,
                info=info,
                reward=agent.total_reward,
                latency_ms=agent.total_latency_ms / max(agent.requests_processed, 1)
            )
            agent.history.append(record)
            
            # Build snapshot
            metrics_dict = agent.tracker.snapshot()
            snapshots[name] = AgentSnapshot(
                name=agent.name,
                step=agent.requests_processed,
                metrics=metrics_dict,
                shaped_reward=reward,
                last_action=f"Action {action}",
            )
            
            observations[name] = next_obs
        
        # Build battle snapshot
        return BattleSnapshot(
            episode=episode_num,
            request_id=episode_num,
            topology=self.topology_name,
            connection_label="Multi-Agent Battle Royale",
            agents=list(snapshots.values()),
        )
    
    def run(self) -> BattleMetrics:
        """Ejecuta la demo completa."""
        self._intro_banner()
        self._loading_agents()
        
        if not self.agents:
            console.print("[red]✗ No agents loaded. Exiting.[/red]")
            return BattleMetrics()
        
        console.print(f"[bold yellow]🎮 Starting Battle Royale - {self.episodes} episodes on {self.topology_name}[/bold yellow]\n")
        time.sleep(1)
        
        visualizer = UltraVisualizer()
        
        with visualizer:
            for episode in range(1, self.episodes + 1):
                self.current_episode = episode
                snapshot = self._run_episode(episode)
                visualizer.update(snapshot)
                
                # Escribir datos en tiempo real para el dashboard
                self._write_live_data()
                
                time.sleep(0.05)  # Control refresh rate (~20 FPS)
        
        # Final statistics
        self._final_report()
        
        # Build battle metrics
        histories = {name: agent.history for name, agent in self.agents.items()}
        return BattleMetrics(histories=histories)
    
    def _final_report(self) -> None:
        """Reporte final con estadísticas completas."""
        console.print("\n" + "="*80)
        console.print("[bold cyan]📊 FINAL BATTLE ROYALE STATISTICS[/bold cyan]")
        console.print("="*80 + "\n")
        
        from rich.table import Table
        
        table = Table(title="Agent Performance Summary", show_header=True, header_style="bold magenta")
        table.add_column("Agent", style="cyan", width=20)
        table.add_column("Avg Reward", justify="right", style="green")
        table.add_column("Blocking %", justify="right", style="yellow")
        table.add_column("Spectral Eff", justify="right", style="blue")
        table.add_column("Avg Latency (ms)", justify="right", style="white")
        
        # Calculate final metrics
        for name, agent in self.agents.items():
            avg_reward = agent.total_reward / max(agent.requests_processed, 1)
            avg_latency = agent.total_latency_ms / max(agent.requests_processed, 1)
            
            metrics = agent.tracker.snapshot()
            blocking = metrics.get("blocking", 0.0) * 100
            spectral = metrics.get("spectral_efficiency", 0.0) * 100
            
            table.add_row(
                name,
                f"{avg_reward:+.2f}",
                f"{blocking:.1f}%",
                f"{spectral:.1f}%",
                f"{avg_latency:.2f}",
            )
        
        console.print(table)
        console.print("\n" + "="*80 + "\n")
        
        # Winner declaration using composite score
        def calculate_score(agent_state):
            """Calculate composite score: (reward × 100) + (spectral × 50) + (qot × 30) - (blocking × 200)"""
            metrics = agent_state.tracker.snapshot()
            blocking = metrics.get("blocking", 1.0)
            spectral = metrics.get("spectral_efficiency", 0.0)
            qot = metrics.get("qot", 0.0)
            avg_reward = agent_state.total_reward / max(agent_state.requests_processed, 1)
            
            score = (avg_reward * 100) + (spectral * 50) + (qot * 30) - (blocking * 200)
            return score
        
        winner_name = max(self.agents.items(), key=lambda x: calculate_score(x[1]))[0]
        winner_score = calculate_score(self.agents[winner_name])
        console.print(f"[bold yellow]🏆 WINNER: {winner_name}! (Score: {winner_score:+.2f}) 🏆[/bold yellow]\n")


def parse_args():
    parser = argparse.ArgumentParser(description="RMSA Battle Royale Demo Orchestrator")
    parser.add_argument(
        "--agents",
        nargs="*",
        default=["CONTROL", "ULTHO", "HYPERQ-OPT", "BOHAMIANN", "DEEPRMSA-QOT", "META-LEARNING"],
        help="Agents to include in battle royale",
    )
    parser.add_argument("--episodes", type=int, default=200, help="Number of episodes to run")
    parser.add_argument("--topology", type=str, default="NSFNET", help="Network topology")
    parser.add_argument("--seed", type=int, default=31415, help="Random seed")
    parser.add_argument(
        "--extreme",
        action="store_true",
        help="Use EXTREME battle configuration (USNET, 95%% load, 100 slots)",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    
    # Use extreme configuration if requested
    if args.extreme:
        from battle_config_extreme import EXTREME_ENVIRONMENT, EXTREME_DEMO, get_extreme_battle_description
        
        console.print(Panel(
            get_extreme_battle_description(),
            title="[bold red]🔥 EXTREME MODE ACTIVATED 🔥[/bold red]",
            border_style="bold red",
        ))
        time.sleep(3)
        
        # Override environment settings
        from environment import EnvironmentFactory
        factory = EnvironmentFactory(base_kwargs=EXTREME_ENVIRONMENT.as_dict())
        
        # Use extreme topology and episodes
        topology = EXTREME_ENVIRONMENT.topology
        episodes = args.episodes if args.episodes != 200 else EXTREME_DEMO.demo_requests
        
    else:
        topology = args.topology
        episodes = args.episodes
    
    orchestrator = DemoOrchestrator(
        agents_to_load=args.agents,
        episodes=episodes,
        topology=topology,
        seed=args.seed,
    )
    
    battle_metrics = orchestrator.run()
    
    console.print("[bold green]✓ Battle Royale completed successfully![/bold green]")
    
    # Auto-generate dashboards if battle metrics are valid
    if battle_metrics.histories:
        console.print("\n[bold cyan]📊 Generating Advanced Dashboards...[/bold cyan]\n")
        
        try:
            from plotly_dashboard import generate_dashboards_from_battle
            from network_visualizer import NetworkVisualizer
            from presentation_visualizer import generate_presentation_visualizations
            
            # Generate Plotly dashboards
            console.print("  [yellow]→[/yellow] Creating comprehensive analysis dashboard...")
            generate_dashboards_from_battle(battle_metrics, output_dir="dashboards")
            console.print("  [green]✓[/green] Dashboards saved to [cyan]dashboards/[/cyan]")
            
            # Generate presentation visualizations
            console.print("  [yellow]→[/yellow] Creating presentation-ready visualizations...")
            generate_presentation_visualizations(battle_metrics, output_dir="presentation_viz")
            console.print("  [green]✓[/green] Presentation visualizations saved to [cyan]presentation_viz/[/cyan]")
            
            # Generate network visualizations
            console.print("  [yellow]→[/yellow] Creating network topology comparisons...")
            viz = NetworkVisualizer()
            viz.save_all_visualizations()
            console.print("  [green]✓[/green] Network visualizations saved to [cyan]network_viz/[/cyan]")
            
            console.print("\n[bold green]🎉 All visualizations generated successfully![/bold green]")
            console.print("\n[bold yellow]📁 Open these files to view results:[/bold yellow]")
            console.print("\n[bold cyan]Main Dashboards:[/bold cyan]")
            console.print("  • [cyan]dashboards/comprehensive_analysis.html[/cyan]")
            console.print("  • [cyan]dashboards/statistical_tests.html[/cyan]")
            console.print("\n[bold cyan]Presentation Visualizations:[/bold cyan]")
            console.print("  • [cyan]presentation_viz/box_plot_comparison.html[/cyan]")
            console.print("  • [cyan]presentation_viz/radar_chart.html[/cyan]")
            console.print("  • [cyan]presentation_viz/violin_plot.html[/cyan]")
            console.print("  • [cyan]presentation_viz/correlation_heatmap.html[/cyan]")
            console.print("  • [cyan]presentation_viz/3d_scatter.html[/cyan]")
            console.print("  • [cyan]presentation_viz/time_series.html[/cyan]")
            console.print("  • [cyan]presentation_viz/ranking_table.html[/cyan]")
            console.print("\n[bold cyan]Network Visualizations:[/bold cyan]")
            console.print("  • [cyan]network_viz/all_topologies_comparison.html[/cyan]")
            
        except Exception as e:
            console.print(f"[yellow]⚠ Could not generate dashboards: {e}[/yellow]")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    main()
