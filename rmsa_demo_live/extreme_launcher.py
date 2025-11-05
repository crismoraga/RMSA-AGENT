# 🔥 EXTREME BATTLE LAUNCHER - Ejecuta y Genera Todo Automáticamente

"""
Script de conveniencia para ejecutar batalla extrema completa con todas las visualizaciones.
"""

import subprocess
import sys
import time
from pathlib import Path

def print_banner():
    banner = """
╔═══════════════════════════════════════════════════════════════════════╗
║                                                                       ║
║            🔥 EXTREME BATTLE ROYALE LAUNCHER 🔥                      ║
║                                                                       ║
║  Este script ejecutará automáticamente:                              ║
║                                                                       ║
║  ✅ Battle Royale en modo EXTREME (USNET, 95% load, 100 slots)       ║
║  ✅ 2000 episodios de evaluación exhaustiva                           ║
║  ✅ 11 visualizaciones interactivas (Plotly + NetworkX)               ║
║  ✅ Análisis estadístico completo (ANOVA, t-tests)                    ║
║                                                                       ║
║  Duración estimada: 10-15 minutos                                     ║
║                                                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
"""
    print(banner)

def check_models_exist():
    """Verifica que todos los modelos estén entrenados."""
    models_dir = Path("models")
    expected_models = [
        "default_agent.zip",
        "ultho_agent.zip",
        "hyperq_agent.zip",
        "bohamiann_agent.zip",
        "deeprmsa_qot_agent.zip",
        "meta_learning_agent.zip",
    ]
    
    missing = []
    for model in expected_models:
        if not (models_dir / model).exists():
            missing.append(model)
    
    if missing:
        print(f"\n❌ ERROR: Modelos faltantes: {', '.join(missing)}")
        print("\n💡 Ejecuta primero el entrenamiento:")
        print("   python rmsa_demo_live/trainer.py --agents CONTROL ULTHO HYPERQ-OPT BOHAMIANN DEEPRMSA-QOT META-LEARNING")
        return False
    
    print("\n✅ Todos los modelos entrenados encontrados!")
    return True

def run_extreme_battle():
    """Ejecuta la batalla en modo EXTREME."""
    print("\n🔥 Iniciando Battle Royale en modo EXTREME...")
    print("   Topología: USNET (24 nodos, 43 enlaces)")
    print("   Carga: 95% (ultra-alta)")
    print("   Espectro: 100 slots (reducido)")
    print("   Episodios: 2000")
    print()
    
    cmd = [
        sys.executable,
        "rmsa_demo_live/demo_orchestrator.py",
        "--extreme",
    ]
    
    result = subprocess.run(cmd)
    return result.returncode == 0

def open_visualizations():
    """Abre las visualizaciones principales en el navegador."""
    print("\n📊 Abriendo visualizaciones en el navegador...")
    
    viz_files = [
        "presentation_viz/ranking_table.html",
        "presentation_viz/radar_chart.html",
        "presentation_viz/box_plot_comparison.html",
        "dashboards/comprehensive_analysis.html",
    ]
    
    for viz_file in viz_files:
        viz_path = Path(viz_file)
        if viz_path.exists():
            try:
                # Windows
                import os
                os.startfile(str(viz_path))
                time.sleep(0.5)  # Evitar abrir todos a la vez
            except:
                print(f"   → {viz_file}")
        else:
            print(f"   ⚠ No encontrado: {viz_file}")

def main():
    print_banner()
    
    # Paso 1: Verificar modelos
    if not check_models_exist():
        sys.exit(1)
    
    # Paso 2: Ejecutar batalla extrema
    success = run_extreme_battle()
    
    if not success:
        print("\n❌ La batalla falló. Revisa los errores arriba.")
        sys.exit(1)
    
    # Paso 3: Mostrar resumen
    print("\n" + "="*80)
    print("🎉 EXTREME BATTLE COMPLETADA EXITOSAMENTE! 🎉")
    print("="*80)
    
    print("\n📁 Visualizaciones generadas:")
    print("\n📊 Dashboards Principales:")
    print("   • dashboards/comprehensive_analysis.html")
    print("   • dashboards/statistical_tests.html")
    
    print("\n🎨 Visualizaciones para Presentación:")
    print("   • presentation_viz/ranking_table.html")
    print("   • presentation_viz/radar_chart.html")
    print("   • presentation_viz/box_plot_comparison.html")
    print("   • presentation_viz/violin_plot.html")
    print("   • presentation_viz/correlation_heatmap.html")
    print("   • presentation_viz/3d_scatter.html")
    print("   • presentation_viz/time_series.html")
    
    print("\n🌐 Visualizaciones de Red:")
    print("   • network_viz/all_topologies_comparison.html")
    
    # Paso 4: Abrir visualizaciones
    print()
    response = input("¿Abrir visualizaciones principales en el navegador? (s/n): ")
    if response.lower() in ['s', 'si', 'yes', 'y']:
        open_visualizations()
    
    print("\n✨ ¡Listo! Usa los HTML generados para tu presentación.")

if __name__ == "__main__":
    main()
