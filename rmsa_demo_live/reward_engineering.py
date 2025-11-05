"""Módulo de Ingeniería de Recompensas Ultra-Avanzadas para el RMSA Battle Royale."""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, Protocol

import numpy as np


class UltraRewardFunction(Protocol):
    """Protocolo para todas las funciones de recompensa avanzadas."""
    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        ...


# --- 1. Binaria Simple (Control) ---
@dataclass(frozen=True)
class BinaryReward:
    """Recompensa simple: +1 por éxito, -1 por bloqueo."""
    success_bonus: float = 1.0
    block_penalty: float = -1.0

    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        return self.success_bonus if info.get("allocation_success", False) else self.block_penalty


# --- 2. Multi-Objetivo QoT-Aware ---
@dataclass(frozen=True)
class QoTAwareMultiObjectiveReward:
    """Recompensa compleja que balancea múltiples objetivos de red, con foco en QoT."""
    weights: Dict[str, float] = field(default_factory=lambda: {
        "allocation": 10.0,
        "qot": 3.0,
        "spectral_efficiency": 5.0,
        "fragmentation": -2.0,
        "load_balance": 1.5,
    })
    block_penalty: float = -5.0

    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", False):
            return self.block_penalty

        # R_QoT: Asumimos que info['qot'] es un valor normalizado (0-1) donde 1 es mejor.
        # La fórmula -exp(-OSNR/20) es difícil de aplicar sin OSNR directo.
        # Usamos una transformación exponencial sobre el QoT disponible para un efecto similar.
        qot_value = info.get("qot", 0.0)
        r_qot = math.exp(qot_value - 1) * self.weights["qot"]

        # R_efficiency: Recompensa la baja utilización (más espectro libre)
        # Asumimos que 'spectral_efficiency' en info es la utilización del espectro.
        spectrum_utilization = info.get("spectral_efficiency", 0.0)
        r_efficiency = (1.0 - spectrum_utilization) * self.weights["spectral_efficiency"]

        # R_fragmentation: Penaliza la fragmentación (entropía de Shannon)
        fragmentation = info.get("fragmentation", 0.0)
        r_fragmentation = fragmentation * self.weights["fragmentation"]

        # R_load_balance: Recompensa el balance de carga (baja varianza)
        load_variance = info.get("load_balance", 0.0)
        r_load_balance = (1.0 - load_variance) * self.weights["load_balance"]

        total_reward = (
            self.weights["allocation"] +
            r_qot +
            r_efficiency +
            r_fragmentation +
            r_load_balance
        )
        return total_reward


# --- 3. Delayed Assignment Temporal ---
@dataclass
class DelayedAssignmentReward:
    """Recompensa que considera el impacto futuro de una acción."""
    gamma: float = 0.95  # Factor de descuento para el impacto futuro
    beta: float = 0.5   # Peso del impacto en el estado de la red
    
    previous_fragmentation: float = 0.0
    previous_load_variance: float = 0.0

    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", False):
            self.previous_fragmentation = info.get("fragmentation", 0.0)
            self.previous_load_variance = info.get("load_balance", 0.0)
            return -1.0  # Penalización inmediata por bloqueo

        r_immediate = 1.0

        # R_future_fragmentation: Cambio en la fragmentación
        current_fragmentation = info.get("fragmentation", 0.0)
        delta_fragmentation = current_fragmentation - self.previous_fragmentation
        r_future_fragmentation = -delta_fragmentation  # Penaliza el aumento de fragmentación

        # R_network_state_impact: Cambio en el balance de carga
        current_load_variance = info.get("load_balance", 0.0)
        delta_load_variance = current_load_variance - self.previous_load_variance
        r_network_state_impact = -delta_load_variance # Penaliza el desbalanceo

        r_delayed = r_immediate + self.gamma * (r_future_fragmentation + self.beta * r_network_state_impact)

        # Actualizar estado para el siguiente paso
        self.previous_fragmentation = current_fragmentation
        self.previous_load_variance = current_load_variance

        return r_delayed


