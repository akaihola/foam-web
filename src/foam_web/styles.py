"""Styling module for foam-web with readable typography and colors."""

from pygments.formatters.html import HtmlFormatter

# Use a light, readable Pygments style
FORMATTER = HtmlFormatter(style="friendly", nowrap=False)
HIGHLIGHT_CSS = FORMATTER.get_style_defs(".highlight")

# Clean, minimal CSS for maximum readability
CSS = f"""
/* Layout: sidebar + content */
* {{ box-sizing: border-box; }}
body {{
    font-family: Charter, "Bitstream Charter", "Sitka Text", Cambria, Georgia, serif;
    font-size: 1.1rem;
    line-height: 1.65;
    margin: 0;
    padding: 0;
    background: #faf9f7;
    color: #333;
}}

/* Sidebar */
.sidebar {{
    position: fixed;
    top: 0;
    left: 0;
    width: 260px;
    height: 100vh;
    background: #f5f4f2;
    border-right: 1px solid #e0ddd8;
    overflow-y: auto;
    padding: 1rem 0;
    transition: transform 0.25s ease;
    z-index: 100;
}}
.sidebar.hidden {{
    transform: translateX(-260px);
}}
.sidebar-toggle {{
    position: fixed;
    top: 0.5rem;
    left: 0.5rem;
    z-index: 101;
    background: #faf9f7;
    border: 1px solid #e0ddd8;
    border-radius: 4px;
    padding: 0.3rem 0.6rem;
    cursor: pointer;
    font-size: 1.1rem;
    transition: left 0.25s ease;
}}
.sidebar.hidden ~ .sidebar-toggle {{
    left: 0.5rem;
}}
.sidebar:not(.hidden) ~ .sidebar-toggle {{
    left: 268px;
}}

/* File tree */
.file-tree {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    font-size: 0.85rem;
    line-height: 1.4;
}}
.file-tree ul {{
    list-style: none;
    padding-left: 1rem;
    margin: 0;
}}
.file-tree > ul {{
    padding-left: 0.5rem;
}}
.file-tree li {{
    margin: 0.15em 0;
    display: grid;
    grid-template-columns: 1.4em 1fr;
    grid-template-rows: auto;
}}
.file-tree li > ul {{
    grid-column: 2 / 3;
}}
.file-tree li > a {{
    grid-column: 2 / 3;
    word-break: break-word;
}}
.file-tree li > a:only-child {{
    grid-column: 1 / -1;
}}
.file-tree .toggle {{
    grid-column: 1 / 2;
    grid-row: 1;
    align-self: start;
    width: 1em;
    cursor: pointer;
    user-select: none;
    color: #888;
}}
.file-tree .collapsed > ul {{
    display: none;
}}
.file-tree .collapsed > .toggle {{
    transform: rotate(-90deg);
}}
.file-tree a {{
    color: #333;
}}
.file-tree a:hover {{
    color: #1a5f9c;
}}
.file-tree a.current {{
    font-weight: 600;
    color: #1a5f9c;
}}

/* Main content area */
.content {{
    max-width: 42em;
    margin: 2rem auto;
    padding: 0 1.5rem 0 1.5rem;
    margin-left: 280px;
    transition: margin-left 0.25s ease;
}}
.sidebar.hidden ~ .content {{
    margin-left: auto;
}}

/* Links: subtle, accessible */
a {{ color: #1a5f9c; text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Code blocks */
pre {{
    background: #f0eeeb;
    padding: 1rem;
    overflow-x: auto;
    border-radius: 4px;
    font-size: 0.85rem;
    line-height: 1.5;
}}
code {{
    font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
    background: #f0eeeb;
    padding: 0.15em 0.3em;
    border-radius: 3px;
    font-size: 0.85em;
}}
pre code {{ background: none; padding: 0; }}

/* Tables */
table {{ border-collapse: collapse; margin: 1rem 0; line-height: 1.3; }}
td, th {{ border: 1px solid #ddd; padding: 0.25em 0.6em; text-align: left; vertical-align: top; }}
th {{ background: #f0eeeb; }}

/* Navigation breadcrumbs */
nav {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    margin-bottom: 1.5rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid #e0ddd8;
    font-size: 0.9rem;
}}

/* File listing icons — hanging indent so wrapped lines align after the icon */
.dir::before {{ content: "📁"; }}
.file::before {{ content: "📄"; }}
.md::before {{ content: "📝"; }}
.file-tree a.dir,
.file-tree a.file,
.file-tree a.md,
.file-tree a.img-file {{
    display: inline-flex;
    align-items: baseline;
    gap: 0.3em;
}}
.file-tree a.dir::before,
.file-tree a.file::before,
.file-tree a.md::before {{
    flex-shrink: 0;
}}
.tree-thumb {{
    width: 1em;
    height: 1em;
    object-fit: cover;
    flex-shrink: 0;
    vertical-align: middle;
    border-radius: 2px;
}}

/* Lists */
ul {{ padding-left: 1.5em; }}
li {{ margin: 0.3em 0; }}

/* Headings */
h1, h2, h3, h4, h5, h6 {{ margin-top: 1.5em; margin-bottom: 0.5em; line-height: 1.3; }}

/* Syntax highlighting */
{HIGHLIGHT_CSS}
"""

