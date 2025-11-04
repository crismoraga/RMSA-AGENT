"""Quick test script to verify RMSA environment works correctly."""
import sys

import numpy as np
from rich.console import Console
from rich.table import Table

import rmsa_environment
from config import ENVIRONMENT
from environment import EnvironmentFactory

console = Console()


def test_environment():
    """Test basic environment functionality."""
    console.print("\n[bold cyan]🧪 Testing RMSA Environment...[/bold cyan]\n")

    factory = EnvironmentFactory(base_kwargs=ENVIRONMENT.as_dict())
    env = factory.make(seed=42)

    console.print(f"✓ Environment created: {env.spec.id}")
    console.print(f"✓ Observation space: {env.observation_space.shape}")
    console.print(f"✓ Action space: {env.action_space.n} actions")

    # Reset
    obs, info = env.reset(seed=42)
    console.print(f"\n✓ Environment reset successful")
    console.print(f"  - Observation shape: {obs.shape}")
    console.print(f"  - Info keys: {list(info.keys())}")

    # Run a few steps
    console.print(f"\n[bold yellow]Running 10 random steps...[/bold yellow]")

    metrics = {
        "allocated": 0,
        "blocked": 0,
    }

    for i in range(10):
        action = env.action_space.sample()
        obs, reward, terminated, truncated, info = env.step(action)

        if info["allocation_success"]:
            metrics["allocated"] += 1
        else:
            metrics["blocked"] += 1

        console.print(
            f"  Step {i+1}: Action={action}, Reward={reward:+.1f}, "
            f"Allocated={info['allocation_success']}, "
            f"Connection={info.get('connection_label', 'N/A')}"
        )

    # Summary table
    table = Table(title="Test Summary")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="green")

    table.add_row("Allocated", str(metrics["allocated"]))
    table.add_row("Blocked", str(metrics["blocked"]))
    table.add_row("Acceptance Rate", f"{metrics['allocated']/10:.1%}")
    table.add_row("Blocking Probability", f"{metrics['blocked']/10:.1%}")

    console.print()
    console.print(table)
    console.print("\n[bold green]✓ Environment test PASSED![/bold green]\n")

    env.close()
    return True


def test_config():
    """Test configuration loading."""
    console.print("\n[bold cyan]⚙️  Testing Configuration...[/bold cyan]\n")

    from config import (
        DEFAULT_AGENT_CONFIG,
        DEFAULT_TRAINING,
        DEMO,
        OPTIMIZED_AGENT_CONFIG,
        OPTIMIZED_TRAINING,
    )

    config_table = Table(title="Agent Configurations")
    config_table.add_column("Parameter", style="cyan")
    config_table.add_column("Default", style="blue")
    config_table.add_column("Optimized", style="green")

    config_table.add_row(
        "Architecture",
        f"{len(DEFAULT_AGENT_CONFIG.net_arch)} layers",
        f"{len(OPTIMIZED_AGENT_CONFIG.net_arch)} layers",
    )
    config_table.add_row(
        "Neurons per layer",
        str(DEFAULT_AGENT_CONFIG.net_arch[0]),
        str(OPTIMIZED_AGENT_CONFIG.net_arch[0]),
    )
    config_table.add_row(
        "Learning Rate",
        f"{DEFAULT_AGENT_CONFIG.learning_rate:.1e}",
        f"{OPTIMIZED_AGENT_CONFIG.learning_rate:.1e}",
    )
    config_table.add_row(
        "Activation", DEFAULT_AGENT_CONFIG.activation, OPTIMIZED_AGENT_CONFIG.activation
    )
    config_table.add_row(
        "Reward Function",
        DEFAULT_AGENT_CONFIG.reward_id,
        OPTIMIZED_AGENT_CONFIG.reward_id,
    )
    config_table.add_row(
        "Dropout", f"{DEFAULT_AGENT_CONFIG.dropout}", f"{OPTIMIZED_AGENT_CONFIG.dropout}"
    )
    config_table.add_row(
        "Training Steps",
        f"{DEFAULT_TRAINING.timesteps:,}",
        f"{OPTIMIZED_TRAINING.timesteps:,}",
    )

    console.print(config_table)
    console.print("\n[bold green]✓ Configuration test PASSED![/bold green]\n")
    return True


def main():
    """Run all tests."""
    console.print("[bold magenta]═" * 60)
    console.print("[bold magenta]   RMSA DEMO - Pre-Training Verification Test Suite")
    console.print("[bold magenta]═" * 60)

    try:
        if not test_config():
            console.print("[bold red]✗ Configuration test FAILED![/bold red]")
            return False

        if not test_environment():
            console.print("[bold red]✗ Environment test FAILED![/bold red]")
            return False

        console.print("[bold green]═" * 60)
        console.print("[bold green]   ✓ ALL TESTS PASSED - Ready for Training!")
        console.print("[bold green]═" * 60)
        console.print("\n[yellow]Next steps:[/yellow]")
        console.print("  1. Train agents: [cyan]python trainer.py --default --optimized[/cyan]")
        console.print("  2. Run demo: [cyan]python demo.py[/cyan]\n")

        return True

    except Exception as e:
        console.print(f"\n[bold red]✗ Test failed with error:[/bold red]")
        console.print(f"[red]{type(e).__name__}: {e}[/red]\n")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
