# ⚡ QUICK START - Dashboard Live + Battle Royale

## 🎯 TODO EN 1 COMANDO

```powershell
python rmsa_demo_live/launch_with_dashboard.py --extreme
```

**Esto hace automáticamente:**
1. ✅ Inicia dashboard web en http://localhost:8050
2. ✅ Abre navegador automáticamente
3. ✅ Ejecuta Battle Royale EXTREME (2000 episodios)
4. ✅ Actualiza 9 gráficos en tiempo real cada segundo
5. ✅ Al finalizar, detiene todo limpiamente

**Duración:** ~15 minutos  
**Visualizaciones:** 9 dinámicas + 17 estáticas (generadas al final)

---

## 🎨 VISUALIZACIONES EN TIEMPO REAL (9)

En el navegador verás (actualizándose cada 1 segundo):

1. **Rewards Evolution** - Line chart de rewards
2. **Blocking Probability** - Line chart de blocking %
3. **Blocking Distribution** - Pie chart de bloqueo actual
4. **Spectral Efficiency** - Bar chart de eficiencia espectral
5. **QoT Gauge** - Velocímetro de calidad de transmisión
6. **Radar Comparison** - Comparación multidimensional 5D
7. **Current Ranking** - Ranking actual por score compuesto
8. **All Metrics Time Series** - Grid 2×2 con 4 métricas
9. **Status Banner** - Progreso (episodio X/Y)

---

## 🔧 OPCIONES

### Batalla Normal (200 episodios, ~3 minutos)
```powershell
python rmsa_demo_live/launch_with_dashboard.py
```

### Custom Episodes
```powershell
python rmsa_demo_live/launch_with_dashboard.py --episodes 500
```

### Sin Dashboard (Solo Terminal)
```powershell
python rmsa_demo_live/demo_orchestrator.py --extreme
```

---

## 🐛 TROUBLESHOOTING

### Dashboard no abre
**Solución:** Abre manualmente http://localhost:8050

### Puerto 8050 ocupado
```powershell
# Ver qué está usando el puerto
netstat -ano | findstr :8050

# Detener proceso
taskkill /PID <PID> /F
```

### Gráficos no se actualizan
**Solución:** Refresca el navegador (F5) o reinicia el launcher

---

## 📊 ARCHIVOS GENERADOS

**Durante la batalla:**
- `live_battle_data.json` - Datos en tiempo real (actualizado cada episodio)

**Al finalizar:**
- `dashboards/comprehensive_analysis.html`
- `dashboards/statistical_tests.html`
- `presentation_viz/*.html` (7 archivos)
- `network_viz/*.html` (8 archivos)

---

## 🎯 PARÁMETROS EXTREME MODE

| Parámetro | Normal | EXTREME | Cambio |
|-----------|--------|---------|--------|
| Topología | NSFNET | NSFNET | - |
| Slots | 196 | 80 | -59% |
| Carga | 80% | 95% | +19% |
| Steps/Episodio | 100 | 300 | +200% |
| Total Episodios | 200 | 2000 | +900% |

**Objetivo:** Forzar bloqueos y separar claramente a los mejores agentes.

---

## 🏆 SIGUIENTE PASO

Una vez terminada la batalla, usa los HTML generados para tu presentación:

```powershell
# Ver ranking final
start presentation_viz/ranking_table.html

# Ver radar chart
start presentation_viz/radar_chart.html

# Ver comparación de topologías
start network_viz/all_topologies_comparison.html
```

---

**¿Listo para empezar? Ejecuta:**

```powershell
python rmsa_demo_live/launch_with_dashboard.py --extreme
```

🚀 ¡Enjoy the show!
