"""🎬 MEGA RUN - Ejecuta pipeline completo del RMSA Battle Royale.

Este script automatiza:
1. Verificación del entrenamiento
2. Ejecución de la demo
3. Generación de dashboards Plotly
4. Generación de visualizaciones de red
5. Reporte final con ganador

Uso:
    python mega_run.py              # Pipeline completo
    python mega_run.py --quick      # Solo demo (sin re-entrenar)
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table

console = Console()


def check_models_exist() -> dict[str, bool]:
    """Verifica qué modelos ya están entrenados."""
    
    models_dir = Path("models")
    expected_models = {
        "CONTROL": "default_agent.zip",
        "ULTHO": "ultho_agent.zip",
        "HYPERQ-OPT": "hyperq_agent.zip",
        "BOHAMIANN": "bohamiann_agent.zip",
        "DEEPRMSA-QOT": "deeprmsa_qot_agent.zip",
        "META-LEARNING": "meta_learning_agent.zip",
    }
    
    status = {}
    for agent, filename in expected_models.items():
        model_path = models_dir / filename
        status[agent] = model_path.exists()
    
    return status


def print_model_status(status: dict[str, bool]) -> None:
    """Imprime tabla de estado de modelos."""
    
    models_dir = Path("models")
    expected_models = {
        "CONTROL": "default_agent.zip",
        "ULTHO": "ultho_agent.zip",
        "HYPERQ-OPT": "hyperq_agent.zip",
        "BOHAMIANN": "bohamiann_agent.zip",
        "DEEPRMSA-QOT": "deeprmsa_qot_agent.zip",
        "META-LEARNING": "meta_learning_agent.zip",
    }
    
    table = Table(title="📦 Model Status", show_header=True, header_style="bold magenta")
    table.add_column("Agent", style="cyan", width=20)
    table.add_column("Status", justify="center", width=15)
    table.add_column("Path", style="dim")
    
    for agent, exists in status.items():
        status_emoji = "✅ Trained" if exists else "❌ Missing"
        status_color = "green" if exists else "red"
        table.add_row(
            agent,
            f"[{status_color}]{status_emoji}[/{status_color}]",
            f"models/{expected_models[agent]}"
        )
    
    console.print(table)
    console.print()


def run_step(step_name: str, command: list[str], description: str) -> bool:
    """Ejecuta un paso del pipeline con feedback visual."""
    
    console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
    console.print(f"[bold yellow]▶ STEP: {step_name}[/bold yellow]")
    console.print(f"[dim]{description}[/dim]")
    console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
    
    try:
        result = subprocess.run(
            command,
            check=True,
            capture_output=False,
            text=True,
        )
        console.print(f"\n[bold green]✓ {step_name} completed successfully![/bold green]\n")
        return True
    except subprocess.CalledProcessError as e:
        console.print(f"\n[bold red]✗ {step_name} failed with error code {e.returncode}[/bold red]\n")
        return False
    except KeyboardInterrupt:
        console.print(f"\n[bold yellow]⚠ {step_name} interrupted by user[/bold yellow]\n")
        return False


def main():
    parser = argparse.ArgumentParser(description="RMSA Battle Royale - MEGA RUN Pipeline")
    parser.add_argument("--quick", action="store_true", help="Skip training (use existing models)")
    parser.add_argument("--no-viz", action="store_true", help="Skip dashboard generation")
    parser.add_argument("--episodes", type=int, default=200, help="Number of demo episodes")
    args = parser.parse_args()
    
    # Banner
    banner = """
