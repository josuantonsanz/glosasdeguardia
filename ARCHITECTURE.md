# Digital Garden Project Architecture & Progress

This document serves as a reference for the architecture, design choices, and features implemented in the Digital Garden static site generator.

## Core Architecture

The project is a custom Static Site Generator (SSG) built in Python. It takes a directory of Markdown notes (e.g., an Obsidian vault) and compiles them into a static `public/` directory suitable for hosting on GitHub Pages or locally.

### Tech Stack
- **Language**: Python 3
- **Dependency Management**: `uv`
- **Markdown Processing**: `python-markdown` (with extensions: `footnotes`, `toc`, `fenced_code`, `tables`, `md_in_html`)
- **Templating**: `Jinja2`
- **Frontmatter Parsing**: `python-frontmatter`
- **Testing Framework**: `pytest` (Adopting Red/Green TDD for all features)

### Directory Structure
```text
.
├── content/              # The source Obsidian notes (Markdown)
├── templates/            # Jinja2 templates (base.html, index.html, note.html) and style.css
├── public/               # The generated static HTML files (output)
├── tests/                # Pytest suites for TDD
├── build.py              # The main compiler script
├── ARCHITECTURE.md       # This document
└── TODO.txt              # User's task tracking
```

## Build Pipeline (`build.py`)

The build process (`uv run python build.py`) follows these steps:
1. **Directory Setup**: Cleans and recreates the `public/` directory.
2. **Note Scanning**: Recursively scans `content/` for `.md` files that have `dg-publish: true` in their YAML frontmatter.
3. **Link Mapping**: Creates a dictionary mapping note names, filenames, and aliases to their future relative URLs, preserving the nested folder structure.
4. **Vault Dictionary**: Pre-loads all note contents into memory for transclusion processing.
5. **Content Processing** (per note):
    - **Metadata Extraction**: Parses YAML frontmatter and extracts the first Markdown `# H1` as the title (removing it from the body). Retrieves `subtitle`, `date`/`planted`, and dynamically calculates a `reading_time`.
    - **Transclusion**: Resolves Obsidian embed syntax (`![[Note]]`, `![[Note#Heading]]`, `![[Note#^block-id]]`) by injecting the target Markdown into a custom `<div class="transclusion" markdown="1">` wrapper.
    - **Wikilinks**: Converts Obsidian links (`[[Note]]` and `[[Note|Alias]]`) into standard Markdown links, calculating the correct `../` depth relative to the current file's folder.
    - **Markdown Conversion**: Converts the processed Markdown into HTML, automatically generating a Table of Contents (TOC).
    - **Jinja Rendering**: Injects the HTML, TOC, and metadata into the `note.html` template. Let the Jinja template resolve relative paths using a dynamically calculated `root_path`.
    - **File Writing**: Saves the output HTML in the `public/` directory, recreating the exact sub-folder structure of the original note.
6. **Index Generation**: Renders `index.html` showcasing all compiled notes.
7. **Asset Pipeline**: Reads `templates/style.css`, minifies it, and saves it to `public/style.min.css`.

## Completed Features

- **TDD Integration**: A robust test suite (`tests/`) checking link resolution, transclusions, and metadata extraction.
- **Nested Folder Support**: Notes retain their folder structure in the `public/` output. Relative paths (like `../../`) are perfectly calculated so links work locally (`file:///`) without needing a web server.
- **Wikilinks & Aliases**: Supports `[[Note Name]]` and `[[Note Name|Custom Alias]]`.
- **Transclusion**: Full support for embedding entire notes, specific headings, or specific block IDs (`^block-id`). Ensures `md_in_html` parses the transcluded text correctly.
- **Metadata Extraction**: Dynamically calculates Word Count / Reading Time and promotes the first H1 to the page `<title>`.
- **Flexoki Theme**: Implemented a warm, ink-and-paper color palette (Flexoki) with custom Orange accents for links.
- **Maggie Appleton Layout (Revised)**: A 2-column mobile-responsive layout featuring a widened center reading column (90ch) and a sticky Table of Contents on the left sidebar.
- **Microframework**: Integrated **Pico.css** for a minimalist, semantic, and responsive foundation.
- **CSS Minification**: Custom regex-based minifier that caches the CSS efficiently.

## Next Steps / Future Work
- **Sidebar Explorer**: Read the directory hierarchy and generate a tree-view navigation panel in the left sidebar.
- **Tags Page**: Aggregate notes by their YAML tags.
- **Hover Previews**: Implement Javascript tooltip popups for internal links to preview content before clicking.
- **Automatic Deployments**: Set up GitHub Actions to run the build script and publish to GitHub Pages on `git push`.
