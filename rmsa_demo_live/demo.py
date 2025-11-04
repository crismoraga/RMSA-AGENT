"""Live demo runner comparing default vs optimized agents."""
from __future__ import annotations

from pathlib import Path
from typing import Generator, Iterable, Tuple

from stable_baselines3 import PPO

from agents import AgentBuilder
from config import (
    DEFAULT_AGENT_CONFIG,
    DEFAULT_TRAINING,
    DEMO,
    ENVIRONMENT,
    OPTIMIZED_AGENT_CONFIG,
    OPTIMIZED_TRAINING,
    REWARD_WEIGHTS,
)
from environment import EnvironmentFactory, RMSAEnvironmentWrapper
from metrics import MetricsTracker
from reward_functions import build_reward_function
from visualizer import AgentSnapshot, DemoSnapshot, LiveVisualizer


def _load_model_or_raise(path: str) -> PPO:
    resolved = Path(path)
    if not resolved.exists():
        raise FileNotFoundError(f"Model checkpoint not found: {resolved}")
    return PPO.load(resolved)


def _prepare_agent(
    builder: AgentBuilder,
    checkpoint: str,
    seed: int,
) -> Tuple[PPO, RMSAEnvironmentWrapper, MetricsTracker]:
    model = _load_model_or_raise(checkpoint)
    tracker = MetricsTracker()
    env = RMSAEnvironmentWrapper(
        factory=builder.factory,
        reward_fn=builder.reward_fn,
        seed=seed,
    )
    env.reset()
    return model, env, tracker


def _snapshot_from(
    name: str,
    step: int,
    shaped_reward: float,
    info: dict,
    tracker: MetricsTracker,
) -> AgentSnapshot:
    metrics = tracker.snapshot()
    last_action = info.get("action_label") or info.get("path") or ""
    return AgentSnapshot(
        name=name,
        step=step,
        shaped_reward=shaped_reward,
        metrics=metrics,
        last_action=str(last_action),
    )


def _episode_stream(
    default_model: PPO,
    optimized_model: PPO,
    default_env: RMSAEnvironmentWrapper,
    optimized_env: RMSAEnvironmentWrapper,
    default_tracker: MetricsTracker,
    optimized_tracker: MetricsTracker,
    max_requests: int,
    episode_id: int,
) -> Generator[DemoSnapshot, None, None]:
    default_obs, default_info = default_env.reset()
    optimized_obs, optimized_info = optimized_env.reset()

    for request_idx in range(1, max_requests + 1):
        default_action, _ = default_model.predict(default_obs, deterministic=True)
        optimized_action, _ = optimized_model.predict(optimized_obs, deterministic=True)

        default_obs, default_reward, default_term, default_trunc, default_info = default_env.step(
            default_action
        )
        optimized_obs, optimized_reward, opt_term, opt_trunc, optimized_info = optimized_env.step(
            optimized_action
        )

        default_tracker.update(default_info)
        optimized_tracker.update(optimized_info)

        connection_label = optimized_info.get("connection_label") or default_info.get(
            "connection_label", ""
        )

        yield DemoSnapshot(
            episode=episode_id,
            request_id=request_idx,
            default_agent=_snapshot_from(
                DEFAULT_AGENT_CONFIG.name,
                request_idx,
                default_reward,
                default_info,
                default_tracker,
            ),
            optimized_agent=_snapshot_from(
                OPTIMIZED_AGENT_CONFIG.name,
                request_idx,
                optimized_reward,
                optimized_info,
                optimized_tracker,
            ),
            connection_label=str(connection_label),
        )

        if default_term or default_trunc or opt_term or opt_trunc:
            break


def demo_stream(episodes: int = 1) -> Iterable[DemoSnapshot]:
    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())

    default_builder = AgentBuilder(
        config=DEFAULT_AGENT_CONFIG,
        factory=factory,
        reward_fn=build_reward_function(
            DEFAULT_AGENT_CONFIG.reward_id, REWARD_WEIGHTS.get(DEFAULT_AGENT_CONFIG.reward_id, {})
        ),
    )
    optimized_builder = AgentBuilder(
        config=OPTIMIZED_AGENT_CONFIG,
        factory=factory,
        reward_fn=build_reward_function(
            OPTIMIZED_AGENT_CONFIG.reward_id, REWARD_WEIGHTS.get(OPTIMIZED_AGENT_CONFIG.reward_id, {})
        ),
    )

    default_model, default_env, default_tracker = _prepare_agent(
        default_builder, DEFAULT_TRAINING.save_path, DEMO.fairness_seed
    )
    optimized_model, optimized_env, optimized_tracker = _prepare_agent(
        optimized_builder, OPTIMIZED_TRAINING.save_path, DEMO.fairness_seed + 7
    )

    for episode in range(1, episodes + 1):
        default_tracker.reset()
        optimized_tracker.reset()
        yield from _episode_stream(
            default_model,
            optimized_model,
            default_env,
            optimized_env,
            default_tracker,
            optimized_tracker,
            DEMO.demo_requests,
            episode,
        )


def main() -> None:
    visualizer = LiveVisualizer(refresh_hz=DEMO.refresh_hz)
    visualizer.run(demo_stream())


if __name__ == "__main__":
    main()
