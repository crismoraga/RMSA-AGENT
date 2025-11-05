"""Advanced metrics engine for the RMSA Battle Royale demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean, pstdev
from typing import Dict, List, Optional

import numpy as np
from scipy import stats


@dataclass
class EpisodeRecord:
    """Stores metrics for a single episode executed by one agent."""

    episode: int
    blocking_probability: float
    spectral_efficiency: float
    qot: float
    fragmentation: float
    load_balance: float
    cumulative_reward: float
    decision_latency_ms: float


@dataclass
class AgentHistory:
    """Keeps track of multiple episode records for an agent."""

    name: str
    records: List[EpisodeRecord] = field(default_factory=list)

    def append(self, record: EpisodeRecord) -> None:
        self.records.append(record)

    # ------------------------------------------------------------------
    # Aggregate statistics
    # ------------------------------------------------------------------
    def _values(self, attr: str) -> List[float]:
        return [getattr(record, attr) for record in self.records]

    def mean(self, attr: str) -> float:
        values = self._values(attr)
        return mean(values) if values else 0.0

    def std(self, attr: str) -> float:
        values = self._values(attr)
        return pstdev(values) if values else 0.0

    def latest(self) -> Optional[EpisodeRecord]:
        return self.records[-1] if self.records else None
    
    # Convenience methods for common metrics
    def mean_blocking(self) -> float:
        return self.mean("blocking_probability")
    
    def mean_spectral_efficiency(self) -> float:
        return self.mean("spectral_efficiency")
    
    def mean_qot(self) -> float:
        return self.mean("qot")
    
    def mean_reward(self) -> float:
        return self.mean("cumulative_reward")
    
    def mean_latency_ms(self) -> float:
        return self.mean("decision_latency_ms")
    
    def std_blocking(self) -> float:
        return self.std("blocking_probability")


@dataclass
class BattleMetrics:
    """Aggregated statistics across all agents."""

    histories: Dict[str, AgentHistory] = field(default_factory=dict)

    def ensure_agent(self, agent_name: str) -> AgentHistory:
        if agent_name not in self.histories:
            self.histories[agent_name] = AgentHistory(agent_name)
        return self.histories[agent_name]

    def append(self, agent_name: str, record: EpisodeRecord) -> None:
        self.ensure_agent(agent_name).append(record)

    # ------------------------------------------------------------------
    # Comparative statistics
    # ------------------------------------------------------------------
    def ranking(self, attribute: str, higher_is_better: bool = True) -> List[str]:
        scores = []
        for name, history in self.histories.items():
            value = history.mean(attribute)
            scores.append((value, name))
        scores.sort(reverse=higher_is_better)
        return [name for _, name in scores]

    def compare(self, metric: str) -> Dict[str, float]:
        """Return mean values for ``metric`` per agent."""

        return {name: history.mean(metric) for name, history in self.histories.items()}

    def t_test(self, agent_a: str, agent_b: str, metric: str) -> Dict[str, float]:
        """Perform Welch's t-test between agents for ``metric``."""

        hist_a = self.histories.get(agent_a)
        hist_b = self.histories.get(agent_b)
        if not hist_a or not hist_b:
            raise ValueError("Both agents must have history for t-test")
        values_a = hist_a._values(metric)
        values_b = hist_b._values(metric)
        if len(values_a) < 2 or len(values_b) < 2:
            raise ValueError("Not enough samples for t-test")
        statistic, pvalue = stats.ttest_ind(values_a, values_b, equal_var=False)
        return {"statistic": float(statistic), "pvalue": float(pvalue)}

    def anova(self, metric: str) -> Dict[str, float]:
        """One-way ANOVA across all agents for the provided metric."""

        samples = [history._values(metric) for history in self.histories.values() if history.records]
        if len(samples) < 2:
            raise ValueError("At least two agents with data required for ANOVA")
        statistic, pvalue = stats.f_oneway(*samples)
        return {"statistic": float(statistic), "pvalue": float(pvalue)}

    # ------------------------------------------------------------------
    # Utility exports
    # ------------------------------------------------------------------
    def as_numpy(self, metric: str) -> Dict[str, np.ndarray]:
        return {name: np.asarray(history._values(metric)) for name, history in self.histories.items()}

    def summary(self) -> Dict[str, Dict[str, float]]:
        metrics = [
            "blocking_probability",
            "spectral_efficiency",
            "qot",
            "fragmentation",
            "load_balance",
            "cumulative_reward",
            "decision_latency_ms",
        ]
        summary: Dict[str, Dict[str, float]] = {}
        for name, history in self.histories.items():
            summary[name] = {metric: history.mean(metric) for metric in metrics}
        return summary


def record_from_info(episode: int, info: Dict[str, float], *, reward: float, latency_ms: float) -> EpisodeRecord:
    """Helper to build an :class:`EpisodeRecord` from an environment info dict."""

    return EpisodeRecord(
        episode=episode,
        blocking_probability=1.0 - float(info.get("allocation_success", 0.0)),
        spectral_efficiency=float(info.get("spectral_efficiency", 0.0)),
        qot=float(info.get("qot", 0.0)),
        fragmentation=float(info.get("fragmentation", 0.0)),
        load_balance=float(info.get("load_balance", 0.0)),
        cumulative_reward=reward,
        decision_latency_ms=latency_ms,
    )


__all__ = [
    "EpisodeRecord",
    "AgentHistory",
    "BattleMetrics",
    "record_from_info",
]
