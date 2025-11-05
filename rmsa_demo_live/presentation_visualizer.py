"""📊 Advanced Comparative Analysis - Generador de Gráficos para Presentaciones.

Genera múltiples visualizaciones comparativas de alta calidad para presentaciones:
- Box plots comparativos de métricas
- Heatmaps de correlación
- Radar charts de performance
- Violin plots de distribuciones
- Scatter plots 3D
- Time series comparisons
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from metrics_engine import BattleMetrics


class PresentationVisualizer:
    """Generador de visualizaciones para presentaciones."""
    
    def __init__(self, battle_metrics: BattleMetrics):
        self.battle_metrics = battle_metrics
        self.agents = list(battle_metrics.histories.keys())
        self.colors = {
            "CONTROL": "#3498db",
            "Default": "#3498db",
            "ULTHO": "#e74c3c",
            "HYPERQ-OPT": "#9b59b6",
            "BOHAMIANN": "#f39c12",
            "DEEPRMSA-QOT": "#1abc9c",
            "META-LEARNING": "#34495e",
        }
    
    def create_box_plot_comparison(self) -> go.Figure:
        """Box plots comparando todas las métricas clave."""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=(
                "Blocking Probability",
                "Spectral Efficiency",
                "Quality of Transmission",
                "Cumulative Reward",
                "Decision Latency",
                "Fragmentation",
            ),
        )
        
        metrics = [
            ("blocking_probability", 1, 1),
            ("spectral_efficiency", 1, 2),
            ("qot", 1, 3),
            ("cumulative_reward", 2, 1),
            ("decision_latency_ms", 2, 2),
            ("fragmentation", 2, 3),
        ]
        
        for metric_name, row, col in metrics:
            for agent_name in self.agents:
                history = self.battle_metrics.histories[agent_name]
                values = [getattr(rec, metric_name) for rec in history.records]
                
                fig.add_trace(
                    go.Box(
                        y=values,
                        name=agent_name,
                        marker_color=self.colors.get(agent_name, "#95a5a6"),
                        showlegend=(row == 1 and col == 1),
                    ),
                    row=row, col=col,
                )
        
        fig.update_layout(
            height=800,
            title_text="<b>Comparative Box Plot Analysis - All Agents</b>",
            title_font_size=20,
            showlegend=True,
        )
        
        return fig
    
    def create_radar_chart(self) -> go.Figure:
        """Radar chart comparando performance multidimensional."""
        fig = go.Figure()
        
        # Metrics to compare (normalized 0-1)
        metric_names = [
            "Blocking (inv)",
            "Spectral Eff",
            "QoT",
            "Reward",
            "Latency (inv)",
        ]
        
        for agent_name in self.agents:
            history = self.battle_metrics.histories[agent_name]
            
            # Calculate average metrics
            avg_blocking = history.mean_blocking()
            avg_spectral = history.mean_spectral_efficiency()
            avg_qot = history.mean_qot()
            avg_reward = history.mean_reward()
            avg_latency = history.mean_latency_ms()
            
            # Normalize (0-1, higher is better)
            values = [
                1.0 - min(avg_blocking, 1.0),  # Lower blocking is better
                min(avg_spectral, 1.0),
                min(avg_qot, 1.0),
                (avg_reward + 10) / 20,  # Assuming reward range [-10, 10]
                1.0 - min(avg_latency / 10.0, 1.0),  # Lower latency is better
            ]
            
            fig.add_trace(go.Scatterpolar(
                r=values + [values[0]],  # Close the polygon
                theta=metric_names + [metric_names[0]],
                fill='toself',
                name=agent_name,
                marker_color=self.colors.get(agent_name, "#95a5a6"),
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                ),
            ),
            title="<b>Multi-Dimensional Performance Radar</b>",
            title_font_size=20,
            height=600,
        )
        
        return fig
    
    def create_violin_plot(self) -> go.Figure:
        """Violin plots mostrando distribuciones de recompensa."""
        fig = go.Figure()
        
        for agent_name in self.agents:
            history = self.battle_metrics.histories[agent_name]
            rewards = [rec.cumulative_reward for rec in history.records]
            
            fig.add_trace(go.Violin(
                y=rewards,
                name=agent_name,
                box_visible=True,
                meanline_visible=True,
                fillcolor=self.colors.get(agent_name, "#95a5a6"),
                opacity=0.6,
                x0=agent_name,
            ))
        
        fig.update_layout(
            title="<b>Reward Distribution - Violin Plot</b>",
            title_font_size=20,
            yaxis_title="Cumulative Reward",
            xaxis_title="Agent",
            height=600,
        )
        
        return fig
    
    def create_correlation_heatmap(self) -> go.Figure:
        """Heatmap de correlación entre métricas para cada agente."""
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=self.agents,
            specs=[[{"type": "heatmap"} for _ in range(3)] for _ in range(2)],
        )
        
        positions = [(1, 1), (1, 2), (1, 3), (2, 1), (2, 2), (2, 3)]
        
        for idx, agent_name in enumerate(self.agents):
            if idx >= len(positions):
                break
            
            history = self.battle_metrics.histories[agent_name]
            
            # Build correlation matrix
            data = np.array([
                [rec.blocking_probability for rec in history.records],
                [rec.spectral_efficiency for rec in history.records],
                [rec.qot for rec in history.records],
                [rec.cumulative_reward for rec in history.records],
                [rec.decision_latency_ms for rec in history.records],
            ])
            
            corr_matrix = np.corrcoef(data)
            
            row, col = positions[idx]
            
            fig.add_trace(
                go.Heatmap(
                    z=corr_matrix,
                    x=["Blocking", "Spectral", "QoT", "Reward", "Latency"],
                    y=["Blocking", "Spectral", "QoT", "Reward", "Latency"],
                    colorscale="RdBu",
                    zmid=0,
                    showscale=(idx == 0),
                ),
                row=row, col=col,
            )
        
        fig.update_layout(
            title="<b>Metric Correlation Heatmaps - Per Agent</b>",
            title_font_size=20,
            height=800,
        )
        
        return fig
    
    def create_3d_scatter(self) -> go.Figure:
        """3D scatter plot: Blocking vs Spectral vs QoT."""
        fig = go.Figure()
        
        for agent_name in self.agents:
            history = self.battle_metrics.histories[agent_name]
            
            blocking = [rec.blocking_probability for rec in history.records]
            spectral = [rec.spectral_efficiency for rec in history.records]
            qot = [rec.qot for rec in history.records]
            
            fig.add_trace(go.Scatter3d(
                x=blocking,
                y=spectral,
                z=qot,
                mode='markers',
                name=agent_name,
                marker=dict(
                    size=4,
                    color=self.colors.get(agent_name, "#95a5a6"),
                    opacity=0.7,
                ),
            ))
        
        fig.update_layout(
            title="<b>3D Performance Space</b>",
            title_font_size=20,
            scene=dict(
                xaxis_title="Blocking Probability",
                yaxis_title="Spectral Efficiency",
                zaxis_title="Quality of Transmission",
            ),
            height=700,
        )
        
        return fig
    
    def create_time_series_comparison(self) -> go.Figure:
        """Time series comparando evolución de recompensa acumulada."""
        fig = go.Figure()
        
        for agent_name in self.agents:
            history = self.battle_metrics.histories[agent_name]
            
            episodes = [rec.episode for rec in history.records]
            rewards = [rec.cumulative_reward for rec in history.records]
            
            fig.add_trace(go.Scatter(
                x=episodes,
                y=rewards,
                mode='lines+markers',
                name=agent_name,
                line=dict(
                    color=self.colors.get(agent_name, "#95a5a6"),
                    width=2,
                ),
                marker=dict(size=4),
            ))
        
        fig.update_layout(
            title="<b>Cumulative Reward Evolution Over Episodes</b>",
            title_font_size=20,
            xaxis_title="Episode",
            yaxis_title="Cumulative Reward",
            height=600,
            hovermode='x unified',
        )
        
        return fig
    
    def create_performance_ranking_table(self) -> go.Figure:
        """Tabla de ranking final con todas las métricas."""
        # Calculate final metrics for each agent
        rows = []
        
        for agent_name in self.agents:
            history = self.battle_metrics.histories[agent_name]
            
            rows.append({
                "Agent": agent_name,
                "Avg Blocking": f"{history.mean_blocking():.3%}",
                "Avg Spectral": f"{history.mean_spectral_efficiency():.3%}",
                "Avg QoT": f"{history.mean_qot():.4f}",
                "Avg Reward": f"{history.mean_reward():+.2f}",
                "Avg Latency": f"{history.mean_latency_ms():.2f} ms",
                "Std Blocking": f"{history.std_blocking():.3%}",
            })
        
        # Sort by blocking (lower is better)
        rows.sort(key=lambda x: float(x["Avg Blocking"].strip('%')))
        
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(rows[0].keys()),
                fill_color='#3498db',
                font=dict(color='white', size=14),
                align='center',
            ),
            cells=dict(
                values=[[row[key] for row in rows] for key in rows[0].keys()],
                fill_color=[['#ecf0f1' if i % 2 == 0 else 'white' for i in range(len(rows))]],
                font=dict(size=12),
                align=['left'] + ['center'] * (len(rows[0]) - 1),
            ),
        )])
        
        fig.update_layout(
            title="<b>Final Performance Ranking - All Metrics</b>",
            title_font_size=20,
            height=400,
        )
        
        return fig
    
    def save_all_visualizations(self, output_dir: str = "presentation_viz") -> None:
        """Genera y guarda todas las visualizaciones."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        visualizations = [
            ("box_plot_comparison", self.create_box_plot_comparison),
            ("radar_chart", self.create_radar_chart),
            ("violin_plot", self.create_violin_plot),
            ("correlation_heatmap", self.create_correlation_heatmap),
            ("3d_scatter", self.create_3d_scatter),
            ("time_series", self.create_time_series_comparison),
            ("ranking_table", self.create_performance_ranking_table),
        ]
        
        for name, viz_func in visualizations:
            try:
                fig = viz_func()
                filepath = output_path / f"{name}.html"
                fig.write_html(str(filepath))
                print(f"✓ Saved {name}.html")
            except Exception as e:
                print(f"✗ Failed to create {name}: {e}")


def generate_presentation_visualizations(battle_metrics: BattleMetrics, output_dir: str = "presentation_viz") -> None:
    """Función de conveniencia para generar todas las visualizaciones."""
    viz = PresentationVisualizer(battle_metrics)
    viz.save_all_visualizations(output_dir)


if __name__ == "__main__":
    # Test with dummy data
    print("Presentation visualizer module loaded successfully!")
