# Guía de Instalación - RMSA Demo Live
## Hardware AMD RX 6700XT + Ryzen 7 5700X3D

### Pre-requisitos
- Python 3.12 (ya instalado)
- GPU AMD RX 6700XT con drivers actualizados
- 16GB RAM
- ~5GB espacio libre en disco

### Pasos de Instalación

#### 1. Actualizar pip y herramientas de build
```powershell
python -m pip install --upgrade pip setuptools wheel
```

#### 2. Instalar PyTorch con ROCm para AMD
**IMPORTANTE**: Tu GPU AMD requiere PyTorch con soporte ROCm, NO CUDA.

```powershell
pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/rocm5.6
```

**Verificar instalación de PyTorch:**
```powershell
python -c "import torch; print(f'PyTorch: {torch.__version__}'); print(f'ROCm disponible: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"
```

Deberías ver:
- PyTorch: 2.1.0+rocm5.6
- ROCm disponible: True
- Device: AMD Radeon RX 6700 XT

#### 3. Instalar dependencias del proyecto
```powershell
cd C:\Users\Cris\Desktop\Taller3\rmsa_demo_live
pip install -r requirements.txt
```

#### 4. Verificar instalación de optical-rl-gym
```powershell
python -c "import optical_rl_gym; print('Optical RL Gym instalado correctamente')"
```

#### 5. Verificar instalación completa
```powershell
python -c "import gymnasium, stable_baselines3, torch, rich, optuna; print('✓ Todas las dependencias instaladas')"
```

### Troubleshooting

#### Si PyTorch no detecta la GPU AMD:
1. Verificar drivers AMD: Adrenalin 23.x o superior
2. Reinstalar PyTorch ROCm: `pip uninstall torch torchvision && pip install torch==2.1.0 torchvision==0.16.0 --index-url https://download.pytorch.org/whl/rocm5.6`
3. Verificar variables de entorno:
   ```powershell
   $env:PYTORCH_ROCM_ARCH="gfx1031"
   $env:HSA_OVERRIDE_GFX_VERSION="10.3.0"
   ```

#### Si optical-rl-gym falla:
```powershell
pip install --no-cache-dir optical-rl-gym==1.3.1
```

#### Si hay errores de compilación:
Instalar Visual Studio Build Tools (requerido para compilar extensiones):
https://visualstudio.microsoft.com/visual-cpp-build-tools/

### Configuración Óptima para tu Hardware

**config.py** ya está optimizado considerando:
- RX 6700XT: 12GB VRAM (suficiente para redes de 4x256 neuronas)
- Ryzen 7 5700X3D: 8 cores (permite batch size 256 sin bottleneck)
- 16GB RAM: Adecuado para vectorized environments

### Próximos Pasos

1. **Entrenar agentes**: `python trainer.py --default --optimized`
2. **Ejecutar demo**: `python demo.py`
3. **Ver logs TensorBoard**: `tensorboard --logdir logs`

### Notas Específicas AMD

- **ROCm vs CUDA**: ROCm es el equivalente de AMD a CUDA de NVIDIA
- **Rendimiento**: RX 6700XT entrenará ~15-20% más lento que RTX 3070, pero es completamente funcional
- **VRAM**: 12GB es excelente, más que suficiente para este proyecto
- **Batch size recomendado**: 256 (optimizado)
- **Tiempo estimado entrenamiento**:
  - Agente default: ~8-12 minutos
  - Agente optimizado: ~18-25 minutos

### Comandos Útiles

**Monitorear GPU durante entrenamiento:**
```powershell
# Instalar radeontop (opcional, requiere WSL si estás en Windows)
# O usar AMD Software: Adrenalin Edition para ver uso de GPU
```

**Limpiar caché PyTorch:**
```python
import torch
torch.cuda.empty_cache()
```

**Ver uso de memoria:**
```python
import torch
if torch.cuda.is_available():
    print(f"Memoria asignada: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")
    print(f"Memoria reservada: {torch.cuda.memory_reserved(0)/1024**3:.2f} GB")
```

### Optimizaciones Específicas para AMD en el Código

El código ya incluye optimizaciones para AMD:
- Uso de `torch.backends.cudnn.benchmark = False` (ROCm no usa cuDNN)
- Batch sizes optimizados para RDNA2 architecture
- Gradient accumulation si es necesario (automático en SB3)

### Referencias AMD ROCm

- ROCm Documentation: https://rocm.docs.amd.com/
- PyTorch ROCm: https://pytorch.org/get-started/locally/
- Compatibilidad RX 6700XT: RDNA2, gfx1031, ROCm 5.x compatible
