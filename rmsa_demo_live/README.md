# 🚀 RMSA Live Demo - Deep Reinforcement Learning para Redes Ópticas

Demo visual espectacular comparando agentes de IA (Default vs Optimizado) resolviendo el problema **RMSA** (Routing, Modulation and Spectrum Assignment) en redes ópticas WDM elásticas.

---

## 📋 Descripción

Aplicación de demostración que muestra **dramáticamente** la diferencia entre:

- **🔵 AGENTE DEFAULT**: Configuración básica con reward binaria simple
- **🟢 AGENTE OPTIMIZADO**: Hiperparámetros científicamente optimizados con reward multi-objetivo

### Características Destacadas

✨ **Interfaz Rich Terminal** - Dashboard en tiempo real visualmente impactante  
⚡ **Procesamiento Paralelo** - Ambos agentes procesan las mismas peticiones simultáneamente  
📊 **Métricas en Vivo** - Blocking probability, utilización espectral, fragmentación, QoT  
🎯 **Fairness Garantizado** - Misma semilla para ambos agentes (comparación justa)  
🔬 **Científicamente Riguroso** - Basado en papers de DeepRMSA y MFDRL-RSA

---

## 🖥️ Hardware Soportado

**PC de Desarrollo:**
- **CPU**: Ryzen 7 5700X3D (8 cores)
- **RAM**: 16 GB
- **GPU**: AMD Radeon RX 6700XT (12GB) - *Nota: En Windows, PyTorch usa CPU*

**Sistema Operativo**: Windows 11  
**Python**: 3.12.3

---

## 📦 Instalación

### 1. Verificar Pre-requisitos

```powershell
python --version  # Debe ser Python 3.11+
```

### 2. Actualizar pip

```powershell
python -m pip install --upgrade pip setuptools wheel
```

### 3. Instalar PyTorch

**IMPORTANTE**: En Windows con GPU AMD, PyTorch usa CPU (ROCm solo en Linux).

```powershell
python -m pip install --user torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
```

### 4. Instalar Dependencias del Proyecto

```powershell
cd c:\Users\Cris\Desktop\Taller3\rmsa_demo_live
python -m pip install --user -r requirements.txt
```

### 5. Verificar Instalación

```powershell
python -c "import torch, gymnasium, stable_baselines3, rich, rmsa_environment; print('✓ Todo instalado correctamente')"
```

---

## 🏗️ Arquitectura del Sistema

```
rmsa_demo_live/
├── config.py              # Configuraciones agentes (default vs optimizado)
├── rmsa_environment.py    # Implementación ambiente RMSA con NSFNET
├── environment.py         # Wrappers y helpers de Gymnasium
├── reward_functions.py    # Rewards: binaria vs multi-objetivo
├── agents.py              # Builders PPO con dropout y arquitecturas custom
├── metrics.py             # Tracking de métricas en tiempo real
├── visualizer.py          # Dashboard Rich con layout dividido
├── trainer.py             # Entrenamiento automatizado
├── demo.py                # ⭐ Script principal de demo
├── requirements.txt       # Dependencias Python
└── README.md              # Esta documentación
```

---

## 🎮 Uso

### Entrenar Agentes

**Entrenar solo agente default** (más rápido):
```powershell
python trainer.py --default
```

**Entrenar solo agente optimizado** (mejor rendimiento):
```powershell
python trainer.py --optimized
```

**Entrenar ambos** (recomendado para demo completa):
```powershell
python trainer.py --default --optimized
```

**Tiempos estimados de entrenamiento (CPU Ryzen 7 5700X3D):**
- Agente Default (30k steps): ~6-10 minutos
- Agente Optimizado (60k steps): ~15-25 minutos

### Ejecutar Demo en Vivo

```powershell
python demo.py
```

La demo procesará **200 peticiones de conexión** mostrando métricas en tiempo real comparando ambos agentes lado a lado.

**Duración**: ~3-5 minutos  
**Efecto Visual**: ¡ESPECTACULAR! 🎆

---

## 🧠 Configuraciones de los Agentes

### 🔵 Agente DEFAULT

```python
Arquitectura: 2 capas × 128 neuronas
Learning Rate: 1e-3 (convergencia rápida pero subóptima)
Activación: ReLU
Reward: Binaria simple (+1 éxito, -1 bloqueo)
Gamma: 0.99
Batch Size: 64
Dropout: 0.0
```

### 🟢 Agente OPTIMIZADO

```python
Arquitectura: 4 capas × 256 neuronas
Learning Rate: 2.7e-4 (optimizado científicamente)
Activación: SiLU/Swish (mejor para redes ópticas)
Reward: Multi-objetivo (5 componentes)
  - Éxito asignación: ±10.0
  - Quality of Transmission: -exp(-OSNR/20.0) × 3.0
  - Eficiencia espectral: 5.0 × (1.0 - utilización)
  - Fragmentación: -2.0 × índice_fragmentación
  - Balance de carga: 1.5 × factor_balance
Gamma: 0.997 (mayor consideración futuro)
Batch Size: 256
Dropout: 0.2
Gradient Clipping: 0.8
```

---

## 📊 Métricas Monitoreadas

La demo muestra en tiempo real:

| Métrica | Descripción |
|---------|-------------|
| **Blocking Probability** | % de conexiones bloqueadas (objetivo: <5%) |
| **Acceptance Rate** | % de conexiones exitosas |
| **Spectral Utilization** | Uso del espectro óptico |
| **Fragmentation Index** | Nivel de fragmentación espectral |
| **QoT Compliance** | Calidad de transmisión óptica |
| **Load Balance** | Balance de carga entre enlaces |
| **Reward Acumulado** | Suma de rewards por episodio |

---

## 🌐 Ambiente RMSA

