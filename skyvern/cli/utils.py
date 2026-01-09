import asyncio
import logging
import os
import shutil
import sys

import typer
from dotenv import load_dotenv, set_key

from skyvern.cli.console import console
from skyvern.utils.env_paths import resolve_backend_env_path, resolve_frontend_env_path


def sync_frontend_api_key() -> bool:
    """Sync the SKYVERN_API_KEY from backend .env to frontend .env.

    Returns:
        True if sync was successful, False otherwise.
    """
    frontend_env_path = resolve_frontend_env_path()
    if frontend_env_path is None:
        console.print("[yellow]Frontend directory not found, skipping API key sync.[/yellow]")
        return False

    frontend_dir = frontend_env_path.parent
    if not frontend_env_path.exists():
        example_env = frontend_dir / ".env.example"
        if example_env.exists():
            console.print("[bold blue]Setting up frontend .env file...[/bold blue]")
            shutil.copy(example_env, frontend_env_path)
            console.print("✅ [green]Successfully set up frontend .env file[/green]")
        else:
            console.print("[yellow]Frontend .env.example not found, skipping API key sync.[/yellow]")
            return False

    backend_env_path = resolve_backend_env_path()
    if not backend_env_path.exists():
        console.print(f"[yellow]Backend .env file not found at {backend_env_path}, skipping API key sync.[/yellow]")
        return False

    load_dotenv(backend_env_path)
    skyvern_api_key = os.getenv("SKYVERN_API_KEY")
    if skyvern_api_key:
        set_key(frontend_env_path, "VITE_SKYVERN_API_KEY", skyvern_api_key)
        console.print("🔑 [green]Synced SKYVERN_API_KEY to frontend .env[/green]")
        return True
    else:
        console.print("[yellow]SKYVERN_API_KEY not found in backend .env, skipping sync.[/yellow]")
        return False


async def start_services(server_only: bool = False) -> None:
    """Start Skyvern services in the background.

    Args:
        server_only: If True, only start the server, not the UI.
    """
    if not server_only:
        sync_frontend_api_key()

    try:
        # Start server in the background
        server_process = await asyncio.create_subprocess_exec(
            sys.executable, "-m", "skyvern.cli.commands", "run", "server"
        )

        # Give server a moment to start
        await asyncio.sleep(2)

        if not server_only:
            # Start UI in the background
            ui_process = await asyncio.create_subprocess_exec(sys.executable, "-m", "skyvern.cli.commands", "run", "ui")

        console.print("\n🎉 [bold green]Skyvern is now running![/bold green]")
        console.print("🌐 [bold]Access the UI at:[/bold] [cyan]http://localhost:8080[/cyan]")
        console.print(f"🔑 [bold]Your API key is in {resolve_backend_env_path()} as SKYVERN_API_KEY[/bold]")

        # Wait for processes to complete (they won't unless killed)
        if not server_only:
            await asyncio.gather(server_process.wait(), ui_process.wait())
        else:
            await server_process.wait()

    except Exception as e:
        console.print(f"[bold red]Error starting services: {str(e)}[/bold red]")
        logging.error("Startup failed", exc_info=True)
        raise typer.Exit(1)
