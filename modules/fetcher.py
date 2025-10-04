# modules/fetcher.py
import requests
from requests.exceptions import RequestException
from urllib.parse import urljoin, urlparse
import time

DEFAULT_HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; SEO-Analyzer/1.0; +https://github.com/yourname/seo-analyzer)"
}

def fetch_page(url, timeout=12):
    """
    Fetch HTML content of the given URL (basic GET).
    Returns: text or None
    """
    try:
        r = requests.get(url, headers=DEFAULT_HEADERS, timeout=timeout)
        r.raise_for_status()
        return r.text
    except RequestException as e:
        print(f"[ERROR] Could not fetch {url}: {e}")
        return None

def check_robots(base_url, timeout=8):
    """
    Fetch robots.txt and return content (or None)
    """
    try:
        parsed = urlparse(base_url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        r = requests.get(robots_url, headers=DEFAULT_HEADERS, timeout=timeout)
        if r.status_code == 200:
            return {"found": True, "content": r.text, "url": robots_url}
        return {"found": False, "status_code": r.status_code, "url": robots_url}
    except RequestException:
        return {"found": False}

def fetch_sitemap(base_url, timeout=8):
    """
    Try common sitemap locations: /sitemap.xml and robots.txt sitemap: lines
    Returns dict with found:boolean and url or None
    """
    from bs4 import BeautifulSoup

    parsed = urlparse(base_url)
    root = f"{parsed.scheme}://{parsed.netloc}"

    # 1) Try /sitemap.xml
    try:
        r = requests.get(urljoin(root, "/sitemap.xml"), headers=DEFAULT_HEADERS, timeout=timeout)
        if r.status_code == 200 and "<urlset" in r.text:
            return {"found": True, "url": urljoin(root, "/sitemap.xml"), "content": r.text}
    except RequestException:
        pass

    # 2) Check robots.txt for Sitemap: lines
    try:
        rob = requests.get(urljoin(root, "/robots.txt"), headers=DEFAULT_HEADERS, timeout=timeout)
        if rob.status_code == 200:
            for line in rob.text.splitlines():
                if line.lower().startswith("sitemap:"):
                    sitemap_url = line.split(":", 1)[1].strip()
                    return {"found": True, "url": sitemap_url}
    except RequestException:
        pass

    return {"found": False}
