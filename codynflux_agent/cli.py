# Copyright (c) 2025 ByteDance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

"""Command Line Interface for Codynflux Agent."""

import asyncio
import os
import sys
import traceback
from pathlib import Path

import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from codynflux_agent.utils.cli_console import CLIConsole

from .agent import CodynfluxAgent
from .utils.config import Config, load_config

# Load environment variables
_ = load_dotenv()

console = Console()


def create_agent(config: Config) -> CodynfluxAgent:
    """
    create_agent creates a Codynflux Agent with the specified configuration.
    Args:
        config: Agent configuration. It is expected that the config comes from load_config.
    Return:
        CodynfluxAgent object
    """
    try:
        # Create agent
        agent = CodynfluxAgent(config)
        return agent

    except Exception as e:
        console.print(f"[red]Error creating agent: {e}[/red]")
        console.print(traceback.format_exc())
        sys.exit(1)


# Display functions moved to agent/base.py for real-time progress display


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """Codynflux Agent - LLM-based agent for software engineering tasks."""
    pass


@cli.command()
@click.argument("task")
@click.option("--provider", "-p", help="LLM provider to use")
@click.option("--model", "-m", help="Specific model to use")
@click.option("--model-base-url", help="Base URL for the model API")
@click.option("--api-key", "-k", help="API key (or set via environment variable)")
@click.option("--max-steps", help="Maximum number of execution steps", type=int)
@click.option("--working-dir", "-w", help="Working directory for the agent")
@click.option("--must-patch", "-mp", is_flag=True, help="Whether to patch the code")
@click.option("--config-file", help="Path to configuration file", default="codynflux_config.json")
@click.option("--trajectory-file", "-t", help="Path to save trajectory file")
@click.option("--patch-path", "-pp", help="Path to patch file")
@click.option("--dtdd-mode", "-dtdd", is_flag=True, help="Enable DTDD (Document-Driven Development) workflow mode")
@click.option("--multi-agent-mode", "-ma", is_flag=True, help="Enable Multi-Agent coordination system for complex tasks")
def run(
    task: str,
    patch_path: str,
    provider: str | None = None,
    model: str | None = None,
    model_base_url: str | None = None,
    api_key: str | None = None,
    max_steps: int | None = None,
    working_dir: str | None = None,
    must_patch: bool = False,
    config_file: str = "codynflux_config.json",
    trajectory_file: str | None = None,
    dtdd_mode: bool = False,
    multi_agent_mode: bool = False,
):
    """
    Run is the main function of codynflux. It runs a task using Codynflux Agent.
    Args:
        tasks: the task that you want your agent to solve. This is required to be in the input
        model: the model expected to be use
        working_dir: the working directory of the agent. This should be set either in cli or inf the config file (codynflux_config.json)
        dtdd_mode: Enable DTDD (Document-Driven Development) workflow for systematic development
        multi_agent_mode: Enable Multi-Agent coordination system for complex tasks

    Return:
        None (it is expected to be ended after calling the run function)
    """

    # Change working directory if specified
    if not working_dir:
        working_dir = os.getcwd()
        try:
            os.chdir(working_dir)
            console.print(f"[blue]Changed working directory to: {working_dir}[/blue]")
        except Exception as e:
            console.print(f"[red]Error changing directory: {e}[/red]")
            sys.exit(1)

    task_path = Path(task)
    if task_path.exists() and task_path.is_file():
        task = task_path.read_text()

    config = load_config(config_file, provider, model, model_base_url, api_key, max_steps)

    # Create agent based on mode
    if multi_agent_mode:
        # Import the SixAgentCodynfluxAgent for multi-agent coordination
        from .agent.six_agent_system import SixAgentCodynfluxAgent
        agent = SixAgentCodynfluxAgent(config)
    else:
        # Create standard agent
        agent: CodynfluxAgent = create_agent(config)

    # Set up trajectory recording
    trajectory_path = None
    if trajectory_file:
        trajectory_path = agent.setup_trajectory_recording(trajectory_file)
    else:
        trajectory_path = agent.setup_trajectory_recording()

    # Create CLI Console
    cli_console = CLIConsole(config)
    cli_console.print_task_details(
        task,
        working_dir,
        config.default_provider,
        config.model_providers[config.default_provider].model,
        config.max_steps,
        config_file,
        trajectory_path,
        dtdd_mode,
        multi_agent_mode,
    )

    # Set up agent console (only for standard agent)
    if not multi_agent_mode:
        agent.set_cli_console(cli_console)

    try:
        task_args = {
            "project_path": working_dir,
            "issue": task,
            "must_patch": "true" if must_patch else "false",
            "patch_path": patch_path or "",
            "dtdd_mode": "true" if dtdd_mode else "false",
            "multi_agent_mode": "true" if multi_agent_mode else "false",
        }
        agent.new_task(task, task_args)
        _ = asyncio.run(agent.execute_task())

        console.print(f"\n[green]Trajectory saved to: {trajectory_path}[/green]")

    except KeyboardInterrupt:
        console.print("\n[yellow]Task execution interrupted by user[/yellow]")
        if trajectory_path:
            console.print(f"[blue]Partial trajectory saved to: {trajectory_path}[/blue]")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[red]Unexpected error: {e}[/red]")
        console.print(traceback.format_exc())
        if trajectory_path:
            console.print(f"[blue]Trajectory saved to: {trajectory_path}[/blue]")
        sys.exit(1)


