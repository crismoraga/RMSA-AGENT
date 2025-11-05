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

ULTHO_AGENT_CONFIG = AgentConfig(
    name="ULTHO",
    policy="MlpPolicy",
    learning_rate=2.5e-4,
    gamma=0.997,
    batch_size=256,
    n_steps=2048,
    net_arch=(512, 384, 256, 128),
    activation="silu",
    reward_id="qot_aware",
    dropout=0.15,
    grad_clip=0.85,
    ent_coef=0.012,
    vf_coef=0.5,
    max_grad_norm=0.85,
    extra_kwargs={},
)

DEEPRMSA_QOT_AGENT_CONFIG = AgentConfig(
    name="DEEPRMSA-QOT",
    policy="MlpPolicy",
    learning_rate=1.5e-4,
    gamma=0.996,
    batch_size=224,
    n_steps=1792,
    net_arch=(384, 384, 384),
    activation="elu",
    reward_id="qot_aware",
    dropout=0.15,
    grad_clip=0.75,
    ent_coef=0.006,
    vf_coef=0.5,
    max_grad_norm=0.75,
    extra_kwargs={},
)

HYPERQ_OPT_AGENT_CONFIG = AgentConfig(
    name="HYPERQ-OPT",
    policy="MlpPolicy",
    learning_rate=1.8e-4,
    gamma=0.998,
    batch_size=256,
    n_steps=2048,
    net_arch=(320, 320, 320, 320),
    activation="leaky_relu",
    reward_id="delayed_assignment",
    dropout=0.18,
    grad_clip=0.8,
    ent_coef=0.012,
    vf_coef=0.5,
    max_grad_norm=0.8,
    extra_kwargs={},
)

BOHAMIANN_AGENT_CONFIG = AgentConfig(
    name="BOHAMIANN",
    policy="MlpPolicy",
    learning_rate=1.2e-4,
    gamma=0.998,
    batch_size=288,
    n_steps=2048,
    net_arch=(512, 384, 256, 128),
    activation="tanh",
    reward_id="bayesian_multi_objective",
    dropout=0.25,
    grad_clip=0.9,
    ent_coef=0.01,
    vf_coef=0.5,
    max_grad_norm=0.9,
    extra_kwargs={},
)

META_LEARNING_AGENT_CONFIG = AgentConfig(
    name="META-LEARNING",
    policy="MlpPolicy",
    learning_rate=1.8e-4,
    gamma=0.994,
    batch_size=288,
    n_steps=1920,
    net_arch=(448, 448, 320, 320),
    activation="gelu",
    reward_id="adaptive_curriculum",
    dropout=0.2,
    grad_clip=0.85,
    ent_coef=0.02,
    vf_coef=0.5,
    max_grad_norm=0.85,
    extra_kwargs={},
)

DEFAULT_TRAINING = TrainingConfig(
    timesteps=50_000,
    tensorboard_log="logs/default",
    save_path="models/default_agent.zip",
    eval_freq=5000,
)

ULTHO_TRAINING = TrainingConfig(
    timesteps=100_000,
    tensorboard_log="logs/ultho",
    save_path="models/ultho_agent.zip",
    eval_freq=5000,
)

DEEPRMSA_QOT_TRAINING = TrainingConfig(
    timesteps=90_000,
    tensorboard_log="logs/deeprmsa_qot",
    save_path="models/deeprmsa_qot_agent.zip",
    eval_freq=5000,
)

HYPERQ_OPT_TRAINING = TrainingConfig(
    timesteps=90_000,
    tensorboard_log="logs/hyperq",
    save_path="models/hyperq_agent.zip",
    eval_freq=5000,
)

BOHAMIANN_TRAINING = TrainingConfig(
    timesteps=110_000,
    tensorboard_log="logs/bohamiann",
    save_path="models/bohamiann_agent.zip",
    eval_freq=5000,
)

META_LEARNING_TRAINING = TrainingConfig(
    timesteps=120_000,  # More timesteps for meta-learning
    tensorboard_log="logs/meta_learning",
    save_path="models/meta_learning_agent.zip",
    eval_freq=5000,
)

ENVIRONMENT = EnvironmentConfig()
DEMO = DemoConfig()

REWARD_WEIGHTS: Dict[str, Dict[str, float]] = {
    "qot_aware": {
        "allocation": 10.0,
        "qot": 3.5,
        "spectral_efficiency": 4.5,
        "fragmentation": 2.0,
        "load_balance": 1.5,
    },
    "delayed_assignment": {
        "allocation": 9.0,
        "qot": 3.0,
        "spectral_efficiency": 4.0,
        "fragmentation": 2.5,
        "load_balance": 2.2,
    },
    "bayesian_multi_objective": {
        "allocation": 11.0,
        "qot": 4.0,
        "spectral_efficiency": 4.5,
        "fragmentation": 2.5,
        "load_balance": 1.8,
    },
    "adaptive_curriculum": {
        "allocation": 8.5,
        "qot": 4.0,
        "spectral_efficiency": 6.0,
        "fragmentation": 2.0,
        "load_balance": 2.5,
    },
    "quantum_enhanced": {
        "allocation": 9.0,
        "qot": 3.5,
        "spectral_efficiency": 5.5,
        "fragmentation": 2.5,
        "load_balance": 2.0,
    },
}


# ---------------------------------------------------------------------------
# Battle Royale collections
# ---------------------------------------------------------------------------

BATTLE_AGENT_CONFIGS: Dict[str, AgentConfig] = {
    "CONTROL": DEFAULT_AGENT_CONFIG,
    "ULTHO": ULTHO_AGENT_CONFIG,
    "HYPERQ-OPT": HYPERQ_OPT_AGENT_CONFIG,
    "BOHAMIANN": BOHAMIANN_AGENT_CONFIG,
    "DEEPRMSA-QOT": DEEPRMSA_QOT_AGENT_CONFIG,
    "META-LEARNING": META_LEARNING_AGENT_CONFIG,
}

BATTLE_TRAINING_CONFIGS: Dict[str, TrainingConfig] = {
    "CONTROL": DEFAULT_TRAINING,
    "ULTHO": ULTHO_TRAINING,
    "HYPERQ-OPT": HYPERQ_OPT_TRAINING,
    "BOHAMIANN": BOHAMIANN_TRAINING,
    "DEEPRMSA-QOT": DEEPRMSA_QOT_TRAINING,
    "META-LEARNING": META_LEARNING_TRAINING,
}


# Backwards compatibility aliases (legacy scripts)
OPTIMIZED_AGENT_CONFIG = ULTHO_AGENT_CONFIG
DEEP_QOT_AGENT_CONFIG = DEEPRMSA_QOT_AGENT_CONFIG
ADAPTIVE_AGENT_CONFIG = HYPERQ_OPT_AGENT_CONFIG
SPECTRAL_AGENT_CONFIG = BOHAMIANN_AGENT_CONFIG
OPTIMIZED_TRAINING = ULTHO_TRAINING
DEEP_QOT_TRAINING = DEEPRMSA_QOT_TRAINING
ADAPTIVE_TRAINING = HYPERQ_OPT_TRAINING
SPECTRAL_TRAINING = BOHAMIANN_TRAINING