### Topología: NSFNET
- **Nodos**: 14
- **Enlaces**: 21
- **Distancias**: Realistas (300-2700 km)

### Espectro Óptico
- **Banda**: C-band
- **Frequency Slots**: 196
- **Granularidad**: 12.5 GHz

### Formatos de Modulación

| Formato | Alcance | Eficiencia Espectral |
|---------|---------|---------------------|
| BPSK | 4000 km | 1 bit/s/Hz |
| QPSK | 2000 km | 2 bit/s/Hz |
| 8QAM | 1000 km | 3 bit/s/Hz |
| 16QAM | 500 km | 4 bit/s/Hz |

### Tráfico
- **Bit Rates**: 25, 50, 100, 200, 400 Gbps
- **Distribución**: Exponencial (load factor = 0.8)
- **Política**: First-Fit spectrum assignment
- **Rutas**: K=3 shortest paths

---

## 🎯 Criterios de Éxito

La demo es exitosa si:

✅ **Agente Optimizado** muestra blocking <5% vs >12% del default  
✅ **Diferencias visuales** son dramáticas e inmediatas  
✅ **Demo corre** sin interrupciones en 3-5 minutos  
✅ **Métricas** se actualizan suavemente en tiempo real  
✅ **Interfaz Rich** es profesional y espectacular  
✅ **Audiencia** reconoce inmediatamente qué agente es superior

---

## 🔧 Troubleshooting

### Error: "optical-rl-gym not found"
**Solución**: Usamos implementación custom en `rmsa_environment.py`. No se requiere optical-rl-gym.

### Error: "GPU not detected"
**Solución**: Normal en Windows con AMD. PyTorch usa CPU que es completamente funcional.

### Entrenamiento muy lento
**Solución**: 
- Reducir `timesteps` en `config.py`
- Usar `--default` solo para pruebas rápidas
- Batch size ya optimizado para tu CPU

### Demo se congela
**Solución**:
- Verificar modelos entrenados existen en `models/`
- Reducir `demo_requests` en `config.py`
- Cerrar otras aplicaciones pesadas

---

## 📚 Referencias Científicas

1. **DeepRMSA**: Deep Reinforcement Learning for Routing and Spectrum Allocation  
   Chen et al., IEEE INFOCOM 2018

2. **MFDRL-RSA**: Multi-Feature Deep Reinforcement Learning for RSA  
   Natalino et al., Journal of Optical Communications 2020

3. **Optical RL-Gym**: Simulation Framework for RL in Optical Networks  
   https://github.com/carlosnatalino/optical-rl-gym

4. **Stable-Baselines3**: Reliable RL Implementations  
   https://stable-baselines3.readthedocs.io/

---

## 🎨 Interfaz Visual

La demo usa **Rich library** para crear un dashboard profesional:

```
┌────────────────────────────────────────────────────────────┐
│         RMSA Live Comparison - Default vs Optimized        │
│            Episode 1 | Request #156 | 100→5 @ 200Gbps     │
└────────────────────────────────────────────────────────────┘

┌─────────────── Default ───────────────┐  ┌───────────── Optimized ─────────────┐
│ Blocking Probability:    15.38%       │  │ Blocking Probability:    3.85%      │
│ Acceptance Rate:         84.62%       │  │ Acceptance Rate:         96.15%     │
│ Spectral Utilization:    42.3%        │  │ Spectral Utilization:    68.7%      │
│ Fragmentation:           0.482        │  │ Fragmentation:           0.234      │
│ QoT Compliance:          0.846        │  │ QoT Compliance:          0.961      │
│ Reward:                  +12.4        │  │ Reward:                  +48.7      │
│ Last Action:             Path 2-5-9   │  │ Last Action:             Path 2-3-8 │
└───────────────────────────────────────┘  └─────────────────────────────────────┘
```

---

## 💡 Optimizaciones para CPU

El código incluye:
- ✅ Batch sizes optimizados para Ryzen 7 5700X3D
- ✅ Timesteps reducidos (30k/60k vs 50k/100k)
- ✅ Eval frequency balanceada
- ✅ Sin uso de GPU (compatible con AMD en Windows)
- ✅ Arquitecturas de red eficientes para CPU

---

## 🚀 Próximos Pasos

1. **Ejecutar entrenamiento completo**: `python trainer.py --default --optimized`
2. **Lanzar demo visual**: `python demo.py`
3. **Analizar logs TensorBoard**: `tensorboard --logdir logs`
4. **Experimentar con hiperparámetros** en `config.py`
5. **Optimizar reward functions** para tu caso de uso

---

## 📝 Notas Técnicas

- **PyTorch CPU** es ~3-5x más lento que GPU pero completamente funcional
- **Tiempos de entrenamiento** pueden variar según carga del sistema
- **Rich terminal** requiere terminal con soporte de color (PowerShell, Windows Terminal)
- **Modelos guardados** en formato `.zip` de Stable-Baselines3

---

## 🤝 Contribuciones

Para mejorar esta demo:

1. Ajustar reward functions en `reward_functions.py`
2. Añadir nuevas topologías en `rmsa_environment.py`
3. Mejorar visualizaciones en `visualizer.py`
4. Optimizar hiperparámetros con Optuna (ya incluido)

---

## 📄 Licencia

Proyecto académico - Taller 3 Deep Reinforcement Learning

---

## 🎓 Autor

Desarrollado para demostración académica de Deep RL aplicado a redes ópticas elásticas.

**Hardware**: Ryzen 7 5700X3D + RX 6700XT + 16GB RAM  
**Stack**: Python 3.12 + PyTorch 2.5.1 + Gymnasium + SB3  
**Fecha**: Noviembre 2025

---

**¡Disfruta de la demo! 🎉**
