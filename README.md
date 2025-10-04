# SEO Analyzer
A modular CLI SEO analyzer tool written in python

## install
1. create a activate virtualenv :
```bash
    python -m venv venv
# windows
    venv\scripts\activate

# linux / macOS
    source venv/bin/activate

2.Install_dependencies
    pip install -r requirements.txt

Optional (for PDF export):
    Install wkhtmltopdf on your system and make sure it's in PATH

USAGE :
Basic:
    python cli.py https://example.com (if python didn't work try py)

Export HTML :
    python cli.py https://example.com --report html --output myreport

Export PDF :
    python cli.py https://example.com --report pdf --output myreport


Flags:

--meta, --content, --images, --links, --performance, --security
--depth N (crawl depth)
--max-pages N (limit pages for crawl)
--quiet (minimal console output)

Structure :

cli.py — main entry
modules/fetcher.py — fetching and robots/sitemap helpers
modules/analyzer.py — SEO checks
modules/report.py — terminal/HTML/JSON/PDF outputs

Notes & next steps :

Add Lighthouse/PageSpeed integration for lab/field CWV metrics.
Add NER/readability (spaCy/textstat) for content quality scoring.
Add OAuth GSC / backlink API integrations for off-page metrics.

---

## How to Install & Run (step-by-step)

1. Ensure your `venv` is active in VS Code terminal:
   - Windows:
     ```
     venv\Scripts\activate
     ```
   - Mac/Linux:
     ```
     source venv/bin/activate
     ```

2. Install dependencies:
pip install -r requirements.txt

3. Run a quick analysis:
python cli.py https://www.wikipedia.org

4. Export HTML:
python cli.py https://www.wikipedia.org --report html --output wiki_report

5. Export PDF (if wkhtmltopdf is installed):
python cli.py https://www.wikipedia.org --report pdf --output wiki_report


---

## Final notes (practical & honest)
- This project is intentionally **modular** and set up to grow. The code focuses on **useful checks** that don’t require paid APIs.  
- For full production usage you’ll want to add: concurrency (async crawling), more robust error handling & retry/backoff, caching, tests, and optional authentication to fetch Search Console data or use PageSpeed APIs.  
- If you want, I can now:
- Convert link checking to **async** to speed it up.
- Add TF-IDF / keyword density with `scikit-learn`.
- Add a Streamlit web UI.
- Add a Lighthouse integration example.