@cli.command()
@click.option("--provider", "-p", help="LLM provider to use")
@click.option("--model", "-m", help="Specific model to use")
@click.option("--model-base-url", help="Base URL for the model API")
@click.option("--api-key", "-k", help="API key (or set via environment variable)")
@click.option("--config-file", help="Path to configuration file", default="codynflux_config.json")
@click.option("--max-steps", help="Maximum number of execution steps", type=int, default=20)
@click.option("--trajectory-file", "-t", help="Path to save trajectory file")
def interactive(
    provider: str | None = None,
    model: str | None = None,
    model_base_url: str | None = None,
    api_key: str | None = None,
    config_file: str = "codynflux_config.json",
    max_steps: int | None = None,
    trajectory_file: str | None = None,
):
    """
    This function starts an interactive session with Codynflux Agent.
    Args:
        tasks: the task that you want your agent to solve. This is required to be in the input
    """
    config = load_config(config_file, provider, model, model_base_url, api_key, max_steps=max_steps)

    console.print(
        Panel(
            f"""[bold]Welcome to Codynflux Agent Interactive Mode![/bold]
    [bold]Provider:[/bold] {config.default_provider}
    [bold]Model:[/bold] {config.model_providers[config.default_provider].model}
    [bold]Max Steps:[/bold] {config.max_steps}
    [bold]Config File:[/bold] {config_file}""",
            title="Interactive Mode",
            border_style="green",
        )
    )

    # Create agent
    agent = create_agent(config)

    while True:
        try:
            console.print("\n[bold blue]Task:[/bold blue] ", end="")
            task = input()

            if task.lower() in ["exit", "quit"]:
                console.print("[green]Goodbye![/green]")
                break

            if task.lower() == "help":
                console.print(
                    Panel(
                        """[bold]Available Commands:[/bold]

• Type any task description to execute it
• 'status' - Show agent status
• 'clear' - Clear the screen
• 'exit' or 'quit' - End the session""",
                        title="Help",
                        border_style="yellow",
                    )
                )
                continue

            console.print("\n[bold blue]Working Directory:[/bold blue] ", end="")
            working_dir = input()

            if task.lower() == "status":
                console.print(
                    Panel(
                        f"""[bold]Provider:[/bold] {agent.llm_client.provider.value}
    [bold]Model:[/bold] {config.model_providers[config.default_provider].model}
    [bold]Available Tools:[/bold] {len(agent.tools)}
    [bold]Config File:[/bold] {config_file}
    [bold]Working Directory:[/bold] {os.getcwd()}""",
                        title="Agent Status",
                        border_style="blue",
                    )
                )
                continue

            if task.lower() == "clear":
                console.clear()
                continue

            # Set up trajectory recording for this task
            trajectory_path = agent.setup_trajectory_recording(trajectory_file)

            console.print(f"[blue]Trajectory will be saved to: {trajectory_path}[/blue]")

            task_args = {
                "project_path": working_dir,
                "issue": task,
                "must_patch": "false",
            }

            # Execute the task
            console.print(f"\n[blue]Executing task: {task}[/blue]")
            agent.new_task(task, task_args)

            # Configure agent for progress display
            _ = asyncio.run(agent.execute_task())

            console.print(f"\n[green]Trajectory saved to: {trajectory_path}[/green]")

        except KeyboardInterrupt:
            console.print("\n[yellow]Use 'exit' or 'quit' to end the session[/yellow]")
        except EOFError:
            console.print("\n[green]Goodbye![/green]")
            break
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")


@cli.command()
@click.option("--config-file", help="Path to configuration file", default="codynflux_config.json")
def show_config(config_file: str):
    """Show current configuration settings."""
    config_path = Path(config_file)
    if not config_path.exists():
        console.print(
            Panel(
                f"""[yellow]No configuration file found at: {config_file}[/yellow]

Using default settings and environment variables.""",
                title="Configuration Status",
                border_style="yellow",
            )
        )

    config = Config(config_file)

    # Display general settings
    general_table = Table(title="General Settings")
    general_table.add_column("Setting", style="cyan")
    general_table.add_column("Value", style="green")

    general_table.add_row("Default Provider", str(config.default_provider or "Not set"))
    general_table.add_row("Max Steps", str(config.max_steps or "Not set"))

    console.print(general_table)

    # Display provider settings
    for provider_name, provider_config in config.model_providers.items():
        provider_table = Table(title=f"{provider_name.title()} Configuration")
        provider_table.add_column("Setting", style="cyan")
        provider_table.add_column("Value", style="green")

        provider_table.add_row("Model", provider_config.model or "Not set")
        provider_table.add_row("API Key", "Set" if provider_config.api_key else "Not set")
        provider_table.add_row("Max Tokens", str(provider_config.max_tokens))
        provider_table.add_row("Temperature", str(provider_config.temperature))
        provider_table.add_row("Top P", str(provider_config.top_p))

        if provider_name == "anthropic":
            provider_table.add_row("Top K", str(provider_config.top_k))

        console.print(provider_table)


@cli.command()
def tools():
    """Show available tools and their descriptions."""
    from .tools import tools_registry

    tools_table = Table(title="Available Tools")
    tools_table.add_column("Tool Name", style="cyan")
    tools_table.add_column("Description", style="green")

    for tool_name in tools_registry:
        try:
            tool = tools_registry[tool_name]()
            tools_table.add_row(tool.name, tool.description)
        except Exception as e:
            tools_table.add_row(tool_name, f"[red]Error loading: {e}[/red]")

    console.print(tools_table)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
