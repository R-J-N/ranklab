import io
import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

#GET url → parse HTML → strip noise → extract text → find links → filter → return (text, links)
# httpx.AsyncClient - asynchronous HTTP requests
# BeautifulSoup - used for web scraping
async def fetch_url(url: str) -> tuple[str, list[str]]:
    """
    Fetch a URL and return (visible_text, outbound_links).

    Steps:
    1. Use httpx.AsyncClient to GET the URL (follow redirects, set a timeout)
    2. Parse the response HTML with BeautifulSoup
    3. Remove non-visible tags: <script>, <style>, <head>, <nav>, <footer>
    4. Extract visible text using soup.get_text()
    5. Find all <a href="..."> tags and resolve relative URLs to absolute
       using urljoin(url, href)
    6. Only keep links with http/https scheme
    7. Return (text, links)
    """
    headers = {"User-Agent": "Mozilla/5.0 (compatible; Ranklab/1.0)"}
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0, headers=headers) as client:
        response = await client.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "head", "nav", "footer"]):
            tag.decompose()

    text = soup.get_text(separator=" ", strip=True)

    links = []
    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"].strip()
        #takes the base URL (the page we fetched) and the href, and figures out the full URL
        absolute = urljoin(url, href)
        if urlparse(absolute).scheme in ("http", "https"):
            links.append(absolute)

    return text, links


async def read_file(file_bytes: bytes, filename: str) -> str:
    """
    Extract plain text from an uploaded file.

    Steps:
    1. If filename ends with ".pdf":
       - Use pypdf.PdfReader to read the bytes (wrap in io.BytesIO)
       - Extract text from each page and join into one string
    2. Otherwise treat as plain text:
       - Decode bytes to string using utf-8 (ignore errors)
    3. Return the extracted text string
    """
    if filename.endswith(".pdf"):
        import pypdf
        reader = pypdf.PdfReader(io.BytesIO(file_bytes))
        return " ".join(page.extract_text() or "" for page in reader.pages)
    else:
        return file_bytes.decode("utf-8", errors="ignore")
