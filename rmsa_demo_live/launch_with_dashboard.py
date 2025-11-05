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
import json
import socket
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


def is_port_available(port: int) -> bool:
    """Verifica si un puerto está disponible."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        try:
            sock.bind(('localhost', port))
            return True
        except OSError:
            return False


def wait_for_server(port: int, timeout: int = 15) -> bool:
    """Espera a que el servidor esté escuchando en el puerto."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            try:
                sock.connect(('localhost', port))
                return True
            except (ConnectionRefusedError, OSError):
                time.sleep(0.5)
    return False


def create_initial_data_file():
    """Crea archivo JSON inicial vacío para evitar errores en el dashboard."""
    data_file = Path("live_battle_data.json")
    if not data_file.exists():
        initial_data = {
            "current_episode": 0,
            "total_episodes": 0,
            "agents": {}
        }
        data_file.write_text(json.dumps(initial_data, indent=2))
        console.print("[dim]📄 Archivo de datos inicial creado[/dim]")


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
    
    # Verificar que el puerto esté disponible
    if not is_port_available(8050):
        console.print("[red]✗ Error: Puerto 8050 ya está en uso[/red]")
        console.print("[yellow]  Intenta cerrar otras aplicaciones que usen el puerto 8050[/yellow]")
        return None
    
    # Crear archivo de datos inicial
    create_initial_data_file()
    
    # Ejecutar el dashboard en un proceso separado
    dashboard_path = Path("rmsa_demo_live/live_dashboard.py")
    if not dashboard_path.exists():
        console.print(f"[red]✗ Error: No se encuentra {dashboard_path}[/red]")
        return None
    
    process = subprocess.Popen(
        [sys.executable, str(dashboard_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    # Esperar a que el servidor realmente inicie (máximo 15 segundos)
    console.print("[dim]⏳ Esperando a que el servidor inicie...[/dim]")
    
    if wait_for_server(8050, timeout=15):
        console.print("[green]✓ Dashboard server iniciado correctamente en http://localhost:8050[/green]")
        return process
    else:
        # Si no se pudo conectar, mostrar los errores
        console.print("[red]✗ Error: El dashboard no pudo iniciarse[/red]")
        
        # Intentar obtener errores del proceso
        try:
            stdout, stderr = process.communicate(timeout=1)
            if stderr:
                console.print(f"[red]Error del dashboard:[/red]\n{stderr}")
        except subprocess.TimeoutExpired:
            pass
        
        process.kill()
        return None


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
    
    if dashboard_process is None:
        console.print("\n[red]✗ No se pudo iniciar el dashboard. Abortando...[/red]")
        console.print("[yellow]💡 Sugerencias:[/yellow]")
        console.print("   1. Verifica que el puerto 8050 esté libre")
        console.print("   2. Ejecuta: [cyan]python rmsa_demo_live/live_dashboard.py[/cyan] para ver errores")
        console.print("   3. Revisa que todas las dependencias estén instaladas: [cyan]pip install dash plotly[/cyan]")
        return
    
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
        if dashboard_process:
            dashboard_process.terminate()
            dashboard_process.wait()
        console.print("[green]✓ Dashboard server detenido[/green]")
    
    console.print("\n[bold green]🎉 Sesión completa finalizada![/bold green]\n")


if __name__ == "__main__":
    main()
