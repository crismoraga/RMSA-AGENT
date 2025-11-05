# 🔴 LIVE DASHBOARD - Visualización Dinámica en Tiempo Real

## 📊 Descripción

Dashboard web interactivo que muestra **9 visualizaciones dinámicas** actualizándose automáticamente cada segundo durante el Battle Royale.

### ✨ Características

- **⚡ Actualización en Tiempo Real**: Los gráficos se refrescan cada 1 segundo
- **📊 9 Visualizaciones Simultáneas**:
  1. **Rewards Evolution** - Line chart de rewards por episodio
  2. **Blocking Probability** - Line chart de blocking % por episodio
  3. **Blocking Distribution** - Pie chart del blocking actual
  4. **Spectral Efficiency** - Bar chart de eficiencia espectral
  5. **QoT Gauge** - Gauge chart de calidad de transmisión
  6. **Radar Comparison** - Radar chart multidimensional
  7. **Current Ranking** - Barras con ranking actual (score compuesto)
  8. **All Metrics Time Series** - 4 subplots con todas las métricas
  9. **Status Banner** - Progreso actual del battle

- **🎨 Diseño Oscuro Profesional**: Template Plotly Dark optimizado
- **📱 Responsive**: Se adapta a diferentes tamaños de pantalla

---

## 🚀 Uso Rápido

### Opción 1: Launcher Automático (RECOMENDADO)

```powershell
# Inicia dashboard + battle royale automáticamente
python rmsa_demo_live/launch_with_dashboard.py

# Modo EXTREME con dashboard
python rmsa_demo_live/launch_with_dashboard.py --extreme

# Custom episodes con dashboard
python rmsa_demo_live/launch_with_dashboard.py --episodes 500
```

**Esto hará:**
1. ✅ Inicia el servidor del dashboard en http://localhost:8050
2. ✅ Abre automáticamente el navegador
3. ✅ Ejecuta el Battle Royale en la terminal
4. ✅ Actualiza gráficos en tiempo real cada segundo
5. ✅ Al finalizar, detiene el servidor automáticamente

---

### Opción 2: Manual (2 Terminales)

**Terminal 1 - Servidor Dashboard:**
```powershell
python rmsa_demo_live/live_dashboard.py
```

**Terminal 2 - Battle Royale:**
```powershell
python rmsa_demo_live/demo_orchestrator.py --episodes 200
```

**Navegador:**
```
http://localhost:8050
```

---

## 📊 Visualizaciones Incluidas

### 1. **Rewards Evolution** (Top Left)
Line chart mostrando la evolución de rewards de cada agente a lo largo de los episodios.
- **Eje X**: Episodios
- **Eje Y**: Average Reward
- **Colores**: Un color por agente

### 2. **Blocking Probability** (Top Right)
Line chart de la probabilidad de bloqueo (blocking %) de cada agente.
- **Eje X**: Episodios
- **Eje Y**: Blocking %
- **Objetivo**: Valores más bajos = mejor

### 3. **Blocking Distribution** (Middle Left)
Pie chart mostrando la distribución actual del blocking entre agentes.
- **Formato**: Donut chart (con agujero central)
- **Valores**: Blocking % actual de cada agente

### 4. **Spectral Efficiency** (Middle Center)
Bar chart de la eficiencia espectral actual de cada agente.
- **Colores**: Gradiente Viridis (verde-azul-morado)
- **Valores**: Eficiencia espectral en %

### 5. **QoT Gauge** (Middle Right)
Gauge (velocímetro) mostrando la calidad de transmisión promedio.
- **Rango**: 0-100%
- **Zonas**:
  - 0-80%: Gris claro (baja calidad)
  - 80-95%: Gris (calidad aceptable)
  - 95-100%: Zona verde (calidad óptima)
- **Referencia**: Línea roja en 95%

### 6. **Radar Comparison** (Bottom Left)
Radar chart comparando 5 métricas simultáneamente:
- **Reward**: Recompensa normalizada
- **Spectral**: Eficiencia espectral
- **QoT**: Calidad de transmisión
- **Low Blocking**: Inversa del blocking (1 - blocking)
- **Latency**: Latencia normalizada

### 7. **Current Ranking** (Bottom Right)
Bar chart horizontal con el ranking actual basado en score compuesto.
- **Fórmula**: `(reward×100) + (spectral×50) + (qot×30) - (blocking×200)`
- **Colores**:
  - 🥇 Oro (1er lugar)
  - 🥈 Plata (2do lugar)
  - 🥉 Bronce (3er lugar)
  - 🔵 Azul acero (resto)

### 8. **All Metrics Time Series** (Bottom Full Width)
Grid 2×2 con 4 subplots mostrando la evolución de todas las métricas:
- **Top-Left**: Rewards
- **Top-Right**: Blocking %
- **Bottom-Left**: Spectral Efficiency
- **Bottom-Right**: QoT

