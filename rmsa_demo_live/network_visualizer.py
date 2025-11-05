"""🌐 Network Topology Visualizer for RMSA Battle Royale.

Genera visualizaciones dinámicas de topologías de red con NetworkX y Plotly.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional, Tuple

import networkx as nx
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from rmsa_environment import (
    BRAZILTopology,
    EUROTopology,
    JAPANTopology,
    NSFNETTopology,
    UKNETTopology,
    USNETTopology,
)


class NetworkVisualizer:
    """Visualizador de topologías de red con NetworkX y Plotly."""
    
    TOPOLOGY_MAP = {
        "NSFNET": NSFNETTopology,
        "USNET": USNETTopology,
        "EURO": EUROTopology,
        "UKNET": UKNETTopology,
        "JAPAN": JAPANTopology,
        "BRAZIL": BRAZILTopology,
    }
    
    def __init__(self):
        self.graphs: Dict[str, nx.Graph] = {}
        self.positions: Dict[str, Dict] = {}
        self._build_graphs()
    
    def _build_graphs(self) -> None:
        """Construye grafos NetworkX para todas las topologías."""
        
        for name, topology_class in self.TOPOLOGY_MAP.items():
            # Get topology graph - support both create_graph() and build() methods
            if hasattr(topology_class, 'create_graph'):
                G = topology_class.create_graph()
            elif hasattr(topology_class, 'build'):
                G = topology_class.build()
            else:
                raise AttributeError(f"{topology_class.__name__} has neither create_graph() nor build() method")
            
            # Calculate layout (spring layout for aesthetic positioning)
            pos = nx.spring_layout(G, seed=42, k=2, iterations=50)
            
            self.graphs[name] = G
            self.positions[name] = pos
    
    def create_topology_figure(
        self,
        topology_name: str,
        highlight_nodes: Optional[List[int]] = None,
        highlight_edges: Optional[List[Tuple[int, int]]] = None,
        node_loads: Optional[Dict[int, float]] = None,
    ) -> go.Figure:
        """Crea visualización interactiva de una topología."""
        
        if topology_name not in self.graphs:
            raise ValueError(f"Unknown topology: {topology_name}")
        
        G = self.graphs[topology_name]
        pos = self.positions[topology_name]
        
        # Extract node positions
        node_x = [pos[node][0] for node in G.nodes()]
        node_y = [pos[node][1] for node in G.nodes()]
        
        # Edge traces
        edge_traces = []
        
        for edge in G.edges():
            x0, y0 = pos[edge[0]]
            x1, y1 = pos[edge[1]]
            
            # Check if this edge is highlighted
            is_highlighted = (
                highlight_edges and 
                (edge in highlight_edges or tuple(reversed(edge)) in highlight_edges)
            )
            
            edge_trace = go.Scatter(
                x=[x0, x1, None],
                y=[y0, y1, None],
                mode='lines',
                line=dict(
                    width=4 if is_highlighted else 1.5,
                    color='#e74c3c' if is_highlighted else '#bdc3c7',
                ),
                hoverinfo='none',
                showlegend=False,
            )
            edge_traces.append(edge_trace)
        
        # Node colors based on load
        if node_loads:
            node_colors = [node_loads.get(node, 0.0) for node in G.nodes()]
            colorscale = 'Viridis'
            showscale = True
        else:
            node_colors = ['#3498db'] * len(G.nodes())
            colorscale = None
            showscale = False
        
        # Node sizes based on degree centrality
        degree_cent = nx.degree_centrality(G)
        node_sizes = [20 + 30 * degree_cent[node] for node in G.nodes()]
        
        # Highlight specific nodes
        if highlight_nodes:
            node_colors = [
                '#e74c3c' if node in highlight_nodes else c
                for node, c in zip(G.nodes(), node_colors)
            ]
        
        # Node trace
        node_trace = go.Scatter(
            x=node_x,
            y=node_y,
            mode='markers+text',
            marker=dict(
                size=node_sizes,
                color=node_colors,
                colorscale=colorscale,
                showscale=showscale,
                line=dict(width=2, color='white'),
                colorbar=dict(
                    title="Node Load",
                    thickness=15,
                    len=0.5,
                ) if showscale else None,
            ),
            text=[f"Node {node}" for node in G.nodes()],
            textposition="top center",
            textfont=dict(size=10, color='#2c3e50'),
            hovertemplate='<b>Node %{text}</b><br>Connections: %{marker.size:.0f}<extra></extra>',
            showlegend=False,
        )
        
        # Create figure
        fig = go.Figure(data=edge_traces + [node_trace])
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"🌐 {topology_name} Topology<br><sub>{len(G.nodes())} nodes, {len(G.edges())} links</sub>",
                font=dict(size=18, color='#2c3e50'),
                x=0.5,
                xanchor='center',
            ),
            showlegend=False,
            hovermode='closest',
            margin=dict(b=0, l=0, r=0, t=60),
            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
            plot_bgcolor='white',
            height=600,
        )
        
        return fig
    
    def create_all_topologies_comparison(self) -> go.Figure:
        """Crea comparación visual de todas las topologías."""
        
        n_topologies = len(self.TOPOLOGY_MAP)
        rows = (n_topologies + 2) // 3  # 3 columns
        cols = 3
        
        fig = make_subplots(
            rows=rows,
            cols=cols,
            subplot_titles=list(self.TOPOLOGY_MAP.keys()),
            specs=[[{"type": "scatter"}] * cols for _ in range(rows)],
            vertical_spacing=0.08,
            horizontal_spacing=0.05,
        )
        
        for idx, (name, G) in enumerate(self.graphs.items()):
            row = idx // cols + 1
            col = idx % cols + 1
            
            pos = self.positions[name]
            
            # Edge traces
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                
                fig.add_trace(
                    go.Scatter(
                        x=[x0, x1, None],
                        y=[y0, y1, None],
                        mode='lines',
                        line=dict(width=1, color='#bdc3c7'),
                        hoverinfo='none',
                        showlegend=False,
                    ),
                    row=row, col=col
                )
            
            # Node trace
            node_x = [pos[node][0] for node in G.nodes()]
            node_y = [pos[node][1] for node in G.nodes()]
            
            fig.add_trace(
                go.Scatter(
                    x=node_x,
                    y=node_y,
                    mode='markers',
                    marker=dict(
                        size=8,
                        color='#3498db',
                        line=dict(width=1, color='white'),
                    ),
                    hoverinfo='skip',
                    showlegend=False,
                ),
                row=row, col=col
            )
            
            # Update axes for this subplot
            fig.update_xaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
            fig.update_yaxes(showgrid=False, zeroline=False, showticklabels=False, row=row, col=col)
        
        fig.update_layout(
            title=dict(
                text="🌍 Global Network Topologies Comparison",
                font=dict(size=22, color='#2c3e50'),
                x=0.5,
                xanchor='center',
            ),
            height=600 * rows,
            showlegend=False,
            plot_bgcolor='white',
        )
        
        return fig
    
    def create_network_statistics_table(self) -> go.Figure:
        """Crea tabla comparativa de estadísticas de red."""
        
        stats_data = []
        
        for name, G in self.graphs.items():
            # Calculate network statistics
            avg_degree = np.mean([d for _, d in G.degree()])
            diameter = nx.diameter(G) if nx.is_connected(G) else "N/A"
            avg_path_length = nx.average_shortest_path_length(G) if nx.is_connected(G) else "N/A"
            clustering = nx.average_clustering(G)
            
            stats_data.append({
                "Topology": name,
                "Nodes": len(G.nodes()),
                "Links": len(G.edges()),
                "Avg Degree": f"{avg_degree:.2f}",
                "Diameter": str(diameter),
                "Avg Path Length": f"{avg_path_length:.2f}" if avg_path_length != "N/A" else "N/A",
                "Clustering Coef": f"{clustering:.3f}",
            })
        
        # Create table
        header = list(stats_data[0].keys())
        cells = [[row[col] for row in stats_data] for col in header]
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[f"<b>{h}</b>" for h in header],
                fill_color='#3498db',
                font=dict(color='white', size=12),
                align='center',
            ),
            cells=dict(
                values=cells,
                fill_color=[['#ecf0f1', 'white'] * (len(stats_data) // 2 + 1)][:len(stats_data)],
                font=dict(size=11),
                align='center',
                height=30,
            )
        )])
        
        fig.update_layout(
            title=dict(
                text="📊 Network Topology Statistics",
                font=dict(size=18, color='#2c3e50'),
                x=0.5,
                xanchor='center',
            ),
            height=400,
        )
        
        return fig
    
    def save_all_visualizations(self, output_dir: str = "network_viz") -> None:
        """Guarda todas las visualizaciones como archivos HTML."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Individual topologies
        for name in self.TOPOLOGY_MAP.keys():
            fig = self.create_topology_figure(name)
            fig.write_html(str(output_path / f"{name.lower()}_topology.html"))
            print(f"✓ Saved {name} topology: {output_path / f'{name.lower()}_topology.html'}")
        
        # Comparison
        comparison = self.create_all_topologies_comparison()
        comparison.write_html(str(output_path / "all_topologies_comparison.html"))
        print(f"✓ Saved topologies comparison: {output_path / 'all_topologies_comparison.html'}")
        
        # Statistics table
        stats_table = self.create_network_statistics_table()
        stats_table.write_html(str(output_path / "topology_statistics.html"))
        print(f"✓ Saved statistics table: {output_path / 'topology_statistics.html'}")
        
        print(f"\n[✓] All network visualizations saved to {output_path}/")


if __name__ == "__main__":
    visualizer = NetworkVisualizer()
    visualizer.save_all_visualizations()
