# modules/analyzer.py
import re
import time
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin

# -------------------------
# Basic on-page analysis
# -------------------------
def analyze_basic(html):
    """Extract title, meta description, h1/h2 lists and basic flags."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # Title
    title = ""
    if soup.title and soup.title.string:
        title = soup.title.string.strip()

    # Meta description (case-insensitive)
    meta_desc = ""
    md = soup.find("meta", attrs={"name": "description"})
    if not md:
        # try capitalized attribute variant
        md = soup.find("meta", attrs={"Name": "description"})
    if md and md.get("content"):
        meta_desc = md.get("content").strip()

    # H1 / H2
    h1s = [h.get_text(strip=True) for h in soup.find_all("h1")]
    h2s = [h.get_text(strip=True) for h in soup.find_all("h2")]

    return {
        "title": title,
        "title_length": len(title),
        "meta_description": meta_desc,
        "meta_description_length": len(meta_desc),
        "h1": h1s,
        "h2": h2s,
    }

# -------------------------
# Word count & content
# -------------------------
def analyze_word_count(html):
    """Count visible words (rough estimate)."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    # remove script/style text to avoid noise
    for tag in soup(["script", "style", "noscript"]):
        tag.extract()
    text = soup.get_text(separator=" ", strip=True)
    words = re.findall(r"\b\w+\b", text)
    return len(words)

# -------------------------
# Links analysis (single page, fast)
# -------------------------
def analyze_links(html, base_url, max_check_links=50):
    """
    Extract internal and external links on a single page.
    Does lightweight HEAD checks for first N links to detect broken ones.
    """
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    anchors = soup.find_all("a", href=True)
    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc

    internal = set()
    external = set()
    for a in anchors:
        href = a.get("href").strip()
        if href.startswith("mailto:") or href.startswith("javascript:") or href.startswith("#"):
            continue
        if href.startswith("http://") or href.startswith("https://"):
            if urlparse(href).netloc == base_domain:
                internal.add(href)
            else:
                external.add(href)
        else:
            # relative path -> resolve to absolute (considered internal)
            internal.add(urljoin(base_url, href))

    result = {
        "total_links_on_page": len(anchors),
        "internal_links": list(internal),
        "external_links": list(external),
        "broken_internal": [],
        "broken_external": [],
    }

    # Lightweight broken-link check for first max_check_links each
    def check_url(u):
        try:
            r = requests.head(u, timeout=6, allow_redirects=True, headers={"User-Agent": "SEO-Analyzer/1.0"})
            code = r.status_code
            if code >= 400:
                return False, code
            return True, code
        except Exception:
            return False, None

    # check only a subset to keep runtime reasonable
    for link in list(result["internal_links"])[:max_check_links]:
        ok, code = check_url(link)
        if not ok:
            result["broken_internal"].append({"url": link, "status": code})

    for link in list(result["external_links"])[:max_check_links]:
        ok, code = check_url(link)
        if not ok:
            result["broken_external"].append({"url": link, "status": code})

    return result

# -------------------------
# Images
# -------------------------
def analyze_images(html, base_url=None):
    """Count images, missing alt attributes, example list."""
    try:
        soup = BeautifulSoup(html, "lxml")
    except Exception:
        soup = BeautifulSoup(html, "html.parser")

    imgs = soup.find_all("img")
    total = len(imgs)
    missing_alt = []
    examples = []
    for img in imgs:
        alt = (img.get("alt") or "").strip()
        src = img.get("src") or ""
        if src and base_url and not src.startswith("http"):
            src = urljoin(base_url, src)
        if not alt:
            missing_alt.append(src)
        if len(examples) < 10:
            examples.append({"src": src, "alt": alt})
    return {"total_images": total, "missing_alt_count": len(missing_alt), "missing_alt_examples": missing_alt[:10], "examples": examples}

# -------------------------
# Security & simple perf
# -------------------------
def analyze_security(url):
    """Basic HTTPS presence and headers check."""
    result = {"https": False, "status_code": None, "headers": {}, "error": None}
    try:
        r = requests.get(url, timeout=8, headers={"User-Agent": "SEO-Analyzer/1.0"})
        result["status_code"] = r.status_code
        result["headers"] = dict(r.headers)
        result["https"] = urlparse(url).scheme == "https"
    except Exception as e:
        result["error"] = str(e)
    return result

def analyze_performance_simple(url):
    """
    Simple timing: measures time to first byte and total HTML download time.
    (For Core Web Vitals integrate Lighthouse/PageSpeed)
    """
    timings = {"time_to_first_byte": None, "total_download": None, "status_code": None, "error": None}
    try:
        start = time.time()
        r = requests.get(url, stream=True, timeout=12, headers={"User-Agent": "SEO-Analyzer/1.0"})
        first = time.time()
        _ = r.content  # force download
        end = time.time()
        timings["time_to_first_byte"] = round(first - start, 3)
        timings["total_download"] = round(end - start, 3)
        timings["status_code"] = r.status_code
    except Exception as e:
        timings["error"] = str(e)
    return timings

# -------------------------
# Combined runner
# -------------------------
def run_full_analysis(html, base_url, checks=None):
    """
    Run a set of checks and return a structured dict.
    - html: the page HTML (string)
    - base_url: original URL (for resolving relative links, images)
    - checks: comma-separated string or list of checks to run (None means all)
    """
    if checks:
        if isinstance(checks, str):
            checks = [c.strip().lower() for c in checks.split(",")]
        else:
            checks = [c.strip().lower() for c in checks]
    else:
        checks = ["basic", "wordcount", "links", "images", "security", "performance"]

    results = {"url": base_url, "timestamp": int(time.time()), "checks_run": checks}

    html_input = html

    if "basic" in checks:
        results["basic"] = analyze_basic(html_input)

    if "wordcount" in checks:
        results["word_count"] = analyze_word_count(html_input)

    if "links" in checks:
        results["links"] = analyze_links(html_input, base_url)

    if "images" in checks:
        results["images"] = analyze_images(html_input, base_url)

    if "security" in checks:
        results["security"] = analyze_security(base_url)

    if "performance" in checks:
        results["performance"] = analyze_performance_simple(base_url)

    return results
