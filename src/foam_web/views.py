"""View functions for rendering directories, markdown, and raw files."""

import html
from pathlib import Path

from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer

from foam_web.rendering import md
from foam_web.styles import FORMATTER, render_page


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
    """Build breadcrumb navigation HTML."""
    parts = ['<a href="/">~</a>']
    accum = Path()
    for p in rel.parts:
        accum = accum / p
        parts.append(f'<a href="/{accum}/">{html.escape(p)}</a>')
    return " / ".join(parts)


def serve_dir(rel: Path, full: Path, *, root: Path, livereload: str = "") -> str:
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
        livereload=livereload,
        sidebar=build_file_tree(root, current=rel),
    )


def serve_md(rel: Path, full: Path, *, root: Path, livereload: str = "") -> str:
    """Render a markdown file."""
    body = md.render(full.read_text(encoding="utf-8"))
    return render_page(
        title=full.name,
        nav=breadcrumbs(rel.parent),
        body=body,
        livereload=livereload,
        sidebar=build_file_tree(root, current=rel),
    )


def serve_raw(rel: Path, full: Path, *, root: Path, livereload: str = "") -> str | None:
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
            livereload=livereload,
            sidebar=build_file_tree(root, current=rel),
        )
    return None
