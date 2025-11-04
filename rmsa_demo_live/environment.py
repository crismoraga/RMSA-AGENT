"""Gymnasium environment helpers for the RMSA live demo."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import numpy as np

try:
    import gymnasium as gym
except ImportError as exc:  # pragma: no cover - sanity guard
    raise RuntimeError(
        "gymnasium is required for the RMSA demo. Install requirements first"
    ) from exc

from reward_functions import RewardFunction
import rmsa_environment  # noqa: F401 - registers the environment


def _resolve_env_id() -> str:
    return "RMSA-v0"


@dataclass
class EnvironmentFactory:
    base_kwargs: Dict[str, Any]

    def make(self, seed: Optional[int] = None) -> gym.Env:
        env_id = _resolve_env_id()
        env = gym.make(env_id, **self.base_kwargs)
        if seed is not None:
            env.reset(seed=seed)
        return env


class RewardShapingWrapper(gym.Wrapper):
    def __init__(self, env: gym.Env, reward_fn: RewardFunction) -> None:
        super().__init__(env)
        self._reward_fn = reward_fn

    def step(self, action):
        obs, reward, terminated, truncated, info = self.env.step(action)
        shaped = self._reward_fn(obs, action, reward, terminated or truncated, info)
        info = dict(info)
        info["shaped_reward"] = shaped
        return obs, shaped, terminated, truncated, info


class RMSAEnvironmentWrapper:
    def __init__(
        self,
        factory: EnvironmentFactory,
        reward_fn: RewardFunction,
        seed: Optional[int] = None,
    ) -> None:
        self._factory = factory
        self._reward_fn = reward_fn
        self._seed = seed
        self._env = RewardShapingWrapper(self._factory.make(seed=seed), reward_fn)
        self._rng = np.random.default_rng(seed)

    @property
    def raw_env(self) -> gym.Env:
        return self._env

    def reset(self) -> Tuple[Any, Dict[str, Any]]:
        observation, info = self._env.reset(seed=self._rng.integers(0, 1_000_000))
        return observation, info

    def step(self, action) -> Tuple[Any, float, bool, bool, Dict[str, Any]]:
        return self._env.step(action)

    def close(self) -> None:
        self._env.close()

    def clone(self) -> "RMSAEnvironmentWrapper":
        return RMSAEnvironmentWrapper(
            self._factory,
            self._reward_fn,
            seed=self._rng.integers(0, 1_000_000),
        )


def make_training_env(
    factory: EnvironmentFactory,
    reward_fn: RewardFunction,
    seed: Optional[int] = None,
) -> gym.Env:
    return RewardShapingWrapper(factory.make(seed=seed), reward_fn)
