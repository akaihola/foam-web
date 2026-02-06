"""WSGI application factory for foam-web."""

from pathlib import Path

from foam_web.styles import LIVERELOAD_SCRIPT
from foam_web.views import serve_dir, serve_md, serve_raw


def make_app(root: Path, port: int = 8000):
    """Create a WSGI application for serving the foam-web content."""

    def _livereload_script() -> str:
        return LIVERELOAD_SCRIPT.format(port=port)

    def app(environ, start_response):
        path = environ.get("PATH_INFO", "/")
        # Skip livereload.js - let the Server handle it
        if path == "/livereload.js":
            return None

        rel = Path(path.lstrip("/"))
        full = (root / rel).resolve()

        # Security check
        if not str(full).startswith(str(root.resolve())):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]

        livereload = _livereload_script()

        if full.is_dir():
            content = serve_dir(rel, full, root=root, livereload=livereload)
            data = content.encode("utf-8")
            start_response(
                "200 OK",
                [
                    ("Content-Type", "text/html; charset=utf-8"),
                    ("Content-Length", str(len(data))),
                ],
            )
            return [data]
        elif full.is_file() and full.suffix == ".md":
            content = serve_md(rel, full, root=root, livereload=livereload)
            data = content.encode("utf-8")
            start_response(
                "200 OK",
                [
                    ("Content-Type", "text/html; charset=utf-8"),
                    ("Content-Length", str(len(data))),
                ],
            )
            return [data]
        elif full.is_file():
            content = serve_raw(rel, full, root=root, livereload=livereload)
            if content:
                data = content.encode("utf-8")
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "text/html; charset=utf-8"),
                        ("Content-Length", str(len(data))),
                    ],
                )
                return [data]
            else:
                # Serve raw file
                data = full.read_bytes()
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "text/plain; charset=utf-8"),
                        ("Content-Length", str(len(data))),
                    ],
                )
                return [data]
        else:
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]

    return app
