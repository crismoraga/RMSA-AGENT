"""Metric tracking utilities for the RMSA demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass
class EpisodeMetrics:
    allocated: int = 0
    blocked: int = 0
    qot_acc: float = 0.0
    spectral_efficiency_acc: float = 0.0
    fragmentation_acc: float = 0.0
    load_balance_acc: float = 0.0
    steps: int = 0

    def update(self, info: Dict[str, float]) -> None:
        if info.get("allocation_success", False):
            self.allocated += 1
        else:
            self.blocked += 1

        self.qot_acc += float(info.get("qot", 0.0))
        self.spectral_efficiency_acc += float(info.get("spectral_efficiency", 0.0))
        self.fragmentation_acc += float(info.get("fragmentation", 0.0))
        self.load_balance_acc += float(info.get("load_balance", 0.0))
        self.steps += 1

    def as_dict(self) -> Dict[str, float]:
        safe_steps = max(self.steps, 1)
        return {
            "blocking": self.blocked / safe_steps,
            "acceptance": self.allocated / safe_steps,
            "qot": self.qot_acc / safe_steps,
            "spectral_efficiency": self.spectral_efficiency_acc / safe_steps,
            "fragmentation": self.fragmentation_acc / safe_steps,
            "load_balance": self.load_balance_acc / safe_steps,
            "steps": self.steps,
        }


@dataclass
class MetricsTracker:
    current: EpisodeMetrics = field(default_factory=EpisodeMetrics)

    def reset(self) -> None:
        self.current = EpisodeMetrics()

    def update(self, info: Dict[str, float]) -> None:
        self.current.update(info)

    def snapshot(self) -> Dict[str, float]:
        return self.current.as_dict()