╔═══════════════════════════════════════════════════════════════════╗
║                                                                   ║
║            🚀 RMSA BATTLE ROYALE - MEGA RUN 🚀                    ║
║                                                                   ║
║   Automated Pipeline: Train → Demo → Dashboards → Analysis       ║
║                                                                   ║
╚═══════════════════════════════════════════════════════════════════╝
"""
    console.print(Panel(banner, border_style="bold magenta"))
    time.sleep(1)
    
    # Check Python version
    console.print(f"[dim]Python: {sys.version.split()[0]}[/dim]")
    console.print(f"[dim]Working Directory: {Path.cwd()}[/dim]\n")
    
    # Step 0: Check model status
    console.print("[bold cyan]📋 Checking model status...[/bold cyan]\n")
    model_status = check_models_exist()
    print_model_status(model_status)
    
    all_trained = all(model_status.values())
    
    # Step 1: Training (optional)
    if not args.quick:
        if not all_trained:
            console.print("[bold yellow]⚠ Some models are missing. Starting training...[/bold yellow]\n")
            time.sleep(2)
            
            success = run_step(
                "1. TRAINING (6 AGENTS)",
                [sys.executable, "rmsa_demo_live/trainer.py"],
                "Training all 6 agents with optimized hyperparameters (~3-4 hours on Ryzen 7 5700X3D)"
            )
            
            if not success:
                console.print("[bold red]✗ Training failed or was interrupted. Exiting.[/bold red]")
                return
        else:
            console.print("[bold green]✓ All models already trained. Skipping training step.[/bold green]\n")
    else:
        console.print("[bold yellow]⚠ Quick mode: Skipping training (using existing models)[/bold yellow]\n")
    
    # Step 2: Run Demo
    success = run_step(
        "2. DEMO ORCHESTRATOR",
        [sys.executable, "rmsa_demo_live/demo_orchestrator.py", "--episodes", str(args.episodes)],
        f"Running Battle Royale demo with {args.episodes} episodes"
    )
    
    if not success:
        console.print("[bold red]✗ Demo failed. Check if all models exist.[/bold red]")
        return
    
    # Step 3: Generate Dashboards (optional)
    if not args.no_viz:
        # Plotly dashboards
        success = run_step(
            "3. PLOTLY DASHBOARDS",
            [sys.executable, "-c", "from rmsa_demo_live.plotly_dashboard import generate_dashboards_from_battle; from rmsa_demo_live.demo_orchestrator import DemoOrchestrator; o = DemoOrchestrator(['CONTROL', 'ULTHO'], 50); m = o.run(); generate_dashboards_from_battle(m)"],
            "Generating interactive Plotly dashboards (HTML)"
        )
        
        # Network visualizations
        success = run_step(
            "4. NETWORK VISUALIZATIONS",
            [sys.executable, "rmsa_demo_live/network_visualizer.py"],
            "Generating NetworkX topology visualizations (HTML)"
        )
    else:
        console.print("[bold yellow]⚠ Skipping dashboard generation (--no-viz flag)[/bold yellow]\n")
    
    # Final Report
    console.print(f"\n[bold cyan]{'='*80}[/bold cyan]")
    console.print("[bold green]🎉 MEGA RUN COMPLETED SUCCESSFULLY! 🎉[/bold green]")
    console.print(f"[bold cyan]{'='*80}[/bold cyan]\n")
    
    # Output summary
    output_table = Table(title="📁 Output Files", show_header=True, header_style="bold magenta")
    output_table.add_column("Category", style="cyan", width=20)
    output_table.add_column("Location", style="green")
    output_table.add_column("Description", style="dim")
    
    output_table.add_row(
        "Models",
        "models/*.zip",
        "6 trained PPO agents (50k-120k timesteps each)"
    )
    output_table.add_row(
        "Logs",
        "logs/*/",
        "TensorBoard training logs (view with: tensorboard --logdir logs)"
    )
    
    if not args.no_viz:
        output_table.add_row(
            "Dashboards",
            "dashboards/*.html",
            "Interactive Plotly analysis dashboards"
        )
        output_table.add_row(
            "Network Viz",
            "network_viz/*.html",
            "NetworkX topology visualizations"
        )
    
    console.print(output_table)
    console.print()
    
    # Next steps
    next_steps = """
[bold cyan]📌 Next Steps:[/bold cyan]

1. [bold]View TensorBoard logs:[/bold]
   tensorboard --logdir logs
   Open: http://localhost:6006

2. [bold]Open Plotly dashboards:[/bold]
   - dashboards/comprehensive_analysis.html
   - dashboards/statistical_tests.html

3. [bold]Explore network topologies:[/bold]
   - network_viz/all_topologies_comparison.html
   - network_viz/topology_statistics.html

4. [bold]Re-run demo with different settings:[/bold]
   python demo_orchestrator.py --topology USNET --episodes 500

5. [bold]Train specific agents only:[/bold]
   python trainer.py --agents CONTROL ULTHO BOHAMIANN
"""
    console.print(Panel(next_steps, border_style="bold green", title="🚀 What's Next?"))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n\n[bold yellow]⚠ Mega run interrupted by user[/bold yellow]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n\n[bold red]✗ Unexpected error: {e}[/bold red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
