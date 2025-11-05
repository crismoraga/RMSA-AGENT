"""CPU optimizations for AMD Ryzen 7 5700X3D (8 cores, 16 threads)."""
from __future__ import annotations

import os
import torch
import multiprocessing as mp


def configure_cpu_performance() -> None:
    """Configure PyTorch and system for maximum CPU performance on Ryzen 7 5700X3D."""
    
    # Ryzen 7 5700X3D: 8 cores, 16 threads
    num_cores = 8
    num_threads = 16
    
    # Set PyTorch to use all threads
    torch.set_num_threads(num_threads)
    torch.set_num_interop_threads(num_cores)
    
    # Enable MKL optimizations for AMD
    os.environ["MKL_NUM_THREADS"] = str(num_threads)
    os.environ["OMP_NUM_THREADS"] = str(num_threads)
    os.environ["OPENBLAS_NUM_THREADS"] = str(num_threads)
    
    # Enable oneDNN (Intel MKL-DNN) optimizations
    # These work well on AMD Ryzen too
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "1"
    
    # Set process affinity to performance cores if possible
    try:
        # Windows-specific: set high priority for training
        import psutil
        p = psutil.Process()
        p.nice(psutil.HIGH_PRIORITY_CLASS)
    except:
        pass
    
    print(f"✓ CPU Optimization configured:")
    print(f"  - PyTorch threads: {num_threads}")
    print(f"  - Interop threads: {num_cores}")
    print(f"  - MKL threads: {num_threads}")
    print(f"  - Device: {torch.get_num_threads()} threads available")


def get_optimal_batch_size(agent_complexity: str = "medium") -> int:
    """
    Calculate optimal batch size based on agent complexity and available RAM.
    
    With 16GB RAM total, we need to be conservative.
    """
    complexity_multipliers = {
        "simple": 128,    # Control agent: 2×128
        "medium": 96,     # Optimized agent: 4×256
        "complex": 64,    # Deep-QoT agent: 3×384
        "adaptive": 80,   # Adaptive agent: 4×320
    }
    
    return complexity_multipliers.get(agent_complexity, 64)


def get_optimal_n_steps(agent_complexity: str = "medium") -> int:
    """Calculate optimal n_steps for PPO rollout buffer."""
    complexity_steps = {
        "simple": 1024,
        "medium": 2048,
        "complex": 1536,
        "adaptive": 1792,
    }
    
    return complexity_steps.get(agent_complexity, 1024)


def print_system_info() -> None:
    """Print detailed system information for debugging."""
    print("\n" + "="*60)
    print("🖥️  SYSTEM CONFIGURATION")
    print("="*60)
    
    # CPU Info
    print(f"CPU Cores: {mp.cpu_count()}")
    print(f"PyTorch Threads: {torch.get_num_threads()}")
    
    # Memory Info
    try:
        import psutil
        mem = psutil.virtual_memory()
        print(f"Total RAM: {mem.total / (1024**3):.1f} GB")
        print(f"Available RAM: {mem.available / (1024**3):.1f} GB")
        print(f"Used RAM: {mem.percent:.1f}%")
    except:
        print("RAM info unavailable")
    
    # PyTorch Info
    print(f"PyTorch Version: {torch.__version__}")
    print(f"CUDA Available: {torch.cuda.is_available()}")
    
    if torch.cuda.is_available():
        print(f"GPU Device: {torch.cuda.get_device_name(0)}")
        print(f"GPU Memory: {torch.cuda.get_device_properties(0).total_memory / (1024**3):.1f} GB")
    else:
        print("GPU: Not available (using CPU)")
    
    # Optimization flags
    print(f"MKL Available: {torch.backends.mkl.is_available()}")
    print(f"MKL-DNN: {torch.backends.mkldnn.is_available()}")
    
    print("="*60 + "\n")


if __name__ == "__main__":
    configure_cpu_performance()
    print_system_info()
