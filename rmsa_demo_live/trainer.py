"""Training entrypoints for the RMSA Battle Royale (6 agents)."""
from __future__ import annotations

import argparse
import time
from typing import Dict, Iterable

from rich.console import Console

from agents import AgentBuilder, train_agent
from config import (
    BATTLE_AGENT_CONFIGS,
    BATTLE_TRAINING_CONFIGS,
    ENVIRONMENT,
    TrainingConfig,
    REWARD_WEIGHTS,
)
from cpu_optimizer import configure_cpu_performance, print_system_info
from environment import EnvironmentFactory
from reward_engineering import build_ultra_reward_function
from reward_functions import build_reward_function

console = Console()


def build_reward(reward_id: str):
    weights = REWARD_WEIGHTS.get(reward_id, {})
    try:
        return build_ultra_reward_function(reward_id, weights=weights)
    except ValueError:
        return build_reward_function(reward_id, weights)


def _resolve_roster(selection: Iterable[str]) -> Dict[str, str]:
    roster = {}
    for alias in selection:
        key = alias.upper()
        if key not in BATTLE_AGENT_CONFIGS:
            raise ValueError(f"Unknown agent '{alias}'. Available: {list(BATTLE_AGENT_CONFIGS)}")
        roster[key] = key
    return roster


def run_training(selected_agents: Iterable[str], seed: int, fast: bool = False) -> None:
    console.print("\n[bold cyan]🚀 Configuring CPU Performance...[/bold cyan]")
    configure_cpu_performance()
    print_system_info()

    roster = _resolve_roster(selected_agents)
    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())

    console.print(f"\n[bold green]✓ Training {len(roster)} agent(s)[/bold green]\n")

    for idx, name in enumerate(roster, 1):
        config = BATTLE_AGENT_CONFIGS[name]
        training = BATTLE_TRAINING_CONFIGS[name]
        agent_seed = seed + idx * 101

        effective_training = training
        if fast:
            effective_training = TrainingConfig(
                timesteps=max(training.timesteps // 20, 5_000),
                tensorboard_log=training.tensorboard_log,
                save_path=training.save_path,
                eval_freq=max(training.eval_freq // 5, 1_000),
            )

        console.print(f"[bold magenta]{'=' * 72}[/bold magenta]")
        console.print(f"[bold cyan]🤖 Agent {idx}/{len(roster)}: {config.name}[/bold cyan]")
        console.print(f"[bold magenta]{'=' * 72}[/bold magenta]\n")
        console.print(f"  Architecture: {config.net_arch}")
        console.print(f"  Timesteps: {effective_training.timesteps:,}")
        console.print(f"  Reward: {config.reward_id}\n")

        builder = AgentBuilder(
            config=config,
            factory=factory,
            reward_fn=build_reward(config.reward_id),
        )
        start = time.time()
        train_agent(builder, effective_training, agent_seed)
        elapsed = time.time() - start
        console.print(f"\n[bold green]✓ {config.name} finished in {elapsed/60:.1f} min[/bold green]\n")

    console.print("\n[bold green]🎉 ALL TRAINING COMPLETED![/bold green]\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train RMSA Battle Royale agents")
    parser.add_argument(
        "--agents",
        nargs="*",
        default=["CONTROL", "ULTHO", "HYPERQ-OPT", "BOHAMIANN", "DEEPRMSA-QOT", "META-LEARNING"],
        help="Subset of agents to train (case insensitive).",
    )
    parser.add_argument("--seed", type=int, default=42, help="Base random seed")
    parser.add_argument("--fast", action="store_true", help="Run a fast smoke-test training (5% timesteps)")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_training(args.agents, args.seed, fast=args.fast)


if __name__ == "__main__":
    main()
