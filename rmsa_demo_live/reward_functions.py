"""Reward shaping utilities for RMSA agents."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, Protocol

import numpy as np


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


@dataclass(frozen=True)
class QoTFocusedReward:
    """
    QoT-focused reward with exponential OSNR penalties.
    Specialized for Deep-QoT agent.
    """
    weights: Dict[str, float]
    block_penalty: float = -3.0
    qot_threshold: float = 15.0  # Minimum acceptable OSNR (dB)

    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", reward > 0):
            return self.block_penalty

        score = 0.0
        
        # QoT component with exponential weighting
        qot_value = info.get("qot", 0.0)
        if qot_value > 0:
            # Exponential bonus for high QoT
            qot_score = self.weights.get("qot", 5.0) * (1.0 - np.exp(-qot_value / self.qot_threshold))
            score += qot_score
        
        # Other components with standard weighting
        for key, weight in self.weights.items():
            if key == "qot":
                continue  # Already handled above
            component = info.get(key)
            if component is None:
                continue
            score += weight * float(component)
        
        return score


@dataclass(frozen=True)
class AdaptiveReward:
    """
    Adaptive reward that evolves during training.
    Includes exploration bonus and curriculum weighting.
    """
    weights: Dict[str, float]
    block_penalty: float = -2.5
    exploration_bonus_decay: float = 0.995
    
    def __init__(self, weights: Dict[str, float], block_penalty: float = -2.5):
        object.__setattr__(self, 'weights', weights)
        object.__setattr__(self, 'block_penalty', block_penalty)
        object.__setattr__(self, 'exploration_bonus_decay', 0.995)
        object.__setattr__(self, '_episode_count', 0)
    
    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", reward > 0):
            return self.block_penalty
        
        # Base multi-objective score
        score = 0.0
        for key, weight in self.weights.items():
            component = info.get(key)
            if component is None:
                continue
            score += weight * float(component)
        
        # Exploration bonus (decays over time)
        exploration_bonus = 0.5 * (self.exploration_bonus_decay ** self._episode_count)
        
        # Quality bonus for high spectral efficiency
        spectral_eff = info.get("spectral_efficiency", 0.0)
        quality_bonus = 1.0 if spectral_eff > 0.6 else 0.0
        
        total_reward = score + exploration_bonus + quality_bonus
        
        # Increment episode counter on episode end
        if done:
            object.__setattr__(self, '_episode_count', self._episode_count + 1)
        
        return total_reward


@dataclass(frozen=True)
class SpectralEfficiencyReward:
    """
    Spectral efficiency maximization reward.
    Heavily penalizes spectrum waste and fragmentation.
    """
    weights: Dict[str, float]
    block_penalty: float = -2.0
    
    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", reward > 0):
            return self.block_penalty
        
        # Calculate base score with emphasis on spectral efficiency
        score = 0.0
        for key, weight in self.weights.items():
            component = info.get(key)
            if component is None:
                continue
            
            # Apply exponential scaling for spectral efficiency
            if key == "spectral_efficiency":
                # Reward grows exponentially with high efficiency
                scaled = (float(component) ** 1.5) * weight
                score += scaled
            else:
                score += weight * float(component)
        
        # Extra penalty for high fragmentation (anti-spectral waste)
        fragmentation = info.get("fragmentation", 0.0)
        if fragmentation > 0.7:
            score -= 1.5 * fragmentation
        
        return score


@dataclass(frozen=True)
class MetaLearningReward:
    """
    Meta-learning reward that encourages topology-agnostic strategies.
    Balanced across all metrics for better generalization.
    """
    weights: Dict[str, float]
    block_penalty: float = -2.2
    
    def __init__(self, weights: Dict[str, float], block_penalty: float = -2.2):
        object.__setattr__(self, 'weights', weights)
        object.__setattr__(self, 'block_penalty', block_penalty)
        object.__setattr__(self, '_performance_history', [])
    
    def __call__(self, observation, action, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", reward > 0):
            return self.block_penalty
        
        # Balanced multi-objective score
        score = 0.0
        metrics_collected = []
        
        for key, weight in self.weights.items():
            component = info.get(key)
            if component is None:
                continue
            value = float(component)
            score += weight * value
            metrics_collected.append(value)
        
        # Reward consistency across metrics (meta-learning bonus)
        if len(metrics_collected) >= 3:
            # Lower variance = more balanced performance = better generalization
            variance = np.var(metrics_collected)
            consistency_bonus = 0.5 * (1.0 - min(variance, 1.0))
            score += consistency_bonus
        
        # Network health bonus (encourages sustainable allocations)
        load_balance = info.get("load_balance", 0.0)
        qot = info.get("qot", 0.0)
        if load_balance > 0.7 and qot > 0.6:
            score += 0.8  # Bonus for healthy network state
        
        return score


def build_reward_function(reward_id: str, weights: Dict[str, float]) -> RewardFunction:
    if reward_id == "binary":
        return BinaryReward()
    if reward_id == "multi_objective":
        return MultiObjectiveReward(weights=weights)
    if reward_id == "qot_focused":
        return QoTFocusedReward(weights=weights)
    if reward_id == "adaptive":
        return AdaptiveReward(weights=weights)
    if reward_id == "spectral_efficiency":
        return SpectralEfficiencyReward(weights=weights)
    if reward_id == "meta_learning":
        return MetaLearningReward(weights=weights)
    raise ValueError(f"Unknown reward id: {reward_id}")
