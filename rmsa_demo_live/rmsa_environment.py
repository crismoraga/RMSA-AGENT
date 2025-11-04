"""RMSA Environment implementation for elastic optical networks."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional, Tuple

import gymnasium as gym
import networkx as nx
import numpy as np
from gymnasium import spaces


@dataclass
class ConnectionRequest:
    source: int
    destination: int
    bit_rate: float  # Gbps
    arrival_time: float
    holding_time: float


class NSFNETTopology:
    """NSFNET topology with 14 nodes and 21 links."""

    @staticmethod
    def create_graph() -> nx.Graph:
        G = nx.Graph()
        # NSFNET nodes
        nodes = list(range(14))
        G.add_nodes_from(nodes)

        # NSFNET links with distances (km)
        edges = [
            (0, 1, 1050), (0, 2, 1500), (0, 3, 2700),
            (1, 2, 600), (1, 7, 1000),
            (2, 5, 750),
            (3, 4, 600), (3, 11, 750),
            (4, 5, 600), (4, 6, 900),
            (5, 9, 900), (5, 12, 750),
            (6, 7, 600),
            (7, 8, 750),
            (8, 9, 750), (8, 10, 900),
            (9, 12, 600), (9, 13, 600),
            (10, 11, 600), (10, 12, 600),
            (11, 13, 300)
        ]

        for u, v, dist in edges:
            G.add_edge(u, v, distance=dist, weight=dist)

        return G


class RMSAEnv(gym.Env):
    """Routing, Modulation and Spectrum Assignment environment."""

    metadata = {"render_modes": ["human"]}

    def __init__(
        self,
        topology: str = "NSFNET",
        num_freq_slots: int = 196,
        episode_length: int = 100,
        load: float = 0.8,
        seed: Optional[int] = None,
        **kwargs
    ):
        super().__init__()

        self.episode_length = episode_length
        self.load = load
        self.num_freq_slots = num_freq_slots
        self.num_requests = 0
        self.current_request: Optional[ConnectionRequest] = None

        # Create network topology
        if topology == "NSFNET":
            self.graph = NSFNETTopology.create_graph()
        else:
            raise ValueError(f"Unknown topology: {topology}")

        self.num_nodes = self.graph.number_of_nodes()
        self.num_edges = self.graph.number_of_edges()

        # Spectrum state: [num_edges x num_freq_slots]
        self.spectrum_state = np.zeros((self.num_edges, num_freq_slots), dtype=np.int8)
        self.edge_list = list(self.graph.edges())

        # Statistics
        self.allocated = 0
        self.blocked = 0

        # Modulation formats and reach (km)
        self.modulations = {
            "BPSK": {"reach": 4000, "spectral_efficiency": 1},
            "QPSK": {"reach": 2000, "spectral_efficiency": 2},
            "8QAM": {"reach": 1000, "spectral_efficiency": 3},
            "16QAM": {"reach": 500, "spectral_efficiency": 4},
        }

        # Action space: k-shortest paths × modulation formats
        self.k_paths = 3
        self.num_modulations = len(self.modulations)
        action_space_size = self.k_paths * self.num_modulations
        self.action_space = spaces.Discrete(action_space_size)

        # Observation space
        obs_size = (
            self.num_nodes * 2  # source and destination one-hot
            + 1  # bit rate normalized
            + self.num_edges * self.num_freq_slots  # spectrum state
            + self.num_edges  # current link utilization
        )
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(obs_size,), dtype=np.float32
        )

        self.rng = np.random.default_rng(seed)

    def reset(
        self, seed: Optional[int] = None, options: Optional[Dict] = None
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        if seed is not None:
            self.rng = np.random.default_rng(seed)

        self.spectrum_state.fill(0)
        self.num_requests = 0
        self.allocated = 0
        self.blocked = 0
        self.current_request = self._generate_request()

        obs = self._get_observation()
        info = self._get_info()

        return obs, info

    def step(self, action: int) -> Tuple[np.ndarray, float, bool, bool, Dict[str, Any]]:
        path_idx = action // self.num_modulations
        mod_idx = action % self.num_modulations

        # Decode action
        paths = self._get_k_shortest_paths(
            self.current_request.source, self.current_request.destination
        )

        if path_idx >= len(paths):
            # Invalid path index
            allocated = False
            reward = -1.0
        else:
            path = paths[path_idx]
            modulation = list(self.modulations.keys())[mod_idx]
            allocated = self._try_allocate(path, modulation, self.current_request.bit_rate)
            reward = 1.0 if allocated else -1.0

        if allocated:
            self.allocated += 1
        else:
            self.blocked += 1

        self.num_requests += 1
        terminated = self.num_requests >= self.episode_length
        truncated = False

        # Generate next request
        if not terminated:
            self.current_request = self._generate_request()

        obs = self._get_observation()
        info = self._get_info(allocated=allocated, path=path if path_idx < len(paths) else None)

        return obs, reward, terminated, truncated, info

    def _generate_request(self) -> ConnectionRequest:
        """Generate a random connection request."""
        source = self.rng.integers(0, self.num_nodes)
        destination = self.rng.integers(0, self.num_nodes)
        while destination == source:
            destination = self.rng.integers(0, self.num_nodes)

        # Bit rates: 25, 50, 100, 200, 400 Gbps
        bit_rate = self.rng.choice([25, 50, 100, 200, 400])

        # Exponential arrival and holding times
        mean_holding = 1.0 / self.load
        holding_time = self.rng.exponential(mean_holding)
        arrival_time = self.rng.exponential(1.0)

        return ConnectionRequest(source, destination, bit_rate, arrival_time, holding_time)

    def _get_k_shortest_paths(self, source: int, dest: int) -> list:
        """Get k-shortest paths between source and destination."""
        try:
            paths = list(
                nx.shortest_simple_paths(self.graph, source, dest, weight="weight")
            )
            return paths[: self.k_paths]
        except nx.NetworkXNoPath:
            return []

    def _try_allocate(self, path: list, modulation: str, bit_rate: float) -> bool:
        """Try to allocate spectrum for the request."""
        # Check if path length is within modulation reach
        path_length = sum(
            self.graph[path[i]][path[i + 1]]["distance"] for i in range(len(path) - 1)
        )

        if path_length > self.modulations[modulation]["reach"]:
            return False

        # Calculate required slots
        spectral_efficiency = self.modulations[modulation]["spectral_efficiency"]
        required_slots = int(np.ceil(bit_rate / (12.5 * spectral_efficiency)))

        # Find first-fit slot
        slot = self._find_first_fit(path, required_slots)

        if slot is None:
            return False

        # Allocate spectrum
        for i in range(len(path) - 1):
            edge_idx = self._get_edge_index(path[i], path[i + 1])
            self.spectrum_state[edge_idx, slot : slot + required_slots] = 1

        return True

    def _find_first_fit(self, path: list, required_slots: int) -> Optional[int]:
        """Find first available slot block that fits on all edges of the path."""
        max_start = self.num_freq_slots - required_slots

        for start in range(max_start + 1):
            available = True
            for i in range(len(path) - 1):
                edge_idx = self._get_edge_index(path[i], path[i + 1])
                if np.any(self.spectrum_state[edge_idx, start : start + required_slots]):
                    available = False
                    break

            if available:
                return start

        return None

    def _get_edge_index(self, u: int, v: int) -> int:
        """Get edge index in edge list."""
        try:
            return self.edge_list.index((u, v))
        except ValueError:
            return self.edge_list.index((v, u))

    def _get_observation(self) -> np.ndarray:
        """Build observation vector."""
        obs_parts = []

        # Source one-hot
        source_onehot = np.zeros(self.num_nodes, dtype=np.float32)
        if self.current_request:
            source_onehot[self.current_request.source] = 1.0
        obs_parts.append(source_onehot)

        # Destination one-hot
        dest_onehot = np.zeros(self.num_nodes, dtype=np.float32)
        if self.current_request:
            dest_onehot[self.current_request.destination] = 1.0
        obs_parts.append(dest_onehot)

        # Bit rate normalized
        bit_rate_norm = np.array([self.current_request.bit_rate / 400.0], dtype=np.float32) if self.current_request else np.array([0.0])
        obs_parts.append(bit_rate_norm)

        # Spectrum state flattened
        spectrum_flat = self.spectrum_state.flatten().astype(np.float32)
        obs_parts.append(spectrum_flat)

        # Link utilization
        link_util = self.spectrum_state.mean(axis=1).astype(np.float32)
        obs_parts.append(link_util)

        return np.concatenate(obs_parts)

    def _get_info(self, allocated: bool = False, path: Optional[list] = None) -> Dict[str, Any]:
        """Build info dictionary."""
        blocking_prob = self.blocked / max(self.num_requests, 1)
        acceptance_rate = self.allocated / max(self.num_requests, 1)

        spectrum_util = self.spectrum_state.mean()
        fragmentation = self._calculate_fragmentation()

        info = {
            "allocation_success": allocated,
            "blocking_probability": blocking_prob,
            "acceptance_rate": acceptance_rate,
            "spectral_efficiency": spectrum_util,
            "fragmentation": fragmentation,
            "qot": 0.8 if allocated else 0.0,  # Simplified QoT
            "load_balance": 1.0 - self.spectrum_state.std(axis=0).mean(),
            "steps": self.num_requests,
            "connection_label": f"{self.current_request.source}→{self.current_request.destination} @ {self.current_request.bit_rate}Gbps" if self.current_request else "",
        }

        if path:
            info["path"] = "→".join(map(str, path))

        return info

    def _calculate_fragmentation(self) -> float:
        """Calculate spectrum fragmentation index."""
        if self.spectrum_state.sum() == 0:
            return 0.0

        # Simple fragmentation: count transitions in spectrum
        transitions = 0
        for edge_spectrum in self.spectrum_state:
            for i in range(len(edge_spectrum) - 1):
                if edge_spectrum[i] != edge_spectrum[i + 1]:
                    transitions += 1

        max_transitions = self.num_edges * (self.num_freq_slots - 1)
        return transitions / max(max_transitions, 1)

    def render(self):
        """Render environment (minimal implementation)."""
        print(f"Requests: {self.num_requests}/{self.episode_length}")
        print(f"Allocated: {self.allocated}, Blocked: {self.blocked}")
        print(f"Blocking probability: {self.blocked / max(self.num_requests, 1):.2%}")


# Register environment
gym.register(
    id="RMSA-v0",
    entry_point=f"{__name__}:RMSAEnv",
)
