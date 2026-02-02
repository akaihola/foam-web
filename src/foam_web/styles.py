"""Styling module for foam-web with readable typography and colors."""

from pygments.formatters.html import HtmlFormatter

# Use a light, readable Pygments style
FORMATTER = HtmlFormatter(style="friendly", nowrap=False)
HIGHLIGHT_CSS = FORMATTER.get_style_defs(".highlight")

# Clean, minimal CSS for maximum readability
CSS = f"""
/* Typography: system fonts, optimal line length and spacing */
body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 1rem;
    line-height: 1.6;
    max-width: 42em;
    margin: 2rem auto;
    padding: 0 1.5rem;
    background: #fff;
    color: #222;
}}

/* Links: subtle, accessible */
a {{ color: #0066cc; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Code blocks */
pre {{
    background: #f6f8fa;
    padding: 1rem;
    overflow-x: auto;
    border-radius: 4px;
    font-size: 0.9rem;
    line-height: 1.5;
}}
code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background: #f6f8fa;
    padding: 0.15em 0.3em;
    border-radius: 3px;
    font-size: 0.9em;
}}
pre code {{ background: none; padding: 0; }}

/* Tables */
table {{ border-collapse: collapse; margin: 1rem 0; }}
td, th {{ border: 1px solid #ddd; padding: 0.5em 0.75em; text-align: left; }}
th {{ background: #f6f8fa; }}

/* Navigation breadcrumbs */
nav {{
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #eee;
    font-size: 0.9rem;
}}

/* File listing icons */
.dir::before {{ content: "📁 "; }}
.file::before {{ content: "📄 "; }}
.md::before {{ content: "📝 "; }}

/* Lists */
ul {{ padding-left: 1.5em; }}
li {{ margin: 0.3em 0; }}

/* Headings */
h1, h2, h3, h4, h5, h6 {{ margin-top: 1.5em; margin-bottom: 0.5em; line-height: 1.3; }}

/* Syntax highlighting */
{HIGHLIGHT_CSS}
"""

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>{css}</style>
</head>
<body>
<nav>{nav}</nav>
{body}
</body>
</html>"""


def render_page(title: str, nav: str, body: str) -> str:
    """Render a complete HTML page with consistent styling."""
    return TEMPLATE.format(css=CSS, title=title, nav=nav, body=body)
