"""Training entrypoints for RMSA agents."""
from __future__ import annotations

import argparse

from agents import AgentBuilder, train_agent
from config import (
    DEFAULT_AGENT_CONFIG,
    DEFAULT_TRAINING,
    ENVIRONMENT,
    OPTIMIZED_AGENT_CONFIG,
    OPTIMIZED_TRAINING,
    REWARD_WEIGHTS,
)
from environment import EnvironmentFactory
from reward_functions import build_reward_function


def build_reward(id_: str):
    weights = REWARD_WEIGHTS.get(id_, {})
    return build_reward_function(id_, weights)


def run_training(run_default: bool, run_optimized: bool, seed: int) -> None:
    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())

    if run_default:
        default_builder = AgentBuilder(
            config=DEFAULT_AGENT_CONFIG,
            factory=factory,
            reward_fn=build_reward(DEFAULT_AGENT_CONFIG.reward_id),
        )
        train_agent(default_builder, DEFAULT_TRAINING, seed)

    if run_optimized:
        optimized_builder = AgentBuilder(
            config=OPTIMIZED_AGENT_CONFIG,
            factory=factory,
            reward_fn=build_reward(OPTIMIZED_AGENT_CONFIG.reward_id),
        )
        train_agent(optimized_builder, OPTIMIZED_TRAINING, seed + 101)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train RMSA PPO agents")
    parser.add_argument("--optimized", action="store_true", help="Train optimized agent")
    parser.add_argument("--default", action="store_true", help="Train default agent")
    parser.add_argument("--seed", type=int, default=1234)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    run_default = args.default or not args.optimized
    run_optimized = args.optimized or not args.default
    run_training(run_default, run_optimized, args.seed)


if __name__ == "__main__":
    main()
