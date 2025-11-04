"""Reward shaping utilities for RMSA agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Protocol


class RewardFunction(Protocol):
    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        ...


@dataclass(frozen=True)
class BinaryReward:
    success_bonus: float = 1.0
    block_penalty: float = -1.0

    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        success = info.get("allocation_success", reward > 0)
        return self.success_bonus if success else self.block_penalty


@dataclass(frozen=True)
class MultiObjectiveReward:
    weights: Dict[str, float]
    block_penalty: float = -2.0

    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", reward > 0):
            return self.block_penalty

        score = 0.0
        for key, weight in self.weights.items():
            component = info.get(key)
            if component is None:
                continue
            score += weight * float(component)
        return score


def build_reward_function(reward_id: str, weights: Dict[str, float]) -> RewardFunction:
    if reward_id == "binary":
        return BinaryReward()
    if reward_id == "multi_objective":
        return MultiObjectiveReward(weights=weights)
    raise ValueError(f"Unknown reward id: {reward_id}")
