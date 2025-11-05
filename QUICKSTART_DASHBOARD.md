# ⚡ QUICKSTART - Dashboard Live + Battle Royale

## 🚀 Inicio Ultra-Rápido (1 Comando)

### Opción 1: Modo EXTREME con Dashboard (RECOMENDADO)

```powershell
python rmsa_demo_live/launch_with_dashboard.py --extreme
```

**Esto hace:**

- ✅ Verifica que el puerto 8050 esté disponible
- ✅ Crea archivo de datos inicial `live_battle_data.json`
- ✅ Inicia servidor web en <http://localhost:8050>
- ✅ Abre automáticamente el dashboard en tu navegador
- ✅ Ejecuta Battle Royale de 2000 episodios en NSFNET
- ✅ Actualiza 11 gráficos cada segundo en tiempo real

**Duración:** 10-15 minutos  
**Visualizaciones:** 11 gráficos dinámicos simultáneos

---

### Opción 2: Modo Normal con Dashboard

```powershell
python rmsa_demo_live/launch_with_dashboard.py --episodes 200
```

**Duración:** 3-5 minutos  
**Ideal para:** Testing rápido

---

## 📊 ¿Qué Verás en el Dashboard?

### 11 Visualizaciones en Tiempo Real

1. **📈 Rewards Evolution** - Line chart de recompensas acumuladas
2. **🚫 Blocking Probability** - Probabilidad de bloqueo por episodio
3. **🍩 Blocking Distribution** - Donut chart de distribución actual
4. **📊 Spectral Efficiency** - Bar chart con gradiente Viridis
5. **🎯 QoT Gauge** - Velocímetro de calidad de transmisión
6. **🕸️ Radar Comparison** - 5D radar (reward, spectral, qot, blocking, latency)
7. **🏆 Current Ranking** - Ranking horizontal con score compuesto
8. **⚡ Latency Comparison** - Comparación de latencias de decisión (NEW!)
9. **🔥 Performance Heatmap** - Heatmap de métricas normalizadas (NEW!)
10. **📊 All Metrics Time Series** - Grid 2x2 con todas las métricas
11. **📢 Status Banner** - Progreso actual (episodio X/Total)

---

## 🔧 Solución de Problemas

### Error: "ERR_CONNECTION_REFUSED"

**Causa:** El servidor del dashboard no pudo iniciarse.

**Soluciones:**

1. **Verificar dependencias:**

```powershell
pip install dash plotly numpy
```

2. **Ejecutar dashboard manualmente para ver errores:**

```powershell
python rmsa_demo_live/live_dashboard.py
```

3. **El launcher ahora verifica automáticamente:**
   - Puerto 8050 disponible
   - Crea `live_battle_data.json` si no existe
   - Muestra errores detallados si falla el inicio

---

### Error: "Address already in use"

**Solución:**

```powershell
# Cerrar proceso que usa puerto 8050
# En Windows PowerShell:
netstat -ano | findstr :8050
# Tomar el PID y:
taskkill /PID <PID> /F
```

---

### Dashboard abre pero no muestra datos

**Causa:** Battle Royale no se está ejecutando o no escribe JSON.

**Verificar:**

1. Que el terminal muestre el progreso del battle
2. Que exista `live_battle_data.json` en la carpeta raíz
3. Que el archivo JSON se actualice (ver última modificación)

**Solución rápida:**

```powershell
# Detener todo (Ctrl+C)
# Borrar archivo viejo
Remove-Item live_battle_data.json -ErrorAction SilentlyContinue
# Re-ejecutar launcher
python rmsa_demo_live/launch_with_dashboard.py --extreme
```

---

## 💡 Tips de Uso

### Ver solo el dashboard (sin battle)

```powershell
python rmsa_demo_live/live_dashboard.py
```

Útil para:

- Testing de visualizaciones
- Debugging
- Ver datos de una ejecución previa

---

### Ejecutar solo el battle (sin dashboard)

```powershell
python rmsa_demo_live/demo_orchestrator.py --extreme
```

Útil para:

- Ejecutar múltiples battles en paralelo
- Análisis estadístico posterior
- Cuando no necesitas visualización en vivo

---

## 🎨 Personalización

### Cambiar puerto del dashboard

Editar `live_dashboard.py` línea ~571:

```python
dashboard.run(debug=False, port=9000)  # Cambiar de 8050 a 9000
```

### Cambiar intervalo de actualización

Editar `live_dashboard.py` línea ~50:

```python
interval=2000,  # Cambiar de 1000ms (1s) a 2000ms (2s)
```

### Agregar más visualizaciones

Ver `live_dashboard.py` métodos `_create_*` para ejemplos de:

- Line charts
- Pie charts
- Bar charts
- Radar charts
- Gauge charts
- Heatmaps
- Subplots

---

## 📖 Documentación Completa

Para más detalles, ver:

- `LIVE_DASHBOARD_README.md` - Documentación completa del dashboard
- `EXTREME_MODE_README.md` - Detalles del modo EXTREME
- `CORRECCIONES_DASHBOARD_LIVE.md` - Historial de correcciones

---

## 🏆 Resultados Post-Battle

Después de completar el battle, se generan automáticamente:

### Dashboards Estáticos (HTML)

- `dashboards/comprehensive_analysis.html`
- `dashboards/statistical_tests.html`

### Visualizaciones de Presentación

- `presentation_viz/box_plot_comparison.html`
- `presentation_viz/radar_chart.html`
- `presentation_viz/violin_plot.html`
- `presentation_viz/correlation_heatmap.html`
- `presentation_viz/3d_scatter.html`
- `presentation_viz/time_series.html`
- `presentation_viz/ranking_table.html`

### Visualizaciones de Red

- `network_viz/all_topologies_comparison.html`
- `network_viz/nsfnet_topology.html`
- ... (6 topologías individuales)

**Total:** 17+ archivos HTML interactivos listos para presentaciones

---

## 🚀 Comandos Rápidos

```powershell
# EXTREME con dashboard (15 min)
python rmsa_demo_live/launch_with_dashboard.py --extreme

# Normal con dashboard (5 min)
python rmsa_demo_live/launch_with_dashboard.py --episodes 200

# Rápido sin dashboard (1 min)
python rmsa_demo_live/demo_orchestrator.py --episodes 50

# Solo dashboard (para testing)
python rmsa_demo_live/live_dashboard.py
```

---

**¡Listo!** 🎉 Ahora tienes el sistema de visualización en tiempo real más avanzado del proyecto.
