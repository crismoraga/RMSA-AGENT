"""Central configuration objects for the RMSA demo."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Any, Tuple


@dataclass(frozen=True)
class AgentConfig:
    name: str
    policy: str
    learning_rate: float
    gamma: float
    batch_size: int
    n_steps: int
    net_arch: Tuple[int, ...]
    activation: str
    reward_id: str
    dropout: float = 0.0
    grad_clip: float = 0.5
    ent_coef: float = 0.0
    vf_coef: float = 0.5
    max_grad_norm: float = 0.5
    extra_kwargs: Dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class EnvironmentConfig:
    topology: str = "NSFNET"
    frequency_slots: int = 196
    load: float = 0.8
    episode_length: int = 100
    seed: int = 42
    spectrum: str = "C"

    def as_dict(self) -> Dict[str, Any]:
        return {
            "episode_length": self.episode_length,
            "load": self.load,
            "seed": self.seed,
            "topology": self.topology,
            "num_freq_slots": self.frequency_slots,
        }


@dataclass(frozen=True)
class TrainingConfig:
    timesteps: int
    tensorboard_log: str
    save_path: str
    eval_freq: int = 5000
    save_freq: int = 10000


@dataclass(frozen=True)
class DemoConfig:
    demo_requests: int = 200
    refresh_hz: float = 15.0
    fairness_seed: int = 31415


DEFAULT_AGENT_CONFIG = AgentConfig(
    name="Default",
    policy="MlpPolicy",
    learning_rate=1e-3,
    gamma=0.99,
    batch_size=64,
    n_steps=1024,
    net_arch=(128, 128),
    activation="relu",
    reward_id="binary",
    dropout=0.0,
    grad_clip=0.5,
    ent_coef=0.0,
    vf_coef=0.5,
    max_grad_norm=0.5,
)

OPTIMIZED_AGENT_CONFIG = AgentConfig(
    name="Optimized",
    policy="MlpPolicy",
    learning_rate=2.7e-4,
    gamma=0.997,
    batch_size=256,
    n_steps=2048,
    net_arch=(256, 256, 256, 256),
    activation="silu",
    reward_id="multi_objective",
    dropout=0.2,
    grad_clip=0.8,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.8,
    extra_kwargs={},  # SDE removido (solo para acciones continuas)
)

DEFAULT_TRAINING = TrainingConfig(
    timesteps=50_000,
    tensorboard_log="logs/default",
    save_path="models/default_agent.zip",
    eval_freq=5000,
)

OPTIMIZED_TRAINING = TrainingConfig(
    timesteps=100_000,
    tensorboard_log="logs/optimized",
    save_path="models/optimized_agent.zip",
    eval_freq=5000,
)

ENVIRONMENT = EnvironmentConfig()
DEMO = DemoConfig()

REWARD_WEIGHTS: Dict[str, Dict[str, float]] = {
    "multi_objective": {
        "allocation": 10.0,
        "qot": 3.0,
        "spectral_efficiency": 5.0,
        "fragmentation": 2.0,
        "load_balance": 1.5,
    }
}
