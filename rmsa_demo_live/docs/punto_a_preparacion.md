# Punto A: Preparación de Herramientas

## 1. Inventario actual del entorno

- **Sistema operativo**: Windows (PowerShell como shell por defecto)
- **Python configurado**: `C:/Python312/python.exe` (versión 3.12.3)
- **pip**: 25.3 (instalado junto a Python)
- **Git**: 2.51.0.windows.1

### Comandos verificados

```powershell
C:/Python312/python.exe --version
# -> Python 3.12.3

C:/Python312/python.exe -m pip --version
# -> pip 25.3 from C:\Users\Cris\AppData\Roaming\Python\Python312\site-packages\pip (python 3.12)

git --version
# -> git version 2.51.0.windows.1
```

## 2. Requerimientos para la demo RMSA

- **Entorno virtual** (recomendado): `python -m venv .venv`
- **Dependencias**: ver `../requirements.txt`
- **Capacidades opcionales**: GPU CUDA (acelera entrenamiento), tarjeta de sonido para audio opcional.

## 3. Procedimiento de instalación rápida

```powershell
# 1) Crear y activar entorno virtual
C:/Python312/python.exe -m venv .venv
.\.venv\Scripts\Activate.ps1

# 2) Actualizar pip y wheel
python -m pip install --upgrade pip wheel

# 3) Instalar dependencias de la demo
python -m pip install -r requirements.txt

# 4) Validar instalación
python - <<'PY'
import gymnasium, stable_baselines3, torch, optical_rl_gym, networkx
print("Dependencias clave OK")
PY
```

## 4. Recursos clave consultados

- **Optical RL-Gym**: toolkit estándar para integrar agentes RL y entornos ópticos, siguiendo la filosofía OpenAI Gym y acelerando la experimentación en RMSA [`Natalino & Monti, 2020`](https://doi.org/10.1109/ICTON51198.2020.9203239).
- **DeepRMSA**: marco DRL basado en A3C/A2C que reduce la probabilidad de bloqueo >20% frente a heurísticas de referencia [`Chen et al., 2019`](https://doi.org/10.48550/arXiv.1905.02248).
- **MFDRL-RSA**: recompensa multi-objetivo con métrica de fragmentación multi-link; logra mejoras del 13% en bloqueo y 10% en eficiencia espectral sobre DeepRMSA en NSFNET [`Jiang et al., 2025`](https://doi.org/10.3390/photonics12070634).

## 5. Próximos pasos sugeridos

1. Definir scripts automatizados (`make.ps1` / tareas VS Code) para levantar demo y limpiar artefactos.
2. Descargar/entrenar modelos base (`models/default_model.zip`, `models/optimized_model.zip`).
3. Validar ejecución mínima del entorno RMSA con agentes "dummy" antes de integrar la UI avanzada.
