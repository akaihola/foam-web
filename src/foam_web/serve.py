"""Web server for browsing and rendering Markdown files with syntax highlighting."""

import threading
from pathlib import Path

from livereload import Server

from foam_web.app import make_app


def run_server(root: Path, bind: str, port: int, restarted: bool = False):
    """Run the foam-web server with live reload."""
    server = Server(make_app(root, port))

    # Watch all markdown files for changes (browser reload)
    server.watch(str(root / "**/*.md"))

    # After a hupper restart, trigger a browser reload once livereload.js reconnects
    if restarted:
        app_dir = Path(__file__).parent

        def _delayed_reload():
            import time

            time.sleep(1)
            server.watcher._changes.append((str(app_dir / "__init__.py"), None))

        threading.Thread(target=_delayed_reload, daemon=True).start()

    print(f"Serving {root} on http://{bind}:{port}")
    print(
        "Live reload enabled - browser refreshes on .md changes, server restarts on .py changes"
    )
    server.serve(host=bind, port=port, root=str(root))


if __name__ == "__main__":
    from foam_web.cli import main

    main()
