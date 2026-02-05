"""Web server for browsing and rendering Markdown files with syntax highlighting."""

import html
from pathlib import Path

from livereload import Server
from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.special import TextLexer

from foam_web.styles import FORMATTER, LIVERELOAD_SCRIPT, render_page


def highlighter(code, lang, _attrs):
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except Exception:
        lexer = TextLexer()
    return highlight(code, lexer, FORMATTER)


md = MarkdownIt("commonmark", {"highlight": highlighter}).enable(
    ["table", "strikethrough"]
)
front_matter_plugin(md)

# Global state for the server configuration
_root: Path = Path(".")
_port: int = 8000


def build_file_tree(root: Path, current: Path | None = None, rel: Path = Path()) -> str:
    """Build a nested HTML file tree for the sidebar."""
    entries = sorted(root.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    items = []
    for e in entries:
        if e.name.startswith("."):
            continue
        name = html.escape(e.name)
        entry_rel = rel / e.name
        if e.is_dir():
            children = build_file_tree(e, current, entry_rel)
            href = f"/{entry_rel}/"
            is_current = current and current == entry_rel
            dir_cls = "dir current" if is_current else "dir"
            items.append(
                f'<li class="collapsed"><span class="toggle">▼</span>'
                f'<a class="{dir_cls}" href="{href}">{name}</a>{children}</li>'
            )
        else:
            href = f"/{entry_rel}"
            is_current = current and current == entry_rel
            cls = "md" if e.suffix == ".md" else "file"
            if is_current:
                cls += " current"
            items.append(f'<li><a class="{cls}" href="{href}">{name}</a></li>')
    return f"<ul>{''.join(items)}</ul>" if items else ""


def breadcrumbs(rel: Path) -> str:
    parts = ['<a href="/">~</a>']
    accum = Path()
    for p in rel.parts:
        accum = accum / p
        parts.append(f'<a href="/{accum}/">{html.escape(p)}</a>')
    return " / ".join(parts)


def _livereload_script() -> str:
    return LIVERELOAD_SCRIPT.format(port=_port)


def serve_dir(rel: Path, full: Path) -> str:
    """Render a directory listing."""
    entries = sorted(full.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
    items = []
    for e in entries:
        if e.name.startswith("."):
            continue
        name = html.escape(e.name)
        href = f"/{rel / e.name}/" if e.is_dir() else f"/{rel / e.name}"
        cls = "dir" if e.is_dir() else ("md" if e.suffix == ".md" else "file")
        items.append(f'<li><a class="{cls}" href="{href}">{name}</a></li>')
    body = f"<ul>{''.join(items)}</ul>" if items else "<p><em>empty</em></p>"
    return render_page(
        title=str(rel) or "~",
        nav=breadcrumbs(rel),
        body=body,
        livereload=_livereload_script(),
        sidebar=build_file_tree(_root, current=rel),
    )


def serve_md(rel: Path, full: Path) -> str:
    """Render a markdown file."""
    body = md.render(full.read_text(encoding="utf-8"))
    return render_page(
        title=full.name,
        nav=breadcrumbs(rel.parent),
        body=body,
        livereload=_livereload_script(),
        sidebar=build_file_tree(_root, current=rel),
    )


def serve_raw(rel: Path, full: Path) -> str | None:
    """Render a raw file with syntax highlighting, or None for plain text."""
    try:
        lexer = get_lexer_by_name(full.suffix.lstrip("."))
    except Exception:
        try:
            lexer = guess_lexer(full.read_text(encoding="utf-8"))
        except Exception:
            lexer = None
    if lexer:
        body = highlight(full.read_text(encoding="utf-8"), lexer, FORMATTER)
        return render_page(
            title=full.name,
            nav=breadcrumbs(rel.parent),
            body=body,
            livereload=_livereload_script(),
            sidebar=build_file_tree(_root, current=rel),
        )
    return None


def make_app(root: Path):
    """Create a WSGI application for serving the foam-web content."""

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

        if full.is_dir():
            content = serve_dir(rel, full)
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
            content = serve_md(rel, full)
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
            content = serve_raw(rel, full)
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


def run_server(root: Path, bind: str, port: int):
    """Run the foam-web server with live reload."""
    global _root, _port
    _root = root
    _port = port

    server = Server(make_app(root))

    # Watch all markdown files for changes
    server.watch(str(root / "**/*.md"))

    print(f"Serving {root} on http://{bind}:{port}")
    print("Live reload enabled - pages will refresh when .md files change")
    server.serve(host=bind, port=port, root=str(root))


if __name__ == "__main__":
    from foam_web.cli import main

    main()
