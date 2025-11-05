"""📊 Advanced Statistical Dashboard Generator for RMSA Battle Royale.

Genera visualizaciones interactivas Plotly con análisis estadístico profundo.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from scipy import stats

from metrics_engine import AgentHistory, BattleMetrics


class StatisticalDashboard:
    """Generador de dashboards estadísticos avanzados."""
    
    def __init__(self, battle_metrics: BattleMetrics):
        self.battle_metrics = battle_metrics
        self.colors = {
            "CONTROL": "#3498db",
            "ULTHO": "#2ecc71",
            "HYPERQ-OPT": "#9b59b6",
            "BOHAMIANN": "#e74c3c",
            "DEEPRMSA-QOT": "#1abc9c",
            "META-LEARNING": "#f39c12",
        }
    
    def create_comprehensive_dashboard(self) -> go.Figure:
        """Crea un dashboard comprehensivo con múltiples subplots."""
        
        fig = make_subplots(
            rows=3, cols=2,
            subplot_titles=(
                "📉 Blocking Probability Over Time",
                "📊 Spectral Efficiency Distribution",
                "🎯 QoT Performance",
                "⚡ Decision Latency Comparison",
                "🏆 Cumulative Reward Evolution",
                "📈 Performance Heatmap"
            ),
            specs=[
                [{"type": "scatter"}, {"type": "box"}],
                [{"type": "scatter"}, {"type": "bar"}],
                [{"type": "scatter"}, {"type": "heatmap"}],
            ],
            vertical_spacing=0.12,
            horizontal_spacing=0.10,
        )
        
        histories = self.battle_metrics.histories
        
        # 1. Blocking Probability Over Time
        for name, history in histories.items():
            episodes = [r.episode for r in history.records]
            blocking = [r.blocking_probability * 100 for r in history.records]
            
            fig.add_trace(
                go.Scatter(
                    x=episodes,
                    y=blocking,
                    mode='lines+markers',
                    name=name,
                    line=dict(color=self.colors.get(name, "#95a5a6"), width=2),
                    marker=dict(size=4),
                ),
                row=1, col=1
            )
        
        # 2. Spectral Efficiency Distribution (Box Plot)
        for name, history in histories.items():
            spectral = [r.spectral_efficiency * 100 for r in history.records]
            
            fig.add_trace(
                go.Box(
                    y=spectral,
                    name=name,
                    marker_color=self.colors.get(name, "#95a5a6"),
                    boxmean='sd',  # Show mean and standard deviation
                ),
                row=1, col=2
            )
        
        # 3. QoT Performance Over Time
        for name, history in histories.items():
            episodes = [r.episode for r in history.records]
            qot = [r.qot for r in history.records]
            
            fig.add_trace(
                go.Scatter(
                    x=episodes,
                    y=qot,
                    mode='lines',
                    name=name,
                    line=dict(color=self.colors.get(name, "#95a5a6"), width=2),
                    fill='tozeroy',
                    fillcolor=self.colors.get(name, "#95a5a6") + "33",  # 20% opacity
                ),
                row=2, col=1
            )
        
        # 4. Decision Latency Comparison (Bar Chart)
        names = []
        avg_latencies = []
        std_latencies = []
        
        for name, history in histories.items():
            latencies = [r.decision_latency_ms for r in history.records]
            names.append(name)
            avg_latencies.append(np.mean(latencies))
            std_latencies.append(np.std(latencies))
        
        fig.add_trace(
            go.Bar(
                x=names,
                y=avg_latencies,
                error_y=dict(type='data', array=std_latencies),
                marker_color=[self.colors.get(n, "#95a5a6") for n in names],
                text=[f"{lat:.2f}ms" for lat in avg_latencies],
                textposition='auto',
            ),
            row=2, col=2
        )
        
        # 5. Cumulative Reward Evolution
        for name, history in histories.items():
            episodes = [r.episode for r in history.records]
            rewards = [r.cumulative_reward for r in history.records]
            
            fig.add_trace(
                go.Scatter(
                    x=episodes,
                    y=rewards,
                    mode='lines',
                    name=name,
                    line=dict(color=self.colors.get(name, "#95a5a6"), width=3),
                ),
                row=3, col=1
            )
        
        # 6. Performance Heatmap
        metrics_names = ["Blocking", "Spectral Eff", "QoT", "Latency", "Reward"]
        agent_names = list(histories.keys())
        
        # Normalize metrics to [0, 1] for heatmap
        heatmap_data = []
        for name in agent_names:
            history = histories[name]
            row = [
                1.0 - np.mean([r.blocking_probability for r in history.records]),  # Lower is better -> invert
                np.mean([r.spectral_efficiency for r in history.records]),
                np.mean([r.qot for r in history.records]),
                1.0 - min(1.0, np.mean([r.decision_latency_ms for r in history.records]) / 10.0),  # Normalize and invert
                (np.mean([r.cumulative_reward for r in history.records]) + 100) / 200,  # Normalize [-100, 100] -> [0, 1]
            ]
            heatmap_data.append(row)
        
        fig.add_trace(
            go.Heatmap(
                z=heatmap_data,
                x=metrics_names,
                y=agent_names,
                colorscale='RdYlGn',
                text=[[f"{val:.2f}" for val in row] for row in heatmap_data],
                texttemplate='%{text}',
                textfont={"size": 10},
                colorbar=dict(title="Performance"),
            ),
            row=3, col=2
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="Episode", row=1, col=1)
        fig.update_yaxes(title_text="Blocking Probability (%)", row=1, col=1)
        
        fig.update_yaxes(title_text="Spectral Efficiency (%)", row=1, col=2)
        
        fig.update_xaxes(title_text="Episode", row=2, col=1)
        fig.update_yaxes(title_text="QoT", row=2, col=1)
        
        fig.update_xaxes(title_text="Agent", row=2, col=2)
        fig.update_yaxes(title_text="Avg Latency (ms)", row=2, col=2)
        
        fig.update_xaxes(title_text="Episode", row=3, col=1)
        fig.update_yaxes(title_text="Cumulative Reward", row=3, col=1)
        
        # Update layout
        fig.update_layout(
            title=dict(
                text="🏆 RMSA Battle Royale - Comprehensive Statistical Analysis",
                font=dict(size=24, color="#2c3e50"),
                x=0.5,
                xanchor='center',
            ),
            height=1400,
            showlegend=True,
            template="plotly_white",
            font=dict(family="Arial, sans-serif", size=11),
            hovermode='x unified',
        )
        
        return fig
    
    def create_statistical_tests_report(self) -> go.Figure:
        """Genera reporte de tests estadísticos (ANOVA, t-tests)."""
        
        histories = self.battle_metrics.histories
        agent_names = list(histories.keys())
        
        # Prepare data for ANOVA
        blocking_data = {name: [r.blocking_probability for r in h.records] for name, h in histories.items()}
        reward_data = {name: [r.cumulative_reward for r in h.records] for name, h in histories.items()}
        
        # Perform ANOVA on blocking probability
        anova_blocking = stats.f_oneway(*blocking_data.values())
        
        # Perform ANOVA on cumulative reward
        anova_reward = stats.f_oneway(*reward_data.values())
        
        # Pairwise t-tests for blocking probability
        n_agents = len(agent_names)
        pvalue_matrix_blocking = np.zeros((n_agents, n_agents))
        
        for i, name1 in enumerate(agent_names):
            for j, name2 in enumerate(agent_names):
                if i != j:
                    _, pval = stats.ttest_ind(blocking_data[name1], blocking_data[name2])
                    pvalue_matrix_blocking[i, j] = pval
                else:
                    pvalue_matrix_blocking[i, j] = 1.0
        
        # Create figure with statistical tests
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=(
                f"Pairwise t-test P-values (Blocking)<br>ANOVA: F={anova_blocking.statistic:.2f}, p={anova_blocking.pvalue:.4f}",
                f"Pairwise t-test P-values (Reward)<br>ANOVA: F={anova_reward.statistic:.2f}, p={anova_reward.pvalue:.4f}",
            ),
            specs=[[{"type": "heatmap"}, {"type": "heatmap"}]],
            horizontal_spacing=0.15,
        )
        
        # Blocking probability p-values heatmap
        fig.add_trace(
            go.Heatmap(
                z=pvalue_matrix_blocking,
                x=agent_names,
                y=agent_names,
                colorscale='RdYlGn_r',  # Reversed: red = significant, green = not significant
                zmid=0.05,  # Significance threshold
                text=[[f"{val:.4f}" for val in row] for row in pvalue_matrix_blocking],
                texttemplate='%{text}',
                textfont={"size": 9},
                colorbar=dict(title="P-value", x=0.45),
            ),
            row=1, col=1
        )
        
        # Reward p-values heatmap
        pvalue_matrix_reward = np.zeros((n_agents, n_agents))
        for i, name1 in enumerate(agent_names):
            for j, name2 in enumerate(agent_names):
                if i != j:
                    _, pval = stats.ttest_ind(reward_data[name1], reward_data[name2])
                    pvalue_matrix_reward[i, j] = pval
                else:
                    pvalue_matrix_reward[i, j] = 1.0
        
        fig.add_trace(
            go.Heatmap(
                z=pvalue_matrix_reward,
                x=agent_names,
                y=agent_names,
                colorscale='RdYlGn_r',
                zmid=0.05,
                text=[[f"{val:.4f}" for val in row] for row in pvalue_matrix_reward],
                texttemplate='%{text}',
                textfont={"size": 9},
                colorbar=dict(title="P-value", x=1.0),
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=dict(
                text="📊 Statistical Significance Tests (α=0.05)",
                font=dict(size=20, color="#2c3e50"),
                x=0.5,
                xanchor='center',
            ),
            height=600,
            template="plotly_white",
        )
        
        return fig
    
    def save_all_dashboards(self, output_dir: str = "dashboards") -> None:
        """Guarda todos los dashboards como archivos HTML interactivos."""
        
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Main comprehensive dashboard
        comprehensive = self.create_comprehensive_dashboard()
        comprehensive.write_html(str(output_path / "comprehensive_analysis.html"))
        print(f"✓ Saved comprehensive dashboard: {output_path / 'comprehensive_analysis.html'}")
        
        # Statistical tests report
        statistical = self.create_statistical_tests_report()
        statistical.write_html(str(output_path / "statistical_tests.html"))
        print(f"✓ Saved statistical tests: {output_path / 'statistical_tests.html'}")
        
        print(f"\n[✓] All dashboards saved to {output_path}/")


def generate_dashboards_from_battle(battle_metrics: BattleMetrics, output_dir: str = "dashboards") -> None:
    """Función de conveniencia para generar todos los dashboards."""
    dashboard = StatisticalDashboard(battle_metrics)
    dashboard.save_all_dashboards(output_dir)


if __name__ == "__main__":
    # Example usage (requires running demo_orchestrator.py first)
    from demo_orchestrator import DemoOrchestrator
    
    orchestrator = DemoOrchestrator(
        agents_to_load=["CONTROL", "ULTHO"],
        episodes=50,
    )
    
    battle_metrics = orchestrator.run()
    generate_dashboards_from_battle(battle_metrics)
