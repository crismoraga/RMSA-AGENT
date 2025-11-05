"""Topology management utilities for the RMSA Battle Royale demo."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Iterable, Iterator, List, Optional

from environment import EnvironmentFactory
from rmsa_environment import (
    BRAZILTopology,
    EUROTopology,
    JAPANTopology,
    NSFNETTopology,
    RMSAEnv,
    UKNETTopology,
    USNETTopology,
)


@dataclass(frozen=True)
class TopologyDescriptor:
    """Metadata describing an optical network topology."""

    name: str
    nodes: int
    links: int
    diameter: Optional[int]
    description: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "name": self.name,
            "nodes": str(self.nodes),
            "links": str(self.links),
            "diameter": "N/A" if self.diameter is None else str(self.diameter),
            "description": self.description,
        }


class TopologyManager:
    """Central registry and helper for switching RMSA topologies on the fly."""

    _DESCRIPTORS: Dict[str, TopologyDescriptor] = {
        "NSFNET": TopologyDescriptor(
            name="NSFNET",
            nodes=14,
            links=21,
            diameter=None,
            description="Red académica clásica de Estados Unidos",
        ),
        "USNET": TopologyDescriptor(
            name="USNET",
            nodes=24,
            links=43,
            diameter=None,
            description="Red comercial estadounidense a gran escala",
        ),
        "EURO": TopologyDescriptor(
            name="EURO",
            nodes=19,
            links=39,
            diameter=None,
            description="Topología paneuropea extendida",
        ),
        "UKNET": TopologyDescriptor(
            name="UKNET",
            nodes=21,
            links=26,
            diameter=None,
            description="Red nacional del Reino Unido",
        ),
        "JAPAN": TopologyDescriptor(
            name="JAPAN",
            nodes=12,
            links=18,
            diameter=None,
            description="Red óptica compacta japonesa",
        ),
        "BRAZIL": TopologyDescriptor(
            name="BRAZIL",
            nodes=19,
            links=31,
            diameter=None,
            description="Infraestructura óptica de América Latina",
        ),
    }

    _TOPOLOGY_CLASSES = {
        "NSFNET": NSFNETTopology,
        "USNET": USNETTopology,
        "EURO": EUROTopology,
        "UKNET": UKNETTopology,
        "JAPAN": JAPANTopology,
        "BRAZIL": BRAZILTopology,
    }

    def __init__(self, base_kwargs: Optional[Dict[str, object]] = None) -> None:
        self._base_kwargs = base_kwargs or {}
        self._sequence = list(self._DESCRIPTORS.keys())
        self._index = 0

    # ------------------------------------------------------------------
    # Introspection helpers
    # ------------------------------------------------------------------
    @classmethod
    def available_names(cls) -> List[str]:
        return list(cls._DESCRIPTORS.keys())

    @classmethod
    def descriptor(cls, name: str) -> TopologyDescriptor:
        try:
            return cls._DESCRIPTORS[name]
        except KeyError as exc:  # pragma: no cover - guard
            raise ValueError(f"Unknown topology: {name}") from exc

    @classmethod
    def iter_descriptors(cls) -> Iterator[TopologyDescriptor]:
        for name in cls.available_names():
            yield cls.descriptor(name)

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------
    def _build_base_kwargs(self, topology: str) -> Dict[str, object]:
        kwargs = dict(self._base_kwargs)
        kwargs.update({"topology": topology})
        return kwargs

    def make_factory(self, topology: str) -> EnvironmentFactory:
        """Produce an :class:`EnvironmentFactory` pre-configured for ``topology``."""

        kwargs = self._build_base_kwargs(topology)
        return EnvironmentFactory(base_kwargs=kwargs)

    def make_env(self, topology: str, **kwargs) -> RMSAEnv:
        """Instantiate the RMSA environment for ``topology`` immediately."""

        factory = self.make_factory(topology)
        env = factory.make(seed=kwargs.get("seed"))
        return env

    # ------------------------------------------------------------------
    # Rotation helpers
    # ------------------------------------------------------------------
    def cycle(self, step: int = 1) -> TopologyDescriptor:
        """Advance the internal pointer and return the next topology descriptor."""

        self._index = (self._index + step) % len(self._sequence)
        return self.descriptor(self._sequence[self._index])

    def current(self) -> TopologyDescriptor:
        return self.descriptor(self._sequence[self._index])

    def reset(self, topology: Optional[str] = None) -> TopologyDescriptor:
        if topology is None:
            self._index = 0
        else:
            if topology not in self._sequence:
                raise ValueError(f"Unknown topology: {topology}")
            self._index = self._sequence.index(topology)
        return self.current()


def build_default_topology_manager() -> TopologyManager:
    """Create a :class:`TopologyManager` using default environment settings."""

    from config import ENVIRONMENT  # Lazy import to avoid cycles

    return TopologyManager(base_kwargs=ENVIRONMENT.as_dict())


__all__ = [
    "TopologyDescriptor",
    "TopologyManager",
    "build_default_topology_manager",
]
