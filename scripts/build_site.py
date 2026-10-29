#!/usr/bin/env python3
"""Build the static frontend from src/ into dist/.

The first run can bootstrap the source tree from the legacy checked-in pages:

    python3 scripts/build_site.py --bootstrap

Subsequent builds only read src/ and replace generated frontend files in dist/.
"""
from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
DIST = ROOT / "dist"


def bootstrap() -> None:
    """Extract the current static pages into maintainable source files."""
    pages = sorted(DIST.glob("*.html"))
    if not pages:
        raise SystemExit("Cannot bootstrap: no dist/*.html files found")

    (SRC / "pages").mkdir(parents=True, exist_ok=True)
    (SRC / "styles").mkdir(parents=True, exist_ok=True)
    (SRC / "scripts").mkdir(parents=True, exist_ok=True)
    (SRC / "assets" / "vendor").mkdir(parents=True, exist_ok=True)

    for asset in ("common.js", "metrics.js"):
        shutil.copy2(DIST / asset, SRC / "scripts" / asset)
    vendor_source = DIST / "vendor"
    if vendor_source.exists():
        for asset in vendor_source.glob("*.js"):
            shutil.copy2(asset, SRC / "assets" / "vendor" / asset.name)

    style_pattern = re.compile(r"<style(?:\s[^>]*)?>(.*?)</style>", re.DOTALL | re.IGNORECASE)
    script_pattern = re.compile(r"<script(?:\s[^>]*)?>(.*?)</script>", re.DOTALL | re.IGNORECASE)
    external_script_pattern = re.compile(r"<script\s+src=[\"']([^\"']+)[\"']\s*></script>", re.IGNORECASE)

    for page in pages:
        html = page.read_text(encoding="utf-8")
        styles = [match.group(1).strip() for match in style_pattern.finditer(html)]
        inline_scripts = [match.group(1).strip() for match in script_pattern.finditer(html) if match.group(1).strip()]
        external_scripts = external_script_pattern.findall(html)
        page_name = page.stem
        (SRC / "styles" / f"{page_name}.css").write_text("\n\n".join(styles) + "\n", encoding="utf-8")
        (SRC / "scripts" / f"{page_name}.js").write_text("\n\n".join(inline_scripts) + "\n", encoding="utf-8")

        html = style_pattern.sub("", html)
        html = script_pattern.sub("", html)
        html = html.replace("</head>", f'<link rel="stylesheet" href="styles/{page_name}.css">\n</head>')
        script_tags = []
        for script in external_scripts:
            if script in {"common.js", "metrics.js"}:
                script = f"scripts/{script}"
            script_tags.append(f'<script src="{script}"></script>')
        script_tags.append(f'<script src="scripts/{page_name}.js"></script>')
        html = html.replace("</body>", "".join(script_tags) + "\n</body>")
        (SRC / "pages" / page.name).write_text(html, encoding="utf-8")

    print(f"Bootstrapped {len(pages)} pages into {SRC}")


def build() -> None:
    pages = sorted((SRC / "pages").glob("*.html"))
    if not pages:
        raise SystemExit("No source pages found. Run: python3 scripts/build_site.py --bootstrap")

    DIST.mkdir(exist_ok=True)
    for generated in DIST.glob("*.html"):
        generated.unlink()
    for generated in DIST.glob("*.js"):
        generated.unlink()
    if (DIST / "vendor").exists():
        shutil.rmtree(DIST / "vendor")

    for page in pages:
        html = page.read_text(encoding="utf-8")
        html = html.replace('src="common.js"', 'src="scripts/common.js"')
        html = html.replace('src="metrics.js"', 'src="scripts/metrics.js"')
        html = html.replace('value="fail">Source result: fail', 'value="fail">Tragedy recorded')
        html = html.replace('value="other">Other outcomes', 'value="other">No summit or recorded deaths')
        html = html.replace(
            'Summit recorded includes disputed source records. “Source result: fail” reflects the database outcome label; deaths are shown separately and do not define that filter.',
            'Summit recorded includes disputed source records. “Tragedy recorded” means no recorded summit and at least one recorded death; “No summit or recorded deaths” means neither is recorded.',
        )
        html = html.replace('<span>all values from the local snapshot</span>', '')
        html = html.replace(
            '<nav class="site-nav">',
            '<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="site-navigation">Menu</button><nav class="site-nav" id="site-navigation">',
        )
        html = html.replace('</body>', '<script src="scripts/nav-toggle.js"></script>\n</body>')
        html = html.replace(
            f'<link rel="stylesheet" href="styles/{page.stem}.css">',
            f'<link rel="stylesheet" href="styles/{page.stem}.css"><link rel="stylesheet" href="styles/base.css">',
        )
        if page.name == "index.html":
            html = html.replace(
                '<script src="scripts/index.js"></script>',
                '<script src="scripts/index.js"></script><script src="scripts/season-order.js"></script>',
            )
        if page.name == "peaks.html":
            html = html.replace(
                '<script src="scripts/peaks.js"></script>',
                '<script src="scripts/peaks.js"></script><script src="scripts/peaks-sort.js"></script>',
            )
        nav = html.split('</nav>', 1)[0]
        if 'href="compare.html"' not in nav:
            html = html.replace(
                '<a href="people.html">People</a>',
                '<a href="compare.html">Compare</a><a href="people.html">People</a>',
            )
            html = html.replace(
                '<a class="active" href="people.html">People</a>',
                '<a href="compare.html">Compare</a><a class="active" href="people.html">People</a>',
            )
        html = html.replace(' · local derived data', '')
        (DIST / page.name).write_text(html, encoding="utf-8")
    for source_dir, output_dir in ((SRC / "styles", DIST / "styles"), (SRC / "scripts", DIST / "scripts"), (SRC / "assets", DIST)):
        if source_dir.exists():
            shutil.copytree(source_dir, output_dir, dirs_exist_ok=True)
    # Keep the historical root-level paths available for local bookmarks and
    # older generated pages while new pages use the namespaced source paths.
    for asset in ("common.js", "metrics.js"):
        shutil.copy2(SRC / "scripts" / asset, DIST / asset)
    print(f"Built {len(pages)} pages into {DIST}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bootstrap", action="store_true", help="extract the existing dist site into src/")
    args = parser.parse_args()
    if args.bootstrap:
        bootstrap()
    build()


if __name__ == "__main__":
    main()
