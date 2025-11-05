"""🎬 Demo Orchestrator - RMSA Battle Royale Ultra-Vanguardista.

Orquesta la demo épica de 10 minutos comparando 6 agentes de RL optimizando RMSA.
"""
from __future__ import annotations

import argparse
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
                snapshot = self._run_episode(episode)
                visualizer.update(snapshot)
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
        
        # Winner declaration
        winner_name = max(self.agents.items(), key=lambda x: x[1].total_reward)[0]
        console.print(f"[bold yellow]🏆 WINNER: {winner_name}! 🏆[/bold yellow]\n")


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
    return parser.parse_args()


def main():
    args = parse_args()
    
    orchestrator = DemoOrchestrator(
        agents_to_load=args.agents,
        episodes=args.episodes,
        topology=args.topology,
        seed=args.seed,
    )
    
    battle_metrics = orchestrator.run()
    
    console.print("[bold green]✓ Battle Royale completed successfully![/bold green]")


if __name__ == "__main__":
    main()
