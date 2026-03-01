import pytest
from pathlib import Path
from build import build_link_map, convert_wikilinks

class MockPost:
    def __init__(self, content="", metadata=None):
        self.content = content
        self.metadata = metadata or {}

def test_build_link_map_maintains_folder_structure():
    # Setup mock notes with nested paths
    base = Path("content")
    notes = [
        (base / "index.md", MockPost()),
        (base / "Folder A" / "Note 1.md", MockPost(metadata={"aliases": ["First Note"]})),
        (base / "Folder B" / "Note 1.md", MockPost()), # Duplicate name, different folder
        (base / "Folder A" / "Subfolder" / "Deep Note.md", MockPost()),
    ]
    
    # Execution
    link_map = build_link_map(notes, base_dir=base)
    
    # We expect the dictionary to map the exact filepath (relative to content) AND the filename to the URL
    assert link_map["index"] == "index.html"
    assert link_map["Folder A/Note 1"] == "Folder A/Note 1.html"
    assert link_map["Folder B/Note 1"] == "Folder B/Note 1.html"
    
    # Aliases should map to the correct full path URL
    assert link_map["First Note"] == "Folder A/Note 1.html"

def test_convert_wikilinks_with_nested_paths():
    link_map = {
        "index": "index.html",
        "Folder A/Note 1": "Folder A/Note 1.html",
        "Folder B/Note 1": "Folder B/Note 1.html",
        "Deep Note": "Folder A/Subfolder/Deep Note.html"
    }

    # Test link from root 'index.md'
    content1 = "Go to [[Deep Note]]"
    assert convert_wikilinks(content1, link_map, current_filepath=Path("index.md")) == "Go to [Deep Note](Folder A/Subfolder/Deep Note.html)"

    # Test link from inside a folder
    content2 = "I prefer [[Folder B/Note 1]]"
    assert convert_wikilinks(content2, link_map, current_filepath=Path("Folder A/Note 1.md")) == "I prefer [Folder B/Note 1](../Folder B/Note 1.html)"

    # Test link from deep subfolder with alias
    content3 = "Check out [[Folder A/Note 1|My First Note]]"
    assert convert_wikilinks(content3, link_map, current_filepath=Path("Folder A/Subfolder/Deep Note.md")) == "Check out [My First Note](../../Folder A/Note 1.html)"

def test_convert_wikilinks_ignores_unpublished():
    link_map = {
        "Published Note": "Published Note.html"
    }
    
    # Link to published note should work
    content_pub = "See [[Published Note]]"
    assert convert_wikilinks(content_pub, link_map, current_filepath=Path("index.md")) == "See [Published Note](Published Note.html)"
    
    # Link to UNPUBLISHED note (not in link_map) should be plain text
    content_unpub = "See [[Secret Note]]"
    assert convert_wikilinks(content_unpub, link_map, current_filepath=Path("index.md")) == "See Secret Note"
    
    # Link to UNPUBLISHED note with alias should be alias text
    content_alias = "See [[Secret Note|Alias]]"
    assert convert_wikilinks(content_alias, link_map, current_filepath=Path("index.md")) == "See Alias"
