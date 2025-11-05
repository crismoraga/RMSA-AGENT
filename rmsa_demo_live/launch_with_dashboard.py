"""🚀 LAUNCHER COMPLETO - Dashboard Live + Battle Royale Simultáneos.

Ejecuta automáticamente:
1. Dashboard web en http://localhost:8050 (actualización en tiempo real)
2. Battle Royale en terminal con visualización Rich

Uso:
    python rmsa_demo_live/launch_with_dashboard.py
    python rmsa_demo_live/launch_with_dashboard.py --extreme
    python rmsa_demo_live/launch_with_dashboard.py --episodes 100
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
import webbrowser
from pathlib import Path
from threading import Thread

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

console = Console()


def print_launcher_banner():
    """Banner de inicio del launcher."""
    banner = Text()
    banner.append("\n╔═══════════════════════════════════════════════════════════════════════╗\n", style="bold cyan")
    banner.append("║                                                                       ║\n", style="bold cyan")
    banner.append("║         🚀 RMSA BATTLE ROYALE + LIVE DASHBOARD LAUNCHER 🚀           ║\n", style="bold yellow")
    banner.append("║                                                                       ║\n", style="bold cyan")
    banner.append("║  Este launcher ejecutará 2 procesos simultáneos:                     ║\n", style="bold white")
    banner.append("║                                                                       ║\n", style="bold cyan")
    banner.append("║  1️⃣  Live Dashboard Web (http://localhost:8050)                       ║\n", style="bold green")
    banner.append("║     • 9 visualizaciones dinámicas en tiempo real                     ║\n", style="white")
    banner.append("║     • Actualización automática cada 1 segundo                        ║\n", style="white")
    banner.append("║     • Pie charts, radar charts, time series, etc.                    ║\n", style="white")
    banner.append("║                                                                       ║\n", style="bold cyan")
    banner.append("║  2️⃣  Battle Royale Terminal (Rich UI)                                 ║\n", style="bold magenta")
    banner.append("║     • 6 agentes compitiendo simultáneamente                          ║\n", style="white")
    banner.append("║     • Scoreboard dinámico en terminal                                ║\n", style="white")
    banner.append("║     • Métricas actualizadas en tiempo real                           ║\n", style="white")
    banner.append("║                                                                       ║\n", style="bold cyan")
    banner.append("╚═══════════════════════════════════════════════════════════════════════╝\n", style="bold cyan")
    
    console.print(Panel(banner, border_style="bold yellow"))


def start_dashboard_server():
    """Inicia el servidor del dashboard en un proceso separado."""
    console.print("\n[bold yellow]🔴 Iniciando Live Dashboard Server...[/bold yellow]")
    
    # Ejecutar el dashboard en un proceso separado
    process = subprocess.Popen(
        [sys.executable, "rmsa_demo_live/live_dashboard.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Esperar a que el servidor inicie
    time.sleep(3)
    
    console.print("[green]✓ Dashboard server iniciado en http://localhost:8050[/green]")
    
    return process


def open_dashboard_browser():
    """Abre el dashboard en el navegador."""
    console.print("[yellow]🌐 Abriendo dashboard en navegador...[/yellow]")
    time.sleep(2)
    webbrowser.open("http://localhost:8050")
    console.print("[green]✓ Dashboard abierto en navegador[/green]\n")


def start_battle_royale(args):
    """Inicia el Battle Royale en el proceso principal."""
    console.print("[bold cyan]⚔️  Iniciando Battle Royale...[/bold cyan]\n")
    time.sleep(1)
    
    # Construir comando
    cmd = [sys.executable, "rmsa_demo_live/demo_orchestrator.py"]
    
    if args.extreme:
        cmd.append("--extreme")
    elif args.episodes:
        cmd.extend(["--episodes", str(args.episodes)])
    
    # Ejecutar battle royale
    subprocess.run(cmd)


def main():
    """Función principal del launcher."""
    parser = argparse.ArgumentParser(description="Launch Battle Royale with Live Dashboard")
    parser.add_argument("--extreme", action="store_true", help="Use EXTREME mode")
    parser.add_argument("--episodes", type=int, help="Number of episodes (overrides extreme)")
    args = parser.parse_args()
    
    print_launcher_banner()
    
    console.print("\n[bold]⚙️  Configuración:[/bold]")
    if args.extreme:
        console.print("  • Modo: [red]EXTREME[/red] (NSFNET, 80 slots, 95% load, 300 steps)")
        console.print("  • Episodios: [yellow]2000[/yellow]")
    elif args.episodes:
        console.print(f"  • Modo: [green]NORMAL[/green]")
        console.print(f"  • Episodios: [yellow]{args.episodes}[/yellow]")
    else:
        console.print("  • Modo: [green]NORMAL[/green]")
        console.print("  • Episodios: [yellow]200[/yellow] (default)")
    
    console.print("\n[bold yellow]═══════════════════════════════════════════════════════════════[/bold yellow]\n")
    
    # Paso 1: Iniciar dashboard server
    dashboard_process = start_dashboard_server()
    
    # Paso 2: Abrir navegador
    Thread(target=open_dashboard_browser).start()
    
    # Paso 3: Iniciar battle royale
    try:
        start_battle_royale(args)
    except KeyboardInterrupt:
        console.print("\n[yellow]⚠️  Battle Royale interrumpido por usuario[/yellow]")
    finally:
        # Cleanup: terminar dashboard server
        console.print("\n[yellow]🛑 Deteniendo Live Dashboard Server...[/yellow]")
        dashboard_process.terminate()
        dashboard_process.wait()
        console.print("[green]✓ Dashboard server detenido[/green]")
    
    console.print("\n[bold green]🎉 Sesión completa finalizada![/bold green]\n")


if __name__ == "__main__":
    main()
