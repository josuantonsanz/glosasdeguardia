import frontmatter
from pathlib import Path

CONTENT_DIR = "content"
notes = []
content_path = Path(CONTENT_DIR)

print(f"Checking {CONTENT_DIR}...")
for filepath in content_path.rglob("*.md"):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)
        publish_flag = post.metadata.get("dg-publish", False)
        print(f"File: {filepath.name}, dg-publish: {publish_flag} (Type: {type(publish_flag)})")
        if publish_flag is True or str(publish_flag).lower() == "true":
            notes.append(filepath)
    except Exception as e:
        print(f"Error reading {filepath}: {e}")

print(f"Found {len(notes)} publishable notes.")
