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


class USNETTopology:
    """USNET topology with 24 nodes and 43 links (more complex)."""

    @staticmethod
    def create_graph() -> nx.Graph:
        G = nx.Graph()
        # USNET nodes (24 major US cities)
        nodes = list(range(24))
        G.add_nodes_from(nodes)

        # USNET links with realistic distances (km)
        edges = [
            # West Coast backbone
            (0, 1, 1100),  # Seattle-San Francisco
            (1, 2, 560),   # SF-LA
            (2, 3, 200),   # LA-San Diego
            
            # Central West
            (1, 4, 950),   # SF-Salt Lake City
            (4, 5, 830),   # SLC-Denver
            (5, 6, 650),   # Denver-Kansas City
            
            # South backbone
            (2, 7, 450),   # LA-Phoenix
            (7, 8, 1050),  # Phoenix-Dallas
            (8, 9, 400),   # Dallas-Houston
            (9, 10, 850),  # Houston-New Orleans
            
            # Midwest
            (6, 11, 500),  # KC-Chicago
            (11, 12, 450), # Chicago-Detroit
            (11, 13, 850), # Chicago-Minneapolis
            (6, 8, 700),   # KC-Dallas
            
            # East Coast backbone
            (14, 15, 340), # Boston-NYC
            (15, 16, 150), # NYC-Philadelphia
            (16, 17, 220), # Philly-DC
            (17, 18, 650), # DC-Atlanta
            (18, 10, 750), # Atlanta-New Orleans
            
            # Cross-country links
            (5, 11, 1450), # Denver-Chicago
            (11, 15, 1100),# Chicago-NYC
            (8, 18, 1200), # Dallas-Atlanta
            (18, 17, 650), # Atlanta-DC
            
            # Northern route
            (0, 13, 2400), # Seattle-Minneapolis
            (13, 12, 650), # Minneapolis-Detroit
            (12, 14, 1050),# Detroit-Boston
            
            # Southern route
            (3, 7, 550),   # SD-Phoenix
            (9, 19, 350),  # Houston-San Antonio
            (19, 8, 450),  # San Antonio-Dallas
            
            # Additional redundancy
            (0, 4, 1150),  # Seattle-SLC
            (4, 6, 950),   # SLC-KC
            (15, 17, 350), # NYC-DC
            (11, 14, 1100),# Chicago-Boston
            (12, 15, 800), # Detroit-NYC
            (13, 11, 550), # Minneapolis-Chicago
            
            # Western interconnects
            (1, 5, 1500),  # SF-Denver
            (2, 8, 1750),  # LA-Dallas
            
            # Eastern interconnects
            (14, 16, 450), # Boston-Philly
            (16, 18, 750), # Philly-Atlanta
            (17, 10, 1500),# DC-New Orleans
        ]

        for u, v, dist in edges:
            G.add_edge(u, v, distance=dist, weight=dist)

        return G


class EUROTopology:
    """European network topology with 19 nodes and 39 links."""

    @staticmethod
    def build() -> nx.Graph:
        G = nx.Graph()
        # 19 European cities
        nodes = [
            "London", "Paris", "Amsterdam", "Brussels", "Frankfurt", "Munich", "Zurich",
            "Milan", "Rome", "Madrid", "Barcelona", "Lisbon", "Copenhagen", "Stockholm",
            "Oslo", "Vienna", "Prague", "Warsaw", "Berlin"
        ]
        for i, city in enumerate(nodes):
            G.add_node(i, label=city)

        # Distances in km
        edges = [
            # Western Europe backbone
            (0, 1, 340),   # London-Paris
            (1, 2, 430),   # Paris-Amsterdam
            (2, 3, 170),   # Amsterdam-Brussels
            (3, 1, 260),   # Brussels-Paris
            
            # Central Europe
            (2, 18, 580),  # Amsterdam-Berlin
            (18, 4, 550),  # Berlin-Frankfurt
            (4, 5, 390),   # Frankfurt-Munich
            (5, 15, 350),  # Munich-Vienna
            (15, 16, 250), # Vienna-Prague
            (16, 18, 280), # Prague-Berlin
            
            # Southern Europe
            (6, 7, 240),   # Zurich-Milan
            (7, 8, 575),   # Milan-Rome
            (1, 9, 1050),  # Paris-Madrid
            (9, 10, 620),  # Madrid-Barcelona
            (10, 7, 720),  # Barcelona-Milan
            (9, 11, 500),  # Madrid-Lisbon
            
            # Northern Europe
            (2, 12, 620),  # Amsterdam-Copenhagen
            (12, 13, 520), # Copenhagen-Stockholm
            (13, 14, 530), # Stockholm-Oslo
            (14, 12, 480), # Oslo-Copenhagen
            
            # Cross-connections
            (0, 2, 360),   # London-Amsterdam
            (4, 6, 310),   # Frankfurt-Zurich
            (6, 5, 250),   # Zurich-Munich
            (4, 16, 400),  # Frankfurt-Prague
            (18, 17, 520), # Berlin-Warsaw
            (16, 17, 540), # Prague-Warsaw
            (12, 18, 360), # Copenhagen-Berlin
            (13, 17, 800), # Stockholm-Warsaw
            
            # UK-Europe links
            (0, 3, 320),   # London-Brussels
            (0, 4, 640),   # London-Frankfurt
            
            # Southern interconnects
            (1, 6, 490),   # Paris-Zurich
            (3, 4, 380),   # Brussels-Frankfurt
            (10, 1, 830),  # Barcelona-Paris
            (7, 15, 550),  # Milan-Vienna
            (8, 15, 760),  # Rome-Vienna
            
            # Additional redundancy
            (5, 18, 590),  # Munich-Berlin
            (4, 12, 680),  # Frankfurt-Copenhagen
        ]

        for u, v, dist in edges:
            G.add_edge(u, v, distance=dist, weight=dist)

        return G


