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

def test_extract_metadata_ignores_frontmatter_title():
    content = "# Markdown Header"
    frontmatter = {"title": "YAML Title", "subtitle": "A great subtitle", "date": "2023-10-01", "planted": "2022-01-01"}
    
    metadata, new_content = extract_metadata(content, frontmatter, "Fallback")
    
    # It should IGNORE "YAML Title" and use "Markdown Header"
    assert metadata["title"] == "Markdown Header"
    assert metadata["subtitle"] == "A great subtitle"
    # The header should be removed from content even if frontmatter title was present
    assert "# Markdown Header" not in new_content
    
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

def test_format_relative_phrase_hoy():
    from build import format_relative_phrase
    assert format_relative_phrase("Atendido", "hoy") == "Atendido hoy"
    assert format_relative_phrase("Plantado", "hoy") == "Plantado hoy"

def test_format_relative_phrase_ayer():
    from build import format_relative_phrase
    assert format_relative_phrase("Atendido", "1 día") == "Atendido ayer"
    assert format_relative_phrase("Plantado", "1 día") == "Plantado ayer"

def test_format_relative_phrase_otros_casos():
    from build import format_relative_phrase
    assert format_relative_phrase("Atendido", "3 días") == "Atendido hace 3 días"
    assert format_relative_phrase("Plantado", "2 meses") == "Plantado hace 2 meses"
    assert format_relative_phrase("Atendido", "") == ""

def test_extract_metadata_atendido_label_hoy():
    from datetime import datetime, timedelta
    frontmatter = {"updated": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")}
    metadata, _ = extract_metadata("content", frontmatter, "Title")
    assert metadata["atendido_label"] == "Atendido hoy"

def test_extract_metadata_plantado_label_hoy():
    from datetime import datetime, timedelta
    frontmatter = {"created": (datetime.now() - timedelta(hours=2)).strftime("%Y-%m-%d %H:%M")}
    metadata, _ = extract_metadata("content", frontmatter, "Title")
    assert metadata["planted_label"] == "Plantado hoy"

def test_process_highlights():
    from build import process_highlights
    content = "This is ==highlighted== text."
    result = process_highlights(content)
    assert result == "This is <mark>highlighted</mark> text."
