import pytest
from build import extract_metadata

def test_extract_metadata_pulls_h1():
    content = "Some text before\n\n# The Real Title\n\nMore text here."
    fallback_title = "Filename Title"
    
    metadata, new_content = extract_metadata(content, {}, fallback_title)
    
    assert metadata["title"] == "The Real Title"
    # The H1 should be removed from the content so we can render it in Jinja instead
    assert "# The Real Title" not in new_content
    assert "More text here" in new_content

def test_extract_metadata_fallback_title():
    content = "Just some text. No headers."
    fallback_title = "Filename Title"
    
    metadata, new_content = extract_metadata(content, {}, fallback_title)
    
    assert metadata["title"] == "Filename Title"

def test_extract_metadata_prioritizes_frontmatter():
    content = "# Markdown Header"
    frontmatter = {"title": "YAML Title", "subtitle": "A great subtitle", "date": "2023-10-01", "planted": "2022-01-01"}
    
    metadata, new_content = extract_metadata(content, frontmatter, "Fallback")
    
    assert metadata["title"] == "YAML Title"
    assert metadata["subtitle"] == "A great subtitle"
    
def test_extract_reading_time():
    # 400 words should be exactly 2 minutes (200 wpm)
    content = "word " * 400
    
    metadata, _ = extract_metadata(content, {}, "Title")
    
    assert metadata["reading_time"] == 2

def test_extract_reading_time_minimum():
    # 10 words should round up to 1 minute
    content = "word " * 10
    
    metadata, _ = extract_metadata(content, {}, "Title")
    
    assert metadata["reading_time"] == 1

def test_extract_metadata_description():
    content = "This is a really long sentence that should be extracted as the description of the note because it doesn't have a frontmatter description provided so it will fallback to generating one."
    metadata, _ = extract_metadata(content, {}, "Title")
    assert metadata["description"].startswith("This is a really long sentence")
    
    frontmatter = {"description": "Custom description here."}
    metadata2, _ = extract_metadata(content, frontmatter, "Title")
    assert metadata2["description"] == "Custom description here."

def test_extract_metadata_image():
    from pathlib import Path
    content = "Just some content."
    frontmatter = {"image": "assets/cover.png"}
    metadata, _ = extract_metadata(content, frontmatter, "Title")
    assert metadata["image"] == "assets/cover.png"
    
    # Test fallback to extracted_images
    metadata2, _ = extract_metadata(content, {}, "Title", extracted_images={Path("content/img1.png")})
    assert metadata2["image"] == "content/img1.png"

def test_process_highlights():
    from build import process_highlights
    content = "This is ==highlighted== text."
    result = process_highlights(content)
    assert result == "This is <mark>highlighted</mark> text."