class UKNETTopology:
    """UK national network with 21 nodes and 26 links."""

    @staticmethod
    def build() -> nx.Graph:
        G = nx.Graph()
        # 21 UK cities
        nodes = [
            "London", "Bristol", "Cardiff", "Birmingham", "Manchester", "Liverpool",
            "Leeds", "Sheffield", "Nottingham", "Leicester", "Cambridge", "Oxford",
            "Southampton", "Brighton", "Norwich", "Newcastle", "Edinburgh", "Glasgow",
            "Aberdeen", "Belfast", "Dublin"
        ]
        for i, city in enumerate(nodes):
            G.add_node(i, label=city)

        # Distances in km
        edges = [
            # Southern England
            (0, 1, 180),   # London-Bristol
            (0, 10, 80),   # London-Cambridge
            (0, 11, 90),   # London-Oxford
            (0, 12, 120),  # London-Southampton
            (0, 13, 85),   # London-Brighton
            (10, 14, 100), # Cambridge-Norwich
            
            # Midlands
            (1, 2, 70),    # Bristol-Cardiff
            (11, 3, 100),  # Oxford-Birmingham
            (3, 9, 65),    # Birmingham-Leicester
            (3, 4, 135),   # Birmingham-Manchester
            (4, 5, 55),    # Manchester-Liverpool
            (4, 6, 70),    # Manchester-Leeds
            (6, 7, 55),    # Leeds-Sheffield
            (7, 8, 60),    # Sheffield-Nottingham
            (8, 9, 45),    # Nottingham-Leicester
            
            # Northern England
            (6, 15, 145),  # Leeds-Newcastle
            (15, 16, 170), # Newcastle-Edinburgh
            (16, 17, 75),  # Edinburgh-Glasgow
            (17, 18, 195), # Glasgow-Aberdeen
            
            # Cross-country links
            (0, 3, 160),   # London-Birmingham
            (3, 6, 155),   # Birmingham-Leeds
            (9, 10, 140),  # Leicester-Cambridge
            (4, 15, 195),  # Manchester-Newcastle
            
            # Ireland connections
            (5, 19, 215),  # Liverpool-Belfast
            (19, 20, 165), # Belfast-Dublin
            (17, 19, 210), # Glasgow-Belfast
        ]

        for u, v, dist in edges:
            G.add_edge(u, v, distance=dist, weight=dist)

        return G


