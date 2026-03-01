import pytest
from pathlib import Path
from build import resolve_transclusions

class MockPost:
    contents = "Full text here.\n\n# Header\nThis is the heading body.\n\nAnd a loose block. ^my-block"

def test_transclude_full_note():
    vault_content = {
        "Source Note": MockPost.contents
    }
    content = "Here is an embed:\n\n![[Source Note]]\n\nEnd."
    resolved = resolve_transclusions(content, vault_content)
    assert "Full text here." in resolved

def test_transclude_block_reference():
    vault_content = {
        "Source Note": MockPost.contents
    }
    content = "Block embed:\n\n![[Source Note#^my-block]]"
    resolved = resolve_transclusions(content, vault_content)
    assert "And a loose block." in resolved
    # It should strip the ^my-block symbol on render
    assert "^my-block" not in resolved
    # It shouldn't contain the full note
    assert "Full text here." not in resolved

def test_transclude_heading_reference():
    vault_content = {
        "Source Note": MockPost.contents
    }
    content = "Heading embed:\n\n![[Source Note#Header]]"
    resolved = resolve_transclusions(content, vault_content)
    assert "This is the heading body." in resolved
    assert "Full text here." not in resolved