SIDEBAR_JS = """
<script>
(function() {
    // Toggle sidebar visibility
    var sidebar = document.querySelector('.sidebar');
    var toggle = document.querySelector('.sidebar-toggle');
    var key = 'foam-sidebar-hidden';
    
    // Restore state
    if (localStorage.getItem(key) === 'true') {
        sidebar.classList.add('hidden');
    }
    
    toggle.onclick = function() {
        sidebar.classList.toggle('hidden');
        localStorage.setItem(key, sidebar.classList.contains('hidden'));
    };
    
    // Expand/collapse folders, persisting state in localStorage
    var TREE_KEY = 'foam-tree-open';
    function loadOpenSet() {
        try { return new Set(JSON.parse(localStorage.getItem(TREE_KEY) || '[]')); }
        catch(e) { return new Set(); }
    }
    function saveOpenSet(s) {
        try { localStorage.setItem(TREE_KEY, JSON.stringify(Array.from(s))); }
        catch(e) {}
    }
    function folderPath(li) {
        // Use the href of the folder's anchor as a stable key
        var a = li.querySelector(':scope > a');
        return a ? a.getAttribute('href') : null;
    }

    // Restore persisted open/closed state before auto-expand
    var openSet = loadOpenSet();
    document.querySelectorAll('.file-tree li.collapsed').forEach(function(li) {
        var fp = folderPath(li);
        if (fp && openSet.has(fp)) {
            li.classList.remove('collapsed');
        }
    });

    // Auto-expand path to current file/folder (always, regardless of saved state)
    var current = document.querySelector('.file-tree a.current');
    if (current) {
        var parent = current.parentElement;
        while (parent && !parent.classList.contains('file-tree')) {
            if (parent.tagName === 'LI') {
                parent.classList.remove('collapsed');
                var fp = folderPath(parent);
                if (fp) openSet.add(fp);
            }
            parent = parent.parentElement;
        }
        saveOpenSet(openSet);
    }

    // Toggle on click and persist
    document.querySelectorAll('.file-tree .toggle').forEach(function(t) {
        t.onclick = function(e) {
            e.stopPropagation();
            var li = t.parentElement;
            li.classList.toggle('collapsed');
            var fp = folderPath(li);
            if (fp) {
                var s = loadOpenSet();
                if (li.classList.contains('collapsed')) { s.delete(fp); }
                else { s.add(fp); }
                saveOpenSet(s);
            }
        };
    });
})();
</script>
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
{sidebar}
<button class="sidebar-toggle" aria-label="Toggle sidebar">☰</button>
<div class="content">
<nav>{nav}</nav>
{body}
</div>
{livereload}
{sidebar_js}
</body>
</html>"""

LIVERELOAD_SCRIPT = '<script src="/livereload.js?port={port}&amp;mindelay=10"></script>'


def render_page(
    title: str, nav: str, body: str, livereload: str = "", sidebar: str = ""
) -> str:
    """Render a complete HTML page with consistent styling."""
    sidebar_html = (
        f'<aside class="sidebar"><nav class="file-tree">{sidebar}</nav></aside>'
        if sidebar
        else ""
    )
    return TEMPLATE.format(
        css=CSS,
        title=title,
        nav=nav,
        body=body,
        livereload=livereload,
        sidebar=sidebar_html,
        sidebar_js=SIDEBAR_JS if sidebar else "",
    )
