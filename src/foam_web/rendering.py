"""Markdown rendering and syntax highlighting configuration."""

from markdown_it import MarkdownIt
from mdit_py_plugins.front_matter import front_matter_plugin
from pygments import highlight
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.lexers.special import TextLexer

from foam_web.styles import FORMATTER


def highlighter(code, lang, _attrs):
    """Highlight a code block using Pygments."""
    try:
        lexer = get_lexer_by_name(lang) if lang else guess_lexer(code)
    except Exception:
        lexer = TextLexer()
    return highlight(code, lexer, FORMATTER)


md = MarkdownIt("commonmark", {"highlight": highlighter}).enable(
    ["table", "strikethrough"]
)
front_matter_plugin(md)
