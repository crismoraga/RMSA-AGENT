# 🔥 EXTREME BATTLE ROYALE - Guía de Uso Rápido

## 🎯 Descripción

Modo **EXTREME** del Battle Royale con configuración ultra-difícil para separar verdaderamente a los mejores agentes.

### Diferencias vs Modo Normal

| Parámetro | Normal | EXTREME | Impacto |
|-----------|--------|---------|---------|
| **Topología** | NSFNET (14 nodos) | USNET (24 nodos) | +71% más compleja |
| **Espectro** | 196 slots | 100 slots | -49% capacidad |
| **Carga** | 80% | 95% | +19% tráfico |
| **Episodio** | 100 pasos | 200 pasos | +100% duración |
| **Peticiones** | 200 | 2000 | +900% evaluaciones |

---

## 🚀 Uso Rápido

### Opción 1: Batalla Extrema Completa (RECOMENDADO)

```powershell
python rmsa_demo_live/demo_orchestrator.py --extreme
```

Esto ejecutará:
- ✅ 2000 episodios en topología USNET (24 nodos, 43 enlaces)
- ✅ Carga 95% (muy alta, forzará bloqueos)
- ✅ Solo 100 slots de espectro (fragmentación extrema)
- ✅ 200 pasos por episodio (estrés prolongado)
- ✅ Generación automática de TODOS los dashboards y visualizaciones

**Duración estimada**: 10-15 minutos

---

### Opción 2: Batalla Extrema Rápida (Test)

```powershell
python rmsa_demo_live/demo_orchestrator.py --extreme --episodes 500
```

**Duración estimada**: 3-5 minutos

---

### Opción 3: Solo Algunos Agentes en Modo Extremo

```powershell
python rmsa_demo_live/demo_orchestrator.py --extreme --agents CONTROL ULTHO BOHAMIANN
```

---

## 📊 Visualizaciones Generadas

Después de la batalla, se generan automáticamente:

### 📁 `dashboards/`
- `comprehensive_analysis.html` - 6 subplots con todas las métricas
- `statistical_tests.html` - ANOVA y t-tests con significancia estadística

### 📁 `presentation_viz/`
- `box_plot_comparison.html` - Box plots de todas las métricas
- `radar_chart.html` - Radar multidimensional de performance
- `violin_plot.html` - Distribuciones de recompensa
- `correlation_heatmap.html` - Correlaciones entre métricas
- `3d_scatter.html` - Espacio 3D de performance
- `time_series.html` - Evolución de recompensa
- `ranking_table.html` - Tabla final de ranking

### 📁 `network_viz/`
- `all_topologies_comparison.html` - Visualización NetworkX de todas las topologías

---

## 🏆 Resultados Esperados

En modo EXTREME, espera ver:

### Agentes Débiles (CONTROL)
- ❌ Blocking: 15-30% (MALO)
- ❌ Spectral Efficiency: <20%
- ❌ Reward negativo o cercano a 0

### Agentes Optimizados (ULTHO, BOHAMIANN, META-LEARNING)
- ✅ Blocking: 3-8% (BUENO)
- ✅ Spectral Efficiency: 40-60%
- ✅ Reward positivo constante

### Diferencia Dramática
El modo EXTREME amplifica las diferencias entre agentes. Solo los verdaderamente optimizados sobrevivirán con métricas decentes.

---

## 🔬 Análisis Científico

Los dashboards incluyen:

- **ANOVA**: Prueba si hay diferencias significativas entre agentes
- **T-tests**: Comparación par a par con valores p
- **Box plots**: Distribuciones y outliers
- **Heatmaps**: Correlaciones entre métricas
- **3D scatter**: Espacio multidimensional de performance

---

## 💡 Tips

1. **Primera vez**: Ejecuta modo EXTREME completo para datos robustos
2. **Comparar recompensas**: Mira `presentation_viz/radar_chart.html`
3. **Identificar ganador**: Mira `presentation_viz/ranking_table.html`
4. **Para presentación**: Todos los gráficos en `presentation_viz/` son listos para slides

---

## ⚠️ Notas

- El modo EXTREME es **significativamente más difícil**
- Los agentes mal optimizados tendrán blocking >20%
- Solo los mejores agentes mantendrán blocking <10%
- Ideal para demostrar valor de optimización avanzada

---

## 🎯 Ejemplo Completo

```powershell
# 1. Ejecutar batalla extrema
python rmsa_demo_live/demo_orchestrator.py --extreme

# 2. Abrir resultados
start presentation_viz/ranking_table.html
start presentation_viz/radar_chart.html
start dashboards/comprehensive_analysis.html

# 3. Para presentación PowerPoint
# → Abrir todos los HTML en presentation_viz/
# → Screenshot de cada gráfico
# → Insertar en slides
```

---

## 🏁 ¡Listo para la Batalla Extrema!

Ejecuta el comando y observa cómo los agentes luchan por sobrevivir en condiciones extremas. Solo el mejor algoritmo prevalecerá. 🔥
