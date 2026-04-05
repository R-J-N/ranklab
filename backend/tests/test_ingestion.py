import asyncio
import pytest
from app.core.ingestion import fetch_url, read_file


def test_read_file_plain_text():
    """Plain text bytes are decoded correctly."""
    content = "Hello, this is a test document."
    result = asyncio.run(read_file(content.encode("utf-8"), "doc.txt"))
    assert result == content


def test_read_file_ignores_invalid_bytes():
    """Invalid UTF-8 bytes are silently dropped."""
    content = b"Hello \xff\xfe world"
    result = asyncio.run(read_file(content, "doc.txt"))
    assert "Hello" in result
    assert "world" in result


def test_read_file_empty():
    """Empty file returns empty string."""
    result = asyncio.run(read_file(b"", "doc.txt"))
    assert result == ""


@pytest.mark.asyncio
async def test_fetch_url_returns_text_and_links():
    """Fetching a real URL returns non-empty text and a list of links."""
    text, links = await fetch_url("https://example.com")
    assert isinstance(text, str)
    assert len(text) > 0
    assert isinstance(links, list)


@pytest.mark.asyncio
async def test_fetch_url_links_are_absolute():
    """All returned links must be absolute http/https URLs."""
    _, links = await fetch_url("https://example.com")
    for link in links:
        assert link.startswith("http://") or link.startswith("https://")


@pytest.mark.asyncio
async def test_fetch_url_no_script_content():
    """Extracted text should not contain script or style tag artifacts."""
    text, _ = await fetch_url("https://example.com")
    assert "<script" not in text
    assert "<style" not in text
    assert "<head" not in text
    assert "<nav" not in text
    assert "<footer" not in text
