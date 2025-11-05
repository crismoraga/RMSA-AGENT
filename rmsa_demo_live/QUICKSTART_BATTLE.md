# ⚡ QUICK START - RMSA Battle Royale

## 🚀 Inicio Rápido en 3 Pasos

### ✅ Paso 1: Verificar Entrenamiento Completo

```powershell
# Check cuántos modelos están listos
ls models/*.zip
```

Deberías ver 6 archivos:
- `default_agent.zip` (CONTROL)
- `ultho_agent.zip`
- `hyperq_agent.zip`
- `bohamiann_agent.zip`
- `deeprmsa_qot_agent.zip`
- `meta_learning_agent.zip`

### ✅ Paso 2: Ejecutar Demo Battle Royale

```powershell
# Demo estándar (200 episodios, ~5 minutos)
python demo_orchestrator.py
```

**Alternativas**:
```powershell
# Demo rápida (50 episodios, ~1 minuto)
python demo_orchestrator.py --episodes 50

# Topología diferente
python demo_orchestrator.py --topology USNET

# Solo algunos agentes
python demo_orchestrator.py --agents CONTROL ULTHO BOHAMIANN
```

### ✅ Paso 3: Generar Dashboards

```powershell
# Opción A: Todo automatizado (RECOMENDADO)
python mega_run.py --quick

# Opción B: Manual
python plotly_dashboard.py
python network_visualizer.py
```

---

## 📊 Ver Resultados

### Dashboards Interactivos (HTML)
```powershell
# Abrir en navegador
start dashboards/comprehensive_analysis.html
start dashboards/statistical_tests.html
start network_viz/all_topologies_comparison.html
```

### TensorBoard (Logs de Entrenamiento)
```powershell
tensorboard --logdir logs
# Abrir: http://localhost:6006
```

---

## 🎯 Comandos Más Útiles

### Re-entrenar Agente Específico
```powershell
python trainer.py --agents CONTROL
python trainer.py --agents ULTHO
```

### Smoke Test (Validación Rápida)
```powershell
python trainer.py --fast --agents CONTROL
```

### Verificar Setup
```powershell
python test_setup.py
```

---

## 🐛 Troubleshooting Rápido

### "FileNotFoundError: models/X_agent.zip"
```powershell
# Re-entrenar el agente faltante
python trainer.py --agents ULTHO  # Por ejemplo
```

### Demo muy lenta
```powershell
# Reducir episodios
python demo_orchestrator.py --episodes 50
```

### Ver qué modelos están listos
```powershell
python -c "from mega_run import check_models_exist, print_model_status; print_model_status(check_models_exist())"
```

---

## 📈 Workflow Recomendado

```powershell
# 1. Verificar entrenamiento completo
ls models

# 2. Demo rápida de prueba (50 eps)
python demo_orchestrator.py --episodes 50

# 3. Demo completa (200 eps)
python demo_orchestrator.py

# 4. Generar todos los dashboards
python mega_run.py --quick --no-viz
python plotly_dashboard.py
python network_visualizer.py

# 5. Análisis TensorBoard
tensorboard --logdir logs

# 6. Capturar screenshots/video
# (OBS Studio o similar)
```

---

## 🏆 Resultado Esperado

Después de ejecutar todo, tendrás:

✅ **6 Modelos Entrenados** (`models/`)  
✅ **Demo Visualizada** (terminal Rich)  
✅ **Dashboards HTML** (`dashboards/`, `network_viz/`)  
✅ **Logs Completos** (`logs/` - TensorBoard)  
✅ **Ganador Identificado** (output demo)  

---

## ⏰ Tiempo Total

- Demo (200 eps): ~5 minutos
- Dashboards: ~2 minutos
- TensorBoard: Instant
- **Total: ~10 minutos para experiencia completa**

---

<div align="center">

**¡Listo para impresionar! 🚀**

</div>
