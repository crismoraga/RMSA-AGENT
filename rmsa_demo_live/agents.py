"""PPO agent builders used in the RMSA demo."""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Tuple

import torch
import torch.nn as nn
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import EvalCallback
from stable_baselines3.common.torch_layers import MlpExtractor
from stable_baselines3.common.vec_env import DummyVecEnv
from stable_baselines3.ppo.policies import MlpPolicy

from config import AgentConfig, TrainingConfig
from environment import EnvironmentFactory, make_training_env
from reward_functions import RewardFunction


ACTIVATIONS: Dict[str, nn.Module] = {
    "relu": nn.ReLU,
    "tanh": nn.Tanh,
    "leaky_relu": nn.LeakyReLU,
    "elu": nn.ELU,
    "silu": nn.SiLU,
    "gelu": nn.GELU,
}


class DropoutMlpExtractor(MlpExtractor):
    def __init__(
        self,
        feature_dim: int,
        net_arch,
        activation_fn: nn.Module,
        dropout: float,
        device: torch.device,
    ) -> None:
        super().__init__(feature_dim, net_arch, activation_fn, device=device)
        self.policy_net = self._insert_dropout(self.policy_net, dropout)
        self.value_net = self._insert_dropout(self.value_net, dropout)

    @staticmethod
    def _insert_dropout(sequential: nn.Sequential, dropout: float) -> nn.Sequential:
        if dropout <= 0:
            return sequential
        layers = []
        for layer in sequential:
            layers.append(layer)
            if isinstance(layer, (nn.ReLU, nn.Tanh, nn.ELU, nn.SiLU, nn.LeakyReLU)):
                layers.append(nn.Dropout(p=dropout))
        return nn.Sequential(*layers)


class DropoutMlpPolicy(MlpPolicy):
    def __init__(self, *args, dropout: float = 0.1, **kwargs) -> None:
        self._dropout = dropout
        super().__init__(*args, **kwargs)

    def _build_mlp_extractor(self) -> None:
        self.mlp_extractor = DropoutMlpExtractor(
            self.features_dim,
            net_arch=self.net_arch,
            activation_fn=self.activation_fn,
            dropout=self._dropout,
            device=self.device,
        )


@dataclass
class AgentBuilder:
    config: AgentConfig
    factory: EnvironmentFactory
    reward_fn: RewardFunction

    def _policy_and_kwargs(self) -> Tuple[type, Dict]:
        activation = ACTIVATIONS.get(self.config.activation.lower())
        if activation is None:
            raise ValueError(f"Unsupported activation {self.config.activation}")

        policy_kwargs: Dict = {
            "net_arch": list(self.config.net_arch),
            "activation_fn": activation,
        }

        policy_class: type
        if self.config.dropout > 0:
            policy_class = DropoutMlpPolicy
            policy_kwargs["dropout"] = self.config.dropout
        else:
            policy_class = MlpPolicy

        return policy_class, policy_kwargs

    def build(self, seed: int) -> PPO:
        policy_class, policy_kwargs = self._policy_and_kwargs()

        def _make_env():
            return make_training_env(self.factory, self.reward_fn, seed=seed)

        vec_env = DummyVecEnv([_make_env])
        model = PPO(
            policy_class,
            vec_env,
            learning_rate=self.config.learning_rate,
            gamma=self.config.gamma,
            batch_size=self.config.batch_size,
            n_steps=self.config.n_steps,
            ent_coef=self.config.ent_coef,
            vf_coef=self.config.vf_coef,
            max_grad_norm=self.config.max_grad_norm,
            policy_kwargs=policy_kwargs,
            **self.config.extra_kwargs,
        )
        return model


def train_agent(
    builder: AgentBuilder,
    training: TrainingConfig,
    seed: int,
) -> PPO:
    Path(training.tensorboard_log).mkdir(parents=True, exist_ok=True)
    Path(training.save_path).parent.mkdir(parents=True, exist_ok=True)

    model = builder.build(seed)

    eval_env = DummyVecEnv(
        [lambda: make_training_env(builder.factory, builder.reward_fn, seed=seed + 1)]
    )
    eval_callback = EvalCallback(
        eval_env,
        eval_freq=training.eval_freq,
        deterministic=True,
        render=False,
        n_eval_episodes=5,
    )

    model.learn(
        total_timesteps=training.timesteps,
        callback=eval_callback,
        progress_bar=True,
        tb_log_name=f"{builder.config.name}_ppo",
    )
    model.save(training.save_path)
    return model
