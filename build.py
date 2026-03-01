import os
import re
import shutil
import frontmatter
import markdown
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
import time

# Configuration
SITE_URL = "https://glosasdeguardia.es"
CONTENT_DIR = "content"
OUTPUT_DIR = "public"
TEMPLATE_DIR = "templates"

def setup_directories():
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

def get_publishable_notes():
    """Returns a list of Path objects for notes that have dg-publish: true."""
    notes = []
    content_path = Path(CONTENT_DIR)
    
    for filepath in content_path.rglob("*.md"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            publish_flag = post.metadata.get("dg-publish", False)
            if publish_flag is True or str(publish_flag).lower() == "true":
                notes.append((filepath, post))
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            
    return notes

def resolve_transclusions(content, vault_content):
    """
    Finds Obsidian transclusions ![[Note]], ![[Note#Header]], ![[Note#^block-id]]
    and replaces them with the content from the target note.
    
    vault_content is a dictionary mapping { 'Note Name': 'Full markdown string' }
    """
    # Match ![[Note Name]] or ![[Note Name#Section]]
    pattern = re.compile(r'!\[\[([^\]#]+)(?:#([^\]]+))?\]\]')
    
    def repl(match):
        note_name = match.group(1).strip()
        section = match.group(2)
        
        # If it's an image, skip transclusion so resolve_images can handle it
        if any(note_name.lower().endswith(ext) for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']):
            return match.group(0)
            
        target_content = vault_content.get(note_name)
        if not target_content:
            return f"*(Transclusion failed: {note_name} not found)*"
            
        if not section:
            # Full note transclusion
            return f'<div class="transclusion" markdown="1">\n\n{target_content}\n\n</div>'
            
        section = section.strip()
        
        # Is it a block reference? (starts with ^)
        if section.startswith('^'):
            block_id = section
            # Find where the block id is located
            block_pos = target_content.find(block_id)
            if block_pos != -1:
                # Search backwards for the start of the block (double newline or start of string)
                start_pos = target_content.rfind('\n\n', 0, block_pos)
                if start_pos == -1:
                    start_pos = 0 # It's at the very beginning of the file
                else:
                    start_pos += 2 # Skip the \n\n
                
                # Search forwards for the end of the block (double newline or end of string)
                end_pos = target_content.find('\n\n', block_pos)
                if end_pos == -1:
                    end_pos = len(target_content)
                    
                extracted = target_content[start_pos:end_pos].strip()
                # Remove the actual ID from the rendered text
                extracted = extracted.replace(f" {block_id}", "").replace(block_id, "")
                return f'<div class="transclusion block-transclusion" markdown="1">\n\n{extracted}\n\n</div>'
                
            return f"*(Block not found: {section})*"
            
        # It's a header reference.
        # We need to find the header and extract everything until the next header of same or higher level
        # E.g., if it's ## History, we extract until the next ## or #
        # Find the header line
        header_pattern = re.compile(r'^(#{1,6})\s+' + re.escape(section) + r'\s*$', re.MULTILINE | re.IGNORECASE)
        header_match = header_pattern.search(target_content)
        
        if header_match:
            level = len(header_match.group(1))
            start_pos = header_match.end()
            
            # Find the next header of same or higher level (fewer or equal #)
            # e.g., if we matched ##, we look for ^# \w or ^## \w
            next_header_pattern = re.compile(r'^#{1,' + str(level) + r'}\s+', re.MULTILINE)
            next_match = next_header_pattern.search(target_content, start_pos)
            
            if next_match:
                extracted = target_content[start_pos:next_match.start()].strip()
            else:
                extracted = target_content[start_pos:].strip()
                
            return f'<div class="transclusion header-transclusion" markdown="1">\n\n{extracted}\n\n</div>'
            
        return f"*(Section not found: {section})*"

    return pattern.sub(repl, content)

def build_link_map(notes, base_dir=Path(CONTENT_DIR)):
    """
    Creates a mapping of note titles, filenames, and full relative paths 
    to their future HTML URLs.
    """
    link_map = {}
    for filepath, post in notes:
        # The path relative to the content directory
        rel_path = filepath.relative_to(base_dir)
        # The URL destination maintain the same folder structure
        url = f"{rel_path.with_suffix('.html').as_posix()}" 
        
        # 1. Map the exact relative path without extension
        exact_match = rel_path.with_suffix('').as_posix()
        link_map[exact_match] = url
        
        # 2. Map just the stem (filename) as a fallback
        # If multiple files have the same name, this will get overwritten by the last one scanned.
        # This mirrors Obsidian's behavior of preferring exact paths or letting the user choose.
        link_map[filepath.stem] = url
        
        # Also map aliases if any
        aliases = post.metadata.get("aliases", [])
        if isinstance(aliases, list):
            for alias in aliases:
                link_map[alias] = url
                
    return link_map

def filter_proprietary_content(content):
    """Removes sections between ;;;propio and ;;;."""
    return re.sub(r';;;propio[\s\S]*?;;;', '', content)

def extract_metadata(content, frontmatter_dict, fallback_title, extracted_images=None):
    """
    Extracts metadata for the template:
    - title (From frontmatter, then H1, then fallback)
    - subtitle
    - date / planted
    - reading_time (in minutes, assuming 200 words per minute)
    - description (From frontmatter, then first 160 chars)
    - image (From frontmatter, then first extracted image)
    
    Returns: (metadata_dict, cleaned_content) where cleaned_content has the primary H1 removed
    if it was used as the title.
    """
    metadata = {
        "title": frontmatter_dict.get("title"),
        "subtitle": frontmatter_dict.get("subtitle", ""),
        "date": frontmatter_dict.get("date", frontmatter_dict.get("planted", ""))
    }
    
    # Calculate reading time and text preview
    text_only = re.sub(r'[#*`_\[\]()!>]', ' ', content)
    word_count = len(text_only.split())
    reading_time = max(1, round(word_count / 200))
    metadata["reading_time"] = reading_time
    
    # Extract description for SEO
    description = frontmatter_dict.get("description", frontmatter_dict.get("summary", ""))
    if not description:
        description_raw = re.sub(r'\s+', ' ', text_only[:300]).strip()
        description = description_raw[:157] + "..." if len(description_raw) > 160 else description_raw
    metadata["description"] = description
    
    # Extract image for Open Graph
    image = frontmatter_dict.get("image", frontmatter_dict.get("cover", ""))
    if not image and extracted_images:
        image = list(extracted_images)[0].as_posix()
    metadata["image"] = image
    
    cleaned_content = content
    if not metadata["title"]:
        h1_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if h1_match:
            title_raw = h1_match.group(1).strip()
            # Unescape common characters like \.
            metadata["title"] = title_raw.replace("\\.", ".")
            cleaned_content = content.replace(h1_match.group(0), "", 1).lstrip()
        else:
            metadata["title"] = fallback_title
    else:
        # Also unescape if title came from frontmatter
        metadata["title"] = str(metadata["title"]).replace("\\.", ".")
            
    return metadata, cleaned_content

def process_inline_footnotes(content):
    """Converts ^[inline footnote] to standard [^id] and appends definition."""
    pattern = re.compile(r'\^\[([^\]]+)\]')
    footnotes = []
    
    def repl(match):
        fn_content = match.group(1)
        fn_id = f"inline-{len(footnotes) + 1}"
        footnotes.append((fn_id, fn_content))
        return f"[^{fn_id}]"
    
    content = pattern.sub(repl, content)
    
    if footnotes:
        content += "\n\n"
        for fn_id, fn_content in footnotes:
            content += f"[^{fn_id}]: {fn_content}\n"
            
    return content

def process_highlights(content):
    """Converts ==text== to <mark>text</mark>."""
    return re.sub(r'==(.+?)==', r'<mark>\1</mark>', content)

def resolve_images(content, current_rel_path, image_map):
    """
    Finds ![[image.png]] and standard image links.
    Returns (processed_content, used_images).
    used_images is a set of relative paths to images to be copied.
    """
    # 1. Obsidian Embeds ![[image.png]]
    obsidian_pattern = re.compile(r'!\[\[([^\]]+)\]\]')
    used_images = set()
    
    # Calculate depth to get back to root
    depth = len(current_rel_path.parts) - 1
    root_prefix = "../" * depth if depth > 0 else ""

    def obsidian_repl(match):
        img_path_str = match.group(1).split('|')[0].strip() # Handle ![[img.png|100]]
        
        # Try to find the image in content dir
        found_img = find_image(img_path_str)
        if found_img:
            used_images.add(found_img)
            # URL should be relative to the note
            url = f"{root_prefix}{found_img.as_posix()}"
            return f'![{img_path_str}]({url})'
        return f"*(Image not found: {img_path_str})*"

    content = obsidian_pattern.sub(obsidian_repl, content)
    
    # 2. Standard Markdown Images ![alt](url)
    md_pattern = re.compile(r'!\[([^\]]*)\]\(([^)]+)\)')
    
    def md_repl(match):
        alt = match.group(1)
        url = match.group(2)
        # If it's a local path (not http), track it
        if not url.startswith(('http://', 'https://', 'data:')):
            found_img = find_image(url)
            if found_img:
                used_images.add(found_img)
                # Ensure the URL is correctly rooted for the output
                return f'![{alt}]({root_prefix}{found_img.as_posix()})'
        return match.group(0)

    content = md_pattern.sub(md_repl, content)
    
    return content, used_images

def find_image(img_name):
    """Attempts to find an image file in the content directory."""
    # If it's already a path that exists
    p = Path(CONTENT_DIR) / img_name
    if p.exists() and p.is_file():
        return p.relative_to(CONTENT_DIR)
        
    # Search all subdirectories if only filename given
    for ext in ['.png', '.jpg', '.jpeg', '.gif', '.svg']:
        # Try with extension if missing
        search_name = img_name if any(img_name.lower().endswith(e) for e in ['.png', '.jpg', '.jpeg', '.gif', '.svg']) else f"{img_name}{ext}"
        
        for p in Path(CONTENT_DIR).rglob(search_name):
            if p.is_file():
                return p.relative_to(CONTENT_DIR)
    return None

def minify_css():
    """Reads templates/style.css, minifies it, and saves to public/style.min.css"""
    css_path = Path(TEMPLATE_DIR) / "style.css"
    out_path = Path(OUTPUT_DIR) / "style.min.css"
    
    if not css_path.exists():
        return
        
    css_content = css_path.read_text(encoding="utf-8")
    
    # Remove CSS comments
    css_content = re.sub(r'/\*[\s\S]*?\*/', '', css_content)
    # Remove newlines and tabs
    css_content = re.sub(r'\n+|\t+', '', css_content)
    # Remove spaces around open brackets
    css_content = re.sub(r'\s*{\s*', '{', css_content)
    # Remove spaces around colons (but not inside rules like `url(http://)`)
    css_content = re.sub(r':\s+', ':', css_content)
    # Remove spaces around semi-colons
    css_content = re.sub(r'\s*;\s*', ';', css_content)
    # Remove last semi-colon in a block
    css_content = re.sub(r';}', '}', css_content)
    
    out_path.write_text(css_content, encoding="utf-8")

def convert_wikilinks(content, link_map, current_filepath):
    """
    Converts [[Note Name]] and [[Note Name|Alias]] to standard markdown links.
    Calculates the relative path from the current_filepath to the target url.
    """
    # Pattern for [[Note Name|Alias]] (but NOT ![[Note Name|Alias]])
    pattern_alias = re.compile(r'(?<!!)\[\[([^\]\|]+)\|([^\]]+)\]\]')
    # Pattern for [[Note Name]] (but NOT ![[Note Name]])
    pattern_simple = re.compile(r'(?<!!)\[\[([^\]]+)\]\]')
    
    # Calculate depth of current file to determine how many ../ we need
    # current_filepath is relative to CONTENT_DIR, e.g., "Folder/Note.md" -> 1 depth ("../")
    depth = len(current_filepath.parts) - 1
    prefix = "../" * depth if depth > 0 else ""
    
    def get_relative_url(target):
        # We get the target's path relative to the root (e.g. "Folder/Target.html")
        target_url = link_map.get(target, f"{target}.html")
        # And we prefix it to make it relative to the currently viewed page
        return f"{prefix}{target_url}"
    
    def repl_alias(match):
        note_target = match.group(1).strip()
        alias = match.group(2).strip()
        url = get_relative_url(note_target)
        return f"[{alias}]({url})"
        
    def repl_simple(match):
        note_target = match.group(1).strip()
        url = get_relative_url(note_target)
        return f"[{note_target}]({url})"
        
    content = pattern_alias.sub(repl_alias, content)
    content = pattern_simple.sub(repl_simple, content)
    
    return content

def build_site():
    setup_directories()
    
    # Optional: Copy static assets if we had them
    # shutil.copytree("static", os.path.join(OUTPUT_DIR, "static"), dirs_exist_ok=True)
    
    print("Scanning vault for publishable notes...")
    notes = list(get_publishable_notes())
    print(f"Found {len(notes)} notes to publish.")
    
    link_map = build_link_map(notes, base_dir=Path(CONTENT_DIR))
    
    env = Environment(loader=FileSystemLoader(TEMPLATE_DIR))
    note_template = env.get_template("note.html")
    index_template = env.get_template("index.html")
    sitemap_template = env.get_template("sitemap.xml")
    
    # Initialize markdown converter (with footnotes, toc, and md_in_html)
    md = markdown.Markdown(extensions=['footnotes', 'toc', 'fenced_code', 'tables', 'md_in_html'])
    
    all_notes_data = []
    all_used_images = set()
    
    # 1. Pre-build dictionary for transclusions { "Note Name": "Content" }
    # Load ALL markdown files in the content directory to support transclusions from any note
    vault_content = {}
    for filepath in Path(CONTENT_DIR).rglob("*.md"):
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                post = frontmatter.load(f)
            # Index by title if available, otherwise filename stem
            title = post.metadata.get("title", filepath.stem)
            vault_content[title] = post.content
            # Also index by relative path stem to ensure safety
            vault_content[filepath.stem] = post.content
        except Exception as e:
            print(f"Error indexing {filepath} for transclusion: {e}")

    for filepath, post in notes:
        # The path relative to the content directory
        rel_path = filepath.relative_to(Path(CONTENT_DIR))
        url = f"{rel_path.with_suffix('.html').as_posix()}"
        
        # 1. Filter proprietary content
        content = filter_proprietary_content(post.content)
        
        # 2. Resolve transclusions first
        content = resolve_transclusions(content, vault_content)
        
        # 3. Process Inline Footnotes ^[...]
        content = process_inline_footnotes(content)
        
        # 4. Process Highlights ==...==
        content = process_highlights(content)
        
        # 5. Resolve Images and Obsidian Embeds ![[img]]
        content, used_images = resolve_images(content, rel_path, all_used_images)
        all_used_images.update(used_images)
        
        # 4. Process Wikilinks with current context path
        content = convert_wikilinks(content, link_map, current_filepath=rel_path)
        
        # Prepare template data
        metadata, cleaned_content = extract_metadata(content, post.metadata, filepath.stem, used_images)
        
        # 5. Convert to HTML
        md.reset()
        html_content = md.convert(cleaned_content)
        
        # Calculate depth for root_path (used for CSS linking)
        depth = len(rel_path.parts) - 1
        root_path = "../" * depth if depth > 0 else "./"
        
        note_data = {
            "title": metadata["title"],
            "subtitle": metadata["subtitle"],
            "date": metadata["date"],
            "reading_time": metadata["reading_time"],
            "description": metadata["description"],
            "image": metadata["image"],
            "content": html_content,
            "toc": md.toc,
            "url": url,
            "site_url": SITE_URL,
            "filepath": rel_path, # Store this to help with tree rendering later
            "root_path": root_path
        }
        all_notes_data.append(note_data)
        
        # Render and save
        output_html = note_template.render(**note_data)
        
        # Need to construct output path and ensure dirs exist
        output_path = Path(OUTPUT_DIR) / rel_path.with_suffix('.html')
        os.makedirs(output_path.parent, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(output_html)
            
    # Copy only used images
    if all_used_images:
        print(f"Copying {len(all_used_images)} used image assets...")
        for img_rel_path in all_used_images:
            src = Path(CONTENT_DIR) / img_rel_path
            dst = Path(OUTPUT_DIR) / img_rel_path
            os.makedirs(dst.parent, exist_ok=True)
            shutil.copy2(src, dst)

    # Generate Index page
    index_html = index_template.render(
        notes=all_notes_data, 
        root_path="./", 
        site_url=SITE_URL, 
        title="Digital Garden", 
        description="A digital garden and personal knowledge base.", 
        url=""
    )
    with open(Path(OUTPUT_DIR) / "index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print("Generating sitemap...")
    sitemap_xml = sitemap_template.render(notes=all_notes_data, site_url=SITE_URL)
    with open(Path(OUTPUT_DIR) / "sitemap.xml", "w", encoding="utf-8") as f:
        f.write(sitemap_xml)
        
    print("Build complete! Files are in the 'public' directory.")
    
    # Process assets
    print("Minifying and copying CSS...")
    minify_css()

if __name__ == "__main__":
    start_time = time.time()
    build_site()
    end_time = time.time()
    print(f"Build time: {end_time - start_time:.2f} seconds")