### 9. **Status Banner** (Top Center)
Banner mostrando el progreso actual:
- **Formato**: `📊 Episodio: X/Y (Z.Z%)`
- **Actualización**: Cada segundo

---

## 🔧 Tecnologías

- **Dash 2.14+**: Framework web de Plotly para dashboards interactivos
- **Plotly 5.17+**: Biblioteca de visualización interactiva
- **Python 3.12**: Lenguaje de programación
- **JSON**: Formato de intercambio de datos

---

## 📁 Archivos Generados

- **`live_battle_data.json`**: Datos en tiempo real compartidos entre procesos
  - Actualizado cada episodio por `demo_orchestrator.py`
  - Leído cada segundo por `live_dashboard.py`

---

## ⚙️ Configuración Avanzada

### Cambiar Puerto del Dashboard

Edita `live_dashboard.py`:

```python
if __name__ == "__main__":
    dashboard = LiveDashboard()
    dashboard.run(debug=False, port=9000)  # Cambiar 8050 → 9000
```

### Cambiar Frecuencia de Actualización

Edita `live_dashboard.py` línea 48:

```python
dcc.Interval(
    id='interval-component',
    interval=500,  # Cambiar 1000ms → 500ms (actualiza cada 0.5s)
    n_intervals=0
),
```

### Personalizar Colores

Edita los templates de Plotly en cada método `_create_*`:

```python
fig.update_layout(
    template='plotly_dark',  # Cambiar a 'plotly', 'ggplot2', 'seaborn', etc.
    ...
)
```

---

## 🐛 Troubleshooting

### Dashboard no carga datos

**Síntoma**: Dashboard muestra "Esperando datos..." permanentemente

**Solución**:
1. Verifica que `demo_orchestrator.py` esté ejecutándose
2. Confirma que existe `live_battle_data.json` en el directorio raíz
3. Revisa permisos de escritura en el directorio

### Puerto 8050 ya en uso

**Síntoma**: Error `Address already in use`

**Solución**:
```powershell
# Opción 1: Detener proceso existente
netstat -ano | findstr :8050
taskkill /PID <PID> /F

# Opción 2: Cambiar puerto (ver Configuración Avanzada)
```

### Gráficos no se actualizan

**Síntoma**: Gráficos estáticos, no cambian

**Solución**:
1. Verifica que `demo_orchestrator.py` esté llamando a `_write_live_data()`
2. Revisa la consola del navegador (F12) para errores JavaScript
3. Reinicia el servidor del dashboard

---

## 📊 Ejemplo de Uso

```powershell
# Terminal única (launcher automático)
PS C:\Users\Cris\Desktop\Taller3> python rmsa_demo_live/launch_with_dashboard.py --extreme

╔═══════════════════════════════════════════════════════════════════════╗
║         🚀 RMSA BATTLE ROYALE + LIVE DASHBOARD LAUNCHER 🚀           ║
╚═══════════════════════════════════════════════════════════════════════╝

⚙️  Configuración:
  • Modo: EXTREME (NSFNET, 80 slots, 95% load, 300 steps)
  • Episodios: 2000

═══════════════════════════════════════════════════════════════════════

🔴 Iniciando Live Dashboard Server...
✓ Dashboard server iniciado en http://localhost:8050
🌐 Abriendo dashboard en navegador...
✓ Dashboard abierto en navegador

⚔️  Iniciando Battle Royale...

[Terminal muestra Rich UI con scoreboard dinámico]
[Navegador muestra 9 gráficos actualizándose cada segundo]
```

---

## 🎯 Métricas Monitoreadas

| Métrica | Descripción | Rango | Mejor |
|---------|-------------|-------|-------|
| **Reward** | Recompensa acumulada promedio | -∞ a +∞ | Mayor |
| **Blocking %** | Probabilidad de bloqueo | 0-100% | Menor |
| **Spectral Efficiency** | Eficiencia en uso del espectro | 0-100% | Mayor |
| **QoT** | Quality of Transmission | 0-1 | Mayor (>0.95) |
| **Latency** | Latencia promedio | 0-∞ ms | Menor |
| **Composite Score** | Score multi-objetivo | -∞ a +∞ | Mayor |

**Fórmula del Composite Score:**
```
Score = (Reward × 100) + (Spectral × 50) + (QoT × 30) - (Blocking × 200)
```

---

## 🚀 Próximas Mejoras

- [ ] WebSocket para actualizaciones más eficientes (vs polling)
- [ ] Exportar dashboards a PNG/PDF
- [ ] Comparación histórica entre runs
- [ ] Alertas cuando un agente falla
- [ ] Predicción de ganador en tiempo real
- [ ] Modo replay de batallas pasadas

---

## 📜 Licencia

MIT License - Ver archivo LICENSE en el directorio raíz.

---

## 🙏 Créditos

Desarrollado como parte del **RMSA Battle Royale Ultra-Vanguardista**.

Dashboard creado con ❤️ usando Plotly Dash.
