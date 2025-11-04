# 🚀 Guía Rápida de Inicio

## ✅ Verificación Pre-Entrenamiento

Ejecuta el test de verificación:

```powershell
python test_setup.py
```

Deberías ver:
- ✓ Configuration test PASSED!
- ✓ Environment test PASSED!
- ✓ ALL TESTS PASSED - Ready for Training!

---

## 🏋️ Entrenar Agentes

### Opción 1: Entrenar Ambos (Recomendado)

```powershell
python trainer.py --default --optimized
```

**Tiempo estimado**: 25-35 minutos en Ryzen 7 5700X3D

### Opción 2: Solo para Pruebas Rápidas

```powershell
python trainer.py --default
```

**Tiempo estimado**: 6-10 minutos

---

## 🎬 Ejecutar Demo

Una vez entrenados los modelos:

```powershell
python demo.py
```

**Duración de la demo**: 3-5 minutos  
**Peticiones procesadas**: 200  
**Efecto visual**: ¡ESPECTACULAR!

---

## 📊 Ver Logs de Entrenamiento

```powershell
tensorboard --logdir logs
```

Abre en navegador: http://localhost:6006

---

## 🎯 Resultados Esperados

### Agente DEFAULT (Básico)
- Blocking Probability: **12-18%**
- Acceptance Rate: **82-88%**
- Spectral Utilization: **35-45%**

### Agente OPTIMIZED (Avanzado)
- Blocking Probability: **3-7%** ⭐
- Acceptance Rate: **93-97%** ⭐
- Spectral Utilization: **60-75%** ⭐

**Diferencia visual**: El agente optimizado bloquea **3-4x menos conexiones** que el default.

---

## 🐛 Troubleshooting Rápido

### "ModuleNotFoundError: No module named 'X'"
```powershell
python -m pip install --user -r requirements.txt
```

### "FileNotFoundError: models/default_agent.zip"
Primero entrena los agentes:
```powershell
python trainer.py --default --optimized
```

### Demo muy lenta
Reduce `demo_requests` en `config.py` (línea 64):
```python
demo_requests: int = 100  # En lugar de 200
```

---

## 📁 Estructura de Archivos Generados

Después del entrenamiento:

```
rmsa_demo_live/
├── models/
│   ├── default_agent.zip      # Modelo agente default
│   └── optimized_agent.zip    # Modelo agente optimizado
└── logs/
    ├── default/                # Logs TensorBoard default
    └── optimized/              # Logs TensorBoard optimizado
```

---

## 🔄 Re-entrenar desde Cero

```powershell
# Borrar modelos anteriores
Remove-Item models\*.zip
Remove-Item -Recurse logs\*

# Entrenar de nuevo
python trainer.py --default --optimized
```

---

## 💡 Tips para Mejor Performance

1. **Cierra aplicaciones pesadas** durante entrenamiento
2. **Usa Windows Terminal** para mejor rendering de Rich
3. **No muevas el mouse** durante la demo (evita lag visual)
4. **Ajusta refresh_hz** en config.py si la demo parpadea

---

## 🎓 Para Presentación Académica

### Preparación:
1. Entrenar ambos agentes con anticipación
2. Verificar que demo corre sin errores
3. Tener TensorBoard abierto en segunda pantalla (opcional)
4. Terminal en pantalla completa

### Durante la Demo:
1. Explicar el problema RMSA brevemente
2. Mostrar configuraciones de agentes (test_setup.py)
3. Lanzar demo visual
4. Mientras corre, explicar métricas mostradas
5. Al finalizar, destacar diferencia de blocking probability

### Puntos Clave a Mencionar:
- ✨ Reward multi-objetivo vs binaria
- ✨ Arquitectura de red (2×128 vs 4×256)
- ✨ Hiperparámetros optimizados científicamente
- ✨ 3-4x menos bloqueos con agente optimizado

---

## 📞 Comandos de Un Solo Paso

### Full Setup (desde cero):
```powershell
python -m pip install --user torch==2.5.1+cpu torchvision==0.20.1+cpu --index-url https://download.pytorch.org/whl/cpu
python -m pip install --user -r requirements.txt
python test_setup.py
python trainer.py --default --optimized
python demo.py
```

### Solo Demo (si ya está entrenado):
```powershell
python demo.py
```

---

**¡Listo para asombrar a la audiencia! 🎉**
