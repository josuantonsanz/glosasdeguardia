"""Beta prototype — a new home page for Glosas de guardia.

Reads the dg-home note (content/Garden-home.md), runs it through the exact
same processing pipeline as the real build (reusing build.py's functions),
then renders it with a custom landing-page design instead of the plain
note layout.

The design is 100% driven by the markdown structure, so it keeps working
when the note changes:
  * paragraphs before the first "## heading"  -> hero intro
  * every "## heading" + the lists under it   -> one card (any heading works;
                                                 add/remove/rename freely)
  * the first image after the last section    -> banner below the hero
  * everything after that image / a <hr>      -> footer note

Usage (from the repo root):
    .venv/Scripts/python.exe beta/build_beta.py

Output:
    beta/index.html   the page (links into ../public/ so it is clickable)
    beta/style.css    the design, hand-written, referenced by index.html
    beta/garden.jpg   copied from content/
"""

import os
import re
import sys
import shutil
from pathlib import Path

import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader

ROOT = Path(__file__).resolve().parent.parent
BETA_DIR = Path(__file__).resolve().parent
os.chdir(ROOT)
sys.path.insert(0, str(ROOT))

import build  # the real pipeline, reused as-is

# The home-page structure helpers were integrated into the real build
# (build.py); the prototype reuses them from there.
from build import (
    TopLevelSplitter,
    split_home,
    parse_dt,
    recent_label,
    compute_recent,
)

HOME_NOTE = ROOT / "content" / "Garden-home.md"


def polish(fragment):
    """Make the prototype clickable: internal links point at the real build
    in ../public/, external links get a class for the ↗ marker."""
    fragment = re.sub(
        r'<a href="(?!https?://|#|mailto:)([^"]+)"',
        r'<a href="../public/\1"',
        fragment,
    )
    fragment = re.sub(
        r'<a href="(https?://[^"]+)"',
        r'<a class="ext" href="\1"',
        fragment,
    )
    return fragment


def main():
    with open(HOME_NOTE, encoding="utf-8") as f:
        post = frontmatter.load(f)

    content = build.filter_proprietary_content(post.content)

    # First H1 -> page title (same rule as the real build)
    title = "Glosas de guardia"
    h1 = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
    if h1:
        title = h1.group(1).strip().replace("\\.", ".")
        content = content.replace(h1.group(0), "", 1).lstrip()

    # Transclusion dictionary (mirrors build.py)
    vault = {}
    for fp in (ROOT / "content").rglob("*.md"):
        try:
            with open(fp, encoding="utf-8") as f:
                vault[fp.stem] = frontmatter.load(f).content
        except Exception:
            pass

    content = build.resolve_transclusions(content, vault)
    content = build.process_inline_footnotes(content)
    content = build.process_highlights(content)
    content = build.process_strikethrough(content)
    content = build.process_callouts(content)

    rel_path = Path("Garden-home.md")
    content, _used_images = build.resolve_images(content, rel_path, set())

    notes = list(build.get_publishable_notes())
    link_map = build.build_link_map(notes, base_dir=Path("content"))
    content = build.convert_wikilinks(content, link_map, current_filepath=rel_path)

    md = markdown.Markdown(
        extensions=["footnotes", "toc", "fenced_code", "tables", "md_in_html"]
    )
    md.reset()
    html_content = md.convert(content)

    parser = TopLevelSplitter()
    parser.feed(html_content)
    blocks = parser.blocks

    intro, sections, trailing = split_home(blocks)

    intro_html = polish("".join(b["html"] + "\n" for b in intro))
    for s in sections:
        s["html"] = polish(s["html"])

    # Banner image: the first image in the trailing material
    image_src = None
    for b in trailing:
        m = re.search(r'<img[^>]+src="([^"]+)"', b["html"])
        if m:
            image_src = m.group(1)
            break
    if image_src:
        src_file = ROOT / "content" / image_src
        if src_file.exists():
            shutil.copy2(src_file, BETA_DIR / image_src)

    # Footer note: trailing material minus the image and the <hr>
    footer_blocks = [
        b for b in trailing if "<img" not in b["html"] and b["tag"] != "hr"
    ]
    footer_html = polish("".join(b["html"] + "\n" for b in footer_blocks))
    footer_html = re.sub(
        r"(info@[A-Za-z0-9._%+-]+)",
        r'<span class="email">\1</span>',
        footer_html,
    )

    created = post.metadata.get("created", post.metadata.get("planted", ""))
    updated = post.metadata.get("updated", post.metadata.get("edited", ""))
    planted_label = build.format_relative_phrase("Plantado", build.get_relative_time(created))
    atendido_label = build.format_relative_phrase("Atendido", build.get_relative_time(updated))

    env = Environment(loader=FileSystemLoader(BETA_DIR))
    template = env.get_template("home.html")
    page = template.render(
        title=title,
        intro_html=intro_html,
        image_src=image_src,
        sections=sections,
        footer_html=footer_html,
        planted_label=planted_label,
        atendido_label=atendido_label,
        recent=compute_recent(notes),
    )

    (BETA_DIR / "index.html").write_text(page, encoding="utf-8")
    print(f"Beta listo: {BETA_DIR / 'index.html'}")
    print(f"  {len(intro)} intro block(s), {len(sections)} section(s), {len(trailing)} trailing block(s)")


if __name__ == "__main__":
    main()
