"""🔥 EXTREME BATTLE CONFIGURATION - Topología Difícil para Battle Royale.

Configuración ultra-difícil para separar verdaderamente a los mejores agentes:
- Topología USNET (24 nodos, 43 enlaces) - más compleja que NSFNET
- Carga muy alta (0.95) para forzar bloqueos
- Menor espectro disponible (100 slots vs 196) para forzar fragmentación
- Episodios más largos (200 pasos) para acumular estrés
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict


@dataclass(frozen=True)
class ExtremeEnvironmentConfig:
    """Configuración de ambiente extremadamente difícil.
    
    ⚠️ USA NSFNET para compatibilidad con modelos entrenados,
       pero con parámetros EXTREMOS para dificultad máxima.
    """
    topology: str = "NSFNET"  # 14 nodos - COMPATIBLE con modelos entrenados
    frequency_slots: int = 80  # REDUCIDO 59% de 196 (espectro muy limitado)
    load: float = 0.95  # AUMENTADO +19% de 0.8 (carga extrema)
    episode_length: int = 300  # AUMENTADO +200% de 100 (episodios muy largos)
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
class ExtremeDemoConfig:
    """Configuración de demo extrema."""
    demo_requests: int = 2000  # AUMENTADO de 200 (más peticiones para probar)
    refresh_hz: float = 20.0  # Más rápido para demo fluida
    fairness_seed: int = 31415


# Configuraciones para batalla extrema
EXTREME_ENVIRONMENT = ExtremeEnvironmentConfig()
EXTREME_DEMO = ExtremeDemoConfig()


def get_extreme_battle_description() -> str:
    """Retorna descripción de la configuración extrema."""
    return f"""
🔥 EXTREME BATTLE CONFIGURATION ACTIVE 🔥

Topology: {EXTREME_ENVIRONMENT.topology} (14 nodes, 21 links) - COMPATIBLE
Spectrum: {EXTREME_ENVIRONMENT.frequency_slots} slots (REDUCED -59% from 196)
Traffic Load: {EXTREME_ENVIRONMENT.load * 100:.0f}% (EXTREME HIGH +19%)
Episode Length: {EXTREME_ENVIRONMENT.episode_length} steps (ULTRA LONG +200%)
Demo Requests: {EXTREME_DEMO.demo_requests} (EXTENSIVE EVALUATION)

⚠️ This configuration will SEVERELY challenge all agents.
   Uses NSFNET for compatibility but with EXTREME difficulty parameters!
"""


if __name__ == "__main__":
    print(get_extreme_battle_description())
