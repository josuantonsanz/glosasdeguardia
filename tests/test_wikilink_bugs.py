import pytest
from pathlib import Path
from build import convert_wikilinks

def test_convert_wikilinks_ignores_transclusion():
    # We should NOT convert ![[Note]] into ![Note](Note.html)
    # because that makes the Markdown compiler turn it into an <img src="Note.html">
    # Our resolve_transclusion handles ![[Note]] instead.
    
    link_map = {
        "Note 1": "Note 1.html",
    }

    # Standard wikilink should convert
    content_link = "Look at [[Note 1]]"
    assert convert_wikilinks(content_link, link_map, current_filepath=Path("index.md")) == "Look at [Note 1](Note 1.html)"

    # Transclusion should NOT convert via convert_wikilinks
    content_transclusion = "Embed:\n![[Note 1]]"
    assert convert_wikilinks(content_transclusion, link_map, current_filepath=Path("index.md")) == "Embed:\n![[Note 1]]"
