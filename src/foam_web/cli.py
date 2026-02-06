"""Command-line interface for foam-web."""

import os
from pathlib import Path
from typing import Annotated, Optional

import hupper
import typer

from foam_web.serve import run_server

app = typer.Typer(
    help="A simple web server for browsing and rendering Markdown files with syntax highlighting.",
    add_completion=False,
)


@app.command()
def serve(
    directory: Annotated[
        Optional[Path],
        typer.Argument(
            help="Directory to serve (default: current directory, or SERVE_ROOT env var)",
        ),
    ] = None,
    port: Annotated[
        int,
        typer.Option("-p", "--port", help="Port to listen on"),
    ] = int(os.environ.get("SERVE_PORT", "8080")),
    bind: Annotated[
        str,
        typer.Option("-b", "--bind", help="Address to bind to"),
    ] = os.environ.get("SERVE_BIND", "0.0.0.0"),
):
    """Start the foam-web server."""
    root = (directory or Path(os.environ.get("SERVE_ROOT", Path.cwd()))).resolve()

    # Start process reloader to restart server when .py files change
    restarted = hupper.is_active()
    reloader = hupper.start_reloader("foam_web.cli.main")
    app_dir = Path(__file__).parent
    for py_file in app_dir.glob("*.py"):
        reloader.watch_files([str(py_file)])

    run_server(root, bind, port, restarted=restarted)


def main():
    """Entry point for the foam-web CLI."""
    app()
