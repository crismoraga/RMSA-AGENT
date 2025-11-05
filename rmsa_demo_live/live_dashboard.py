"""🔴 LIVE DASHBOARD - Visualización Dinámica en Tiempo Real.

Dashboard web que se actualiza automáticamente mostrando:
- Gráficos dinámicos (line charts, pie charts, bar charts, radar charts)
- Métricas en vivo de todos los agentes
- Comparaciones en tiempo real
- Actualización cada 1 segundo

Uso:
    python rmsa_demo_live/live_dashboard.py
    
Luego abre: http://localhost:8050
"""
from __future__ import annotations

import json
import time
from pathlib import Path
from threading import Thread
from typing import Dict, List

import numpy as np
import plotly.graph_objects as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
from plotly.subplots import make_subplots


class LiveDashboard:
    """Dashboard en vivo con auto-actualización."""
    
    def __init__(self, data_file: str = "live_battle_data.json"):
        self.data_file = Path(data_file)
        self.app = Dash(__name__, update_title=None)
        self.setup_layout()
        self.setup_callbacks()
        
    def setup_layout(self):
        """Configura el layout del dashboard."""
        self.app.layout = html.Div([
            html.H1("🔴 RMSA BATTLE ROYALE - LIVE DASHBOARD", 
                   style={'textAlign': 'center', 'color': '#FF4444'}),
            
            html.Div([
                html.H3(id='live-status', style={'textAlign': 'center'}),
            ]),
            
            # Intervalo de actualización (1 segundo)
            dcc.Interval(
                id='interval-component',
                interval=1000,  # milliseconds
                n_intervals=0
            ),
            
            # Row 1: Métricas principales
            html.Div([
                html.Div([
                    dcc.Graph(id='live-rewards'),
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='live-blocking'),
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            # Row 2: Pie charts y distribuciones
            html.Div([
                html.Div([
                    dcc.Graph(id='blocking-pie'),
                ], style={'width': '33%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='spectral-bar'),
                ], style={'width': '33%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='qot-gauge'),
                ], style={'width': '33%', 'display': 'inline-block'}),
            ]),
            
            # Row 3: Comparaciones avanzadas
            html.Div([
                html.Div([
                    dcc.Graph(id='radar-comparison'),
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='ranking-bars'),
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            # Row 4: Latencia y nuevas métricas
            html.Div([
                html.Div([
                    dcc.Graph(id='latency-comparison'),
                ], style={'width': '50%', 'display': 'inline-block'}),
                
                html.Div([
                    dcc.Graph(id='performance-heatmap'),
                ], style={'width': '50%', 'display': 'inline-block'}),
            ]),
            
            # Row 5: Time series completo
            html.Div([
                dcc.Graph(id='all-metrics-time'),
            ]),
        ], style={'backgroundColor': '#1a1a1a', 'padding': '20px'})
    
    def setup_callbacks(self):
        """Configura las callbacks de actualización."""
        
        @self.app.callback(
            [Output('live-status', 'children'),
             Output('live-rewards', 'figure'),
             Output('live-blocking', 'figure'),
             Output('blocking-pie', 'figure'),
             Output('spectral-bar', 'figure'),
             Output('qot-gauge', 'figure'),
             Output('radar-comparison', 'figure'),
             Output('ranking-bars', 'figure'),
             Output('latency-comparison', 'figure'),
             Output('performance-heatmap', 'figure'),
             Output('all-metrics-time', 'figure')],
            [Input('interval-component', 'n_intervals')]
        )
        def update_graphs(n):
            # Leer datos del archivo JSON
            data = self.load_data()
            
            if not data or 'agents' not in data or len(data['agents']) == 0:
                # Datos vacíos - mostrar placeholders
                return self._empty_state()
            
            # Generar todos los gráficos
            status = self._create_status(data)
            rewards_fig = self._create_rewards_chart(data)
            blocking_fig = self._create_blocking_chart(data)
            pie_fig = self._create_blocking_pie(data)
            bar_fig = self._create_spectral_bar(data)
            gauge_fig = self._create_qot_gauge(data)
            radar_fig = self._create_radar_comparison(data)
            ranking_fig = self._create_ranking_bars(data)
            latency_fig = self._create_latency_comparison(data)
            heatmap_fig = self._create_performance_heatmap(data)
            timeseries_fig = self._create_all_metrics_time(data)
            
            return (status, rewards_fig, blocking_fig, pie_fig, bar_fig, 
                   gauge_fig, radar_fig, ranking_fig, latency_fig, heatmap_fig, timeseries_fig)
    
    def load_data(self) -> Dict:
        """Carga datos del archivo JSON con manejo robusto de errores."""
        if not self.data_file.exists():
            # Archivo no existe todavía - crear uno vacío
            initial_data = {
                "current_episode": 0,
                "total_episodes": 0,
                "agents": {}
            }
            try:
                with open(self.data_file, 'w') as f:
                    json.dump(initial_data, f, indent=2)
            except Exception:
                pass
            return initial_data
        
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Validar estructura
                if not isinstance(data, dict):
                    return {"current_episode": 0, "total_episodes": 0, "agents": {}}
                if 'agents' not in data:
                    data['agents'] = {}
                return data
        except json.JSONDecodeError:
            # JSON corrupto - intentar recuperar
            return {"current_episode": 0, "total_episodes": 0, "agents": {}}
        except Exception as e:
            print(f"⚠️  Error leyendo datos: {e}")
            return {"current_episode": 0, "total_episodes": 0, "agents": {}}
    
    def _empty_state(self):
        """Estado cuando no hay datos."""
        empty_fig = go.Figure()
        empty_fig.update_layout(
            template='plotly_dark',
            title='Esperando datos...',
            xaxis={'visible': False},
            yaxis={'visible': False}
        )
        return ("⏳ Esperando inicio de batalla...", 
               empty_fig, empty_fig, empty_fig, empty_fig, 
               empty_fig, empty_fig, empty_fig, empty_fig, empty_fig, empty_fig)
    
    def _create_status(self, data: Dict) -> str:
        """Crea el texto de estado."""
        episode = data.get('current_episode', 0)
        total = data.get('total_episodes', 0)
        progress = (episode / total * 100) if total > 0 else 0
        return f"📊 Episodio: {episode}/{total} ({progress:.1f}%)"
    
    def _create_rewards_chart(self, data: Dict) -> go.Figure:
        """Gráfico de rewards en tiempo real."""
        fig = go.Figure()
        
        for agent_name, agent_data in data.get('agents', {}).items():
            episodes = agent_data.get('episodes', [])
            rewards = agent_data.get('rewards', [])
            
            fig.add_trace(go.Scatter(
                x=episodes,
                y=rewards,
                mode='lines+markers',
                name=agent_name,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            template='plotly_dark',
            title='🎯 Reward Evolution (Live)',
            xaxis_title='Episode',
            yaxis_title='Average Reward',
            hovermode='x unified',
            legend=dict(orientation='h', y=1.1)
        )
        
        return fig
    
    def _create_blocking_chart(self, data: Dict) -> go.Figure:
        """Gráfico de blocking probability."""
        fig = go.Figure()
        
        for agent_name, agent_data in data.get('agents', {}).items():
            episodes = agent_data.get('episodes', [])
            blocking = agent_data.get('blocking', [])
            
            fig.add_trace(go.Scatter(
                x=episodes,
                y=blocking,
                mode='lines+markers',
                name=agent_name,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            template='plotly_dark',
            title='🚫 Blocking Probability (Live)',
            xaxis_title='Episode',
            yaxis_title='Blocking %',
            hovermode='x unified',
            legend=dict(orientation='h', y=1.1)
        )
        
        return fig
    
    def _create_blocking_pie(self, data: Dict) -> go.Figure:
        """Pie chart de blocking actual."""
        agents = []
        blocking_vals = []
        
        for agent_name, agent_data in data.get('agents', {}).items():
            blocking_list = agent_data.get('blocking', [])
            if blocking_list:
                agents.append(agent_name)
                blocking_vals.append(blocking_list[-1])
        
        fig = go.Figure(data=[go.Pie(
            labels=agents,
            values=blocking_vals,
            hole=0.4,
            marker=dict(line=dict(color='#000000', width=2))
        )])
        
        fig.update_layout(
            template='plotly_dark',
            title='📊 Current Blocking Distribution'
        )
        
        return fig
    
    def _create_spectral_bar(self, data: Dict) -> go.Figure:
        """Barras de eficiencia espectral."""
        agents = []
        spectral_vals = []
        
        for agent_name, agent_data in data.get('agents', {}).items():
            spectral_list = agent_data.get('spectral_efficiency', [])
            if spectral_list:
                agents.append(agent_name)
                spectral_vals.append(spectral_list[-1])
        
        fig = go.Figure(data=[go.Bar(
            x=agents,
            y=spectral_vals,
            marker=dict(
                color=spectral_vals,
                colorscale='Viridis',
                showscale=True
            )
        )])
        
        fig.update_layout(
            template='plotly_dark',
            title='📡 Spectral Efficiency (Current)',
            yaxis_title='Efficiency %'
        )
        
        return fig
    
    def _create_qot_gauge(self, data: Dict) -> go.Figure:
        """Gauge de QoT promedio."""
        qot_values = []
        
        for agent_data in data.get('agents', {}).values():
            qot_list = agent_data.get('qot', [])
            if qot_list:
                qot_values.append(qot_list[-1])
        
        avg_qot = sum(qot_values) / len(qot_values) if qot_values else 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=avg_qot * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Average QoT"},
            delta={'reference': 95},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 80], 'color': "lightgray"},
                    {'range': [80, 95], 'color': "gray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 95
                }
            }
        ))
        
        fig.update_layout(
            template='plotly_dark',
            height=300
        )
        
        return fig
    
    def _create_radar_comparison(self, data: Dict) -> go.Figure:
        """Radar chart comparativo."""
        fig = go.Figure()
        
        categories = ['Reward', 'Spectral', 'QoT', 'Low Blocking', 'Latency']
        
        for agent_name, agent_data in data.get('agents', {}).items():
            if not agent_data.get('rewards'):
                continue
                
            # Normalizar métricas a 0-1
            reward = agent_data['rewards'][-1] if agent_data.get('rewards') else 0
            spectral = agent_data['spectral_efficiency'][-1] / 100 if agent_data.get('spectral_efficiency') else 0
            qot = agent_data['qot'][-1] if agent_data.get('qot') else 0
            blocking_inv = 1 - (agent_data['blocking'][-1] / 100) if agent_data.get('blocking') else 0
            latency_inv = 0.5  # Placeholder
            
            values = [reward, spectral, qot, blocking_inv, latency_inv]
            
            fig.add_trace(go.Scatterpolar(
                r=values,
                theta=categories,
                fill='toself',
                name=agent_name
            ))
        
        fig.update_layout(
            template='plotly_dark',
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            title='🌐 Multi-Metric Radar (Current)'
        )
        
        return fig
    
    def _create_ranking_bars(self, data: Dict) -> go.Figure:
        """Barras de ranking actual."""
        agents = []
        scores = []
        
        for agent_name, agent_data in data.get('agents', {}).items():
            if not agent_data.get('rewards'):
                continue
            
            # Calcular score compuesto
            reward = agent_data['rewards'][-1] if agent_data.get('rewards') else 0
            spectral = agent_data['spectral_efficiency'][-1] if agent_data.get('spectral_efficiency') else 0
            qot = agent_data['qot'][-1] * 100 if agent_data.get('qot') else 0
            blocking = agent_data['blocking'][-1] if agent_data.get('blocking') else 0
            
            score = (reward * 100) + (spectral * 50) + (qot * 30) - (blocking * 200)
            
            agents.append(agent_name)
            scores.append(score)
        
        # Ordenar por score
        sorted_data = sorted(zip(agents, scores), key=lambda x: x[1], reverse=True)
        agents, scores = zip(*sorted_data) if sorted_data else ([], [])
        
        colors = ['gold' if i == 0 else 'silver' if i == 1 else 'peru' if i == 2 
                 else 'steelblue' for i in range(len(agents))]
        
        fig = go.Figure(data=[go.Bar(
            x=list(agents),
            y=list(scores),
            marker=dict(color=colors)
        )])
        
        fig.update_layout(
            template='plotly_dark',
            title='🏆 Current Ranking (Composite Score)',
            yaxis_title='Score'
        )
        
        return fig
    
    def _create_all_metrics_time(self, data: Dict) -> go.Figure:
        """Serie temporal de todas las métricas."""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Rewards', 'Blocking %', 'Spectral Efficiency', 'QoT'),
            specs=[[{}, {}], [{}, {}]]
        )
        
        for agent_name, agent_data in data.get('agents', {}).items():
            episodes = agent_data.get('episodes', [])
            
            # Rewards
            fig.add_trace(go.Scatter(
                x=episodes, y=agent_data.get('rewards', []),
                mode='lines', name=agent_name, showlegend=False
            ), row=1, col=1)
            
            # Blocking
            fig.add_trace(go.Scatter(
                x=episodes, y=agent_data.get('blocking', []),
                mode='lines', name=agent_name, showlegend=False
            ), row=1, col=2)
            
            # Spectral
            fig.add_trace(go.Scatter(
                x=episodes, y=agent_data.get('spectral_efficiency', []),
                mode='lines', name=agent_name, showlegend=False
            ), row=2, col=1)
            
            # QoT
            qot_percentage = [q * 100 for q in agent_data.get('qot', [])]
            fig.add_trace(go.Scatter(
                x=episodes, y=qot_percentage,
                mode='lines', name=agent_name, showlegend=True
            ), row=2, col=2)
        
        fig.update_layout(
            template='plotly_dark',
            height=600,
            title_text="📈 All Metrics Time Series",
            showlegend=True,
            legend=dict(orientation='h', y=-0.15)
        )
        
        return fig
    
    def _create_latency_comparison(self, data: Dict) -> go.Figure:
        """Crea un gráfico de comparación de latencias de decisión."""
        fig = go.Figure()
        
        agents = data.get('agents', {})
        
        for agent_name, agent_data in agents.items():
            latencies = agent_data.get('latency', [])
            if latencies:
                episodes = agent_data.get('episodes', list(range(len(latencies))))
                
                # Línea de latencia
                fig.add_trace(go.Scatter(
                    x=episodes,
                    y=latencies,
                    mode='lines+markers',
                    name=agent_name,
                    line=dict(width=2),
                    marker=dict(size=4)
                ))
        
        fig.update_layout(
            template='plotly_dark',
            title='⚡ Decision Latency Comparison (ms)',
            xaxis_title='Episode',
            yaxis_title='Latency (ms)',
            hovermode='x unified',
            height=400
        )
        
        return fig
    
    def _create_performance_heatmap(self, data: Dict) -> go.Figure:
        """Crea un heatmap de performance de todos los agentes."""
        import numpy as np
        
        agents = data.get('agents', {})
        
        if not agents:
            fig = go.Figure()
            fig.update_layout(template='plotly_dark', title='No data yet')
            return fig
        
        # Preparar datos para heatmap
        agent_names = list(agents.keys())
        metrics = ['Reward', 'Spectral Eff', 'QoT', 'Blocking', 'Latency']
        
        # Matriz de valores (normalizada 0-100)
        heatmap_data = []
        
        for metric in metrics:
            row = []
            for agent_name in agent_names:
                agent_data = agents[agent_name]
                
                if metric == 'Reward':
                    values = agent_data.get('rewards', [0])
                    # Normalizar a 0-100 (assuming -1 to 1 range)
                    val = (np.mean(values) + 1) * 50 if values else 0
                elif metric == 'Spectral Eff':
                    values = agent_data.get('spectral_efficiency', [0])
                    val = np.mean(values) if values else 0
                elif metric == 'QoT':
                    values = agent_data.get('qot', [0])
                    val = np.mean(values) * 100 if values else 0
                elif metric == 'Blocking':
                    values = agent_data.get('blocking', [0])
                    # Invertir (lower is better)
                    val = 100 - np.mean(values) if values else 100
                elif metric == 'Latency':
                    values = agent_data.get('latency', [0])
                    # Invertir y normalizar (lower is better)
                    max_latency = 5.0  # Assuming max 5ms
                    val = max(0, 100 - (np.mean(values) / max_latency * 100)) if values else 0
                
                row.append(val)
            heatmap_data.append(row)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=agent_names,
            y=metrics,
            colorscale='Viridis',
            text=np.round(heatmap_data, 1),
            texttemplate='%{text}',
            textfont={"size": 12},
            colorbar=dict(title="Score")
        ))
        
        fig.update_layout(
            template='plotly_dark',
            title='Performance Heatmap (Higher = Better)',
            xaxis_title='Agent',
            yaxis_title='Metric',
            height=400
        )
        
        return fig
    
    def run(self, debug: bool = False, port: int = 8050):
        """Ejecuta el servidor del dashboard."""
        print(f"\n{'='*80}")
        print(f"LIVE DASHBOARD - INICIANDO SERVIDOR")
        print(f"{'='*80}\n")
        
        try:
            # Crear archivo inicial si no existe
            if not self.data_file.exists():
                print(f"Creando archivo de datos inicial: {self.data_file}")
                self.load_data()  # Esto creará el archivo vacío
            
            print(f"URL: http://localhost:{port}")
            print(f"Actualizacion automatica cada 1 segundo")
            print(f"Mostrando 11 visualizaciones en tiempo real")
            print(f"\nPresiona Ctrl+C para detener el servidor")
            print(f"{'='*80}\n")
            
            # Iniciar servidor (bloqueante)
            self.app.run_server(debug=debug, port=port, host='0.0.0.0', dev_tools_silence_routes_logging=True)
            
        except OSError as e:
            if "address already in use" in str(e).lower():
                print(f"\nERROR: Puerto {port} ya esta en uso")
                print(f"Solucion: Cierra otras aplicaciones que usen el puerto {port}")
            else:
                print(f"\nERROR al iniciar servidor: {e}")
            raise
        except Exception as e:
            print(f"\nERROR INESPERADO: {e}")
            raise


def main():
    """Punto de entrada principal."""
    try:
        dashboard = LiveDashboard()
        dashboard.run(debug=False, port=8050)
    except KeyboardInterrupt:
        print("\n\nDashboard detenido correctamente")
    except Exception as e:
        print(f"\n\nError fatal: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
