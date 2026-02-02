"""Command-line interface for foam-web."""

import os
from pathlib import Path
from typing import Annotated, Optional

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
    run_server(root, bind, port)


def main():
    """Entry point for the foam-web CLI."""
    app()