class JAPANTopology:
    """Japanese network topology with 12 nodes and 18 links."""

    @staticmethod
    def build() -> nx.Graph:
        G = nx.Graph()
        # 12 Japanese cities
        nodes = [
            "Tokyo", "Yokohama", "Osaka", "Kyoto", "Nagoya", "Sapporo",
            "Fukuoka", "Kobe", "Sendai", "Hiroshima", "Kitakyushu", "Okayama"
        ]
        for i, city in enumerate(nodes):
            G.add_node(i, label=city)

        # Distances in km
        edges = [
            # Main Honshu backbone
            (0, 1, 30),    # Tokyo-Yokohama
            (0, 4, 350),   # Tokyo-Nagoya
            (4, 3, 140),   # Nagoya-Kyoto
            (3, 2, 50),    # Kyoto-Osaka
            (2, 7, 30),    # Osaka-Kobe
            
            # Western Japan
            (7, 11, 160),  # Kobe-Okayama
            (11, 9, 160),  # Okayama-Hiroshima
            (9, 10, 110),  # Hiroshima-Kitakyushu
            (10, 6, 70),   # Kitakyushu-Fukuoka
            
            # Eastern Japan
            (0, 8, 350),   # Tokyo-Sendai
            (8, 5, 820),   # Sendai-Sapporo
            
            # Cross-connections
            (1, 4, 330),   # Yokohama-Nagoya
            (4, 2, 190),   # Nagoya-Osaka
            (3, 11, 190),  # Kyoto-Okayama
            (2, 9, 340),   # Osaka-Hiroshima
            (6, 2, 550),   # Fukuoka-Osaka
            
            # Northern route
            (0, 5, 1150),  # Tokyo-Sapporo (via ferry/tunnel)
            
            # Additional connections
            (1, 8, 330),   # Yokohama-Sendai
        ]

        for u, v, dist in edges:
            G.add_edge(u, v, distance=dist, weight=dist)

        return G


class BRAZILTopology:
    """Brazilian network topology with 19 nodes and 31 links."""

    @staticmethod
    def build() -> nx.Graph:
        G = nx.Graph()
        # 19 Brazilian cities
        nodes = [
            "Sao Paulo", "Rio de Janeiro", "Brasilia", "Salvador", "Fortaleza",
            "Belo Horizonte", "Manaus", "Curitiba", "Recife", "Porto Alegre",
            "Goiania", "Campinas", "Belem", "Vitoria", "Natal", "Campo Grande",
            "Florianopolis", "Santos", "Maceio"
        ]
        for i, city in enumerate(nodes):
            G.add_node(i, label=city)

        # Distances in km
        edges = [
            # Southeast backbone (economic heart)
            (0, 1, 430),   # SP-Rio
            (0, 11, 95),   # SP-Campinas
            (0, 17, 70),   # SP-Santos
            (0, 5, 585),   # SP-Belo Horizonte
            (5, 1, 440),   # BH-Rio
            (5, 13, 520),  # BH-Vitoria
            
            # Central Brazil
            (0, 2, 1015),  # SP-Brasilia
            (2, 5, 740),   # Brasilia-BH
            (2, 10, 210),  # Brasilia-Goiania
            (10, 15, 840), # Goiania-Campo Grande
            
            # Northeast backbone
            (3, 8, 840),   # Salvador-Recife
            (8, 18, 285),  # Recife-Maceio
            (18, 3, 630),  # Maceio-Salvador
            (8, 14, 290),  # Recife-Natal
            (14, 4, 535),  # Natal-Fortaleza
            
            # North region
            (4, 12, 1600), # Fortaleza-Belem
            (12, 6, 1290), # Belem-Manaus
            (2, 6, 2150),  # Brasilia-Manaus (long link)
            
            # South region
            (0, 7, 410),   # SP-Curitiba
            (7, 16, 300),  # Curitiba-Florianopolis
            (16, 9, 470),  # Florianopolis-Porto Alegre
            (7, 9, 710),   # Curitiba-Porto Alegre
            
            # Cross-country links
            (2, 3, 1060),  # Brasilia-Salvador
            (5, 3, 1370),  # BH-Salvador
            (10, 0, 910),  # Goiania-SP
            (15, 9, 1040), # Campo Grande-Porto Alegre
            (15, 7, 1010), # Campo Grande-Curitiba
            
            # Coastal connections
            (1, 13, 520),  # Rio-Vitoria
            (13, 3, 1200), # Vitoria-Salvador
            
            # Additional redundancy
            (11, 2, 920),  # Campinas-Brasilia
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
        elif topology == "USNET":
            self.graph = USNETTopology.create_graph()
        elif topology == "EURO":
            self.graph = EUROTopology.build()
        elif topology == "UKNET":
            self.graph = UKNETTopology.build()
        elif topology == "JAPAN":
            self.graph = JAPANTopology.build()
        elif topology == "BRAZIL":
            self.graph = BRAZILTopology.build()
        else:
            raise ValueError(f"Unknown topology: {topology}. Available: NSFNET, USNET, EURO, UKNET, JAPAN, BRAZIL")

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