# --- 4. Adaptive Curriculum Reward ---
@dataclass
class AdaptiveCurriculumReward:
    """Recompensa que evoluciona, volviéndose más compleja a medida que el agente aprende."""
    total_episodes: int = 1000  # Total de episodios para el curriculum
    current_episode: int = 0

    def curriculum_weight(self) -> float:
        """El peso cambia de 0 a 1 a lo largo de los episodios."""
        return min(1.0, self.current_episode / (self.total_episodes * 0.75))

    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        if done:
            self.current_episode += 1

        if not info.get("allocation_success", False):
            return -1.0

        # Recompensa base simple
        r_base = 1.0

        # Bonus de exploración (proxy: penalización por acciones de baja probabilidad si se tuvieran)
        # Aquí, lo simulamos con un pequeño bonus aleatorio para incentivar la exploración.
        exploration_bonus = np.random.rand() * 0.1

        # Bonus de calidad (recompensa extra por usar modulaciones más eficientes)
        quality_bonus = info.get("modulation_level", 0) / 4.0 * 0.5

        # La recompensa compleja se introduce gradualmente
        r_complex = QoTAwareMultiObjectiveReward()(observation, action, reward, done, info)
        
        # Combinar recompensas según el curriculum
        weight = self.curriculum_weight()
        r_adaptive = (1 - weight) * (r_base + exploration_bonus + quality_bonus) + weight * r_complex
        
        return r_adaptive


# --- 5. Quantum-Enhanced Reward (Aproximación Clásica) ---
@dataclass(frozen=True)
class QuantumEnhancedReward:
    """
    Aproximación clásica a una recompensa de inspiración cuántica.
    - Superposición: Considera múltiples futuros posibles (rutas no elegidas).
    - Entrelazamiento: Mide qué tan acoplada está la decisión actual a la congestión de la red.
    """
    def __call__(self, observation: Any, action: Any, reward: float, done: bool, info: Dict) -> float:
        if not info.get("allocation_success", False):
            return -10.0 # Penalización fuerte

        # R_superposition: Recompensa por elegir una ruta que deja otras buenas rutas disponibles.
        # Proxy: Medimos la calidad de las rutas alternativas no tomadas.
        # Asumimos que `observation` contiene info de las k-rutas más cortas.
        # observation shape: (k_paths, num_freq_slots). 1 si está ocupado, 0 si libre.
        k_paths = observation.shape[0]
        # Contamos los slots libres en las rutas no elegidas
        chosen_path_idx = action // 4 # Asumiendo 4 modulaciones
        
        superposition_reward = 0
        for i in range(k_paths):
            if i != chosen_path_idx:
                free_slots = np.sum(1 - observation[i, :])
                superposition_reward += free_slots
        
        # Normalizar por el número de rutas y slots
        superposition_reward /= ((k_paths - 1) * observation.shape[1]) if k_paths > 1 else 1

        # R_entanglement: Penalización si la ruta elegida está muy congestionada (entrelazada con la congestión).
        chosen_path_congestion = np.mean(observation[chosen_path_idx, :])
        entanglement_penalty = -math.exp(chosen_path_congestion * 5) # Penalización exponencial a la congestión

        return 5.0 * superposition_reward + entanglement_penalty


# --- Fábrica de Funciones de Recompensa ---
def build_ultra_reward_function(reward_id: str, **kwargs) -> UltraRewardFunction:
    """Construye y devuelve una función de recompensa basada en su ID."""
    weights = kwargs.get("weights")
    if reward_id == "binary":
        return BinaryReward()
    if reward_id == "qot_aware":
        return QoTAwareMultiObjectiveReward(weights=weights or QoTAwareMultiObjectiveReward().weights)
    if reward_id == "delayed_assignment":
        return DelayedAssignmentReward()
    if reward_id == "adaptive_curriculum":
        return AdaptiveCurriculumReward(total_episodes=kwargs.get("total_episodes", 1000))
    if reward_id == "quantum_enhanced":
        return QuantumEnhancedReward()
    if reward_id == "bayesian_multi_objective":
        return QoTAwareMultiObjectiveReward(weights=weights or {
            "allocation": 12.0,
            "qot": 4.0,
            "spectral_efficiency": 4.0,
            "fragmentation": -2.5,
            "load_balance": 2.0,
        })

    raise ValueError(f"Unknown reward id: {reward_id}")
