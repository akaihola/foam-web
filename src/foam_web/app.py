"""WSGI application factory for foam-web."""

import mimetypes
from pathlib import Path
from urllib.parse import quote

from foam_web.styles import LIVERELOAD_SCRIPT
from foam_web.views import serve_dir, serve_md, serve_raw


def make_app(root: Path, port: int = 8000):
    """Create a WSGI application for serving the foam-web content."""

    def _livereload_script() -> str:
        return LIVERELOAD_SCRIPT.format(port=port)

    def app(environ, start_response):
        raw_path = environ.get("PATH_INFO", "/")
        # Skip livereload.js - let the Server handle it
        if raw_path == "/livereload.js":
            return None

        # Tornado's WSGIContainer already URL-decodes PATH_INFO to raw bytes,
        # then encodes as latin-1 per PEP 3333. Reverse that to get UTF-8.
        path = raw_path.encode("latin-1").decode("utf-8")
        rel = Path(path.lstrip("/"))
        full = (root / rel).resolve()

        # Security check
        if not str(full).startswith(str(root.resolve())):
            start_response("403 Forbidden", [("Content-Type", "text/plain")])
            return [b"Forbidden"]

        # Redirect /path/file.md → /path/file
        if full.suffix == ".md" and full.is_file():
            new_path = quote(path[:-3])  # Strip ".md", percent-encode
            start_response(
                "301 Moved Permanently",
                [("Location", new_path), ("Content-Type", "text/plain")],
            )
            return [b"Moved"]

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
                # Serve raw file with correct MIME type
                data = full.read_bytes()
                mime_type, _ = mimetypes.guess_type(full.name)
                if mime_type is None:
                    mime_type = "application/octet-stream"
                content_type = (
                    f"{mime_type}; charset=utf-8"
                    if mime_type.startswith("text/")
                    else mime_type
                )
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", content_type),
                        ("Content-Length", str(len(data))),
                    ],
                )
                return [data]
        else:
            # Try appending .md for extensionless markdown URLs
            md_full = full.with_suffix(".md")
            if md_full.is_file():
                # Re-run security check on the .md path
                if not str(md_full.resolve()).startswith(str(root.resolve())):
                    start_response("403 Forbidden", [("Content-Type", "text/plain")])
                    return [b"Forbidden"]
                md_rel = rel.with_suffix(".md")
                content = serve_md(md_rel, md_full, root=root, livereload=livereload)
                data = content.encode("utf-8")
                start_response(
                    "200 OK",
                    [
                        ("Content-Type", "text/html; charset=utf-8"),
                        ("Content-Length", str(len(data))),
                    ],
                )
                return [data]
            start_response("404 Not Found", [("Content-Type", "text/plain")])
            return [b"Not Found"]

    return app
