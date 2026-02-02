"""Web server for browsing and rendering Markdown files with syntax highlighting."""

import html
import urllib.parse
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from pygments import highlight
from pygments.formatters.html import HtmlFormatter
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.special import TextLexer

FORMATTER = HtmlFormatter(style="monokai")
CSS = FORMATTER.get_style_defs(".highlight")


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

TEMPLATE = """<!doctype html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<style>
body {{ font-family: system-ui, sans-serif; max-width: 50em; margin: 2em auto; padding: 0 1em; background: #1a1a2e; color: #e0e0e0; }}
a {{ color: #7eb8da; }}
pre {{ background: #16213e; padding: 1em; overflow-x: auto; border-radius: 4px; }}
code {{ background: #16213e; padding: 0.2em 0.4em; border-radius: 3px; }}
pre code {{ background: none; padding: 0; }}
table {{ border-collapse: collapse; }} td, th {{ border: 1px solid #444; padding: 0.4em 0.8em; }}
nav {{ margin-bottom: 1.5em; padding-bottom: 0.5em; border-bottom: 1px solid #333; }}
.dir::before {{ content: "📁 "; }} .file::before {{ content: "📄 "; }} .md::before {{ content: "📝 "; }}
{css}
</style><title>{title}</title></head><body><nav>{nav}</nav>{body}</body></html>"""


def breadcrumbs(rel: Path) -> str:
    parts = [f'<a href="/">~</a>']
    accum = Path()
    for p in rel.parts:
        accum = accum / p
        parts.append(f'<a href="/{accum}/">{html.escape(p)}</a>')
    return " / ".join(parts)


class Handler(SimpleHTTPRequestHandler):
    root: Path

    def do_GET(self):
        path = urllib.parse.unquote(self.path.split("?")[0])
        rel = Path(path.lstrip("/"))
        full = (self.root / rel).resolve()
        if not str(full).startswith(str(self.root.resolve())):
            self.send_error(403)
            return
        if full.is_dir():
            self.serve_dir(rel, full)
        elif full.is_file() and full.suffix == ".md":
            self.serve_md(rel, full)
        elif full.is_file():
            self.serve_raw(rel, full)
        else:
            self.send_error(404)

    def respond(self, content: str):
        data = content.encode()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def serve_dir(self, rel: Path, full: Path):
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
        page = TEMPLATE.format(
            css=CSS, title=str(rel) or "~", nav=breadcrumbs(rel), body=body
        )
        self.respond(page)

    def serve_md(self, rel: Path, full: Path):
        body = md.render(full.read_text())
        page = TEMPLATE.format(
            css=CSS, title=full.name, nav=breadcrumbs(rel.parent), body=body
        )
        self.respond(page)

    def serve_raw(self, rel: Path, full: Path):
        try:
            lexer = get_lexer_by_name(full.suffix.lstrip("."))
        except Exception:
            try:
                lexer = guess_lexer(full.read_text())
            except Exception:
                lexer = None
        if lexer:
            body = highlight(full.read_text(), lexer, FORMATTER)
            page = TEMPLATE.format(
                css=CSS, title=full.name, nav=breadcrumbs(rel.parent), body=body
            )
            self.respond(page)
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            data = full.read_bytes()
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)


def make_handler(root: Path):
    """Create a Handler class with the given root directory."""

    class ConfiguredHandler(Handler):
        pass

    ConfiguredHandler.root = root
    return ConfiguredHandler


def run_server(root: Path, bind: str, port: int):
    """Run the foam-web server."""
    print(f"Serving {root} on http://{bind}:{port}")
    HTTPServer((bind, port), make_handler(root)).serve_forever()


if __name__ == "__main__":
    from foam_web.cli import main

    main()
