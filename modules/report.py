# modules/report.py
import json
from rich import print as rprint
from rich.table import Table
from rich.panel import Panel
from bs4 import BeautifulSoup
import pdfkit
import os

class ReportGenerator:
    def __init__(self, results: dict):
        self.results = results

    def print_terminal_summary(self):
        url = self.results.get("url", "N/A")
        rprint(Panel(f"[bold]SEO Analyzer Report[/bold]\n[url]{url}[/url]"))

        basic = self.results.get("basic", {})
        if basic:
            t = Table(title="Meta & Headings Summary")
            t.add_column("Field")
            t.add_column("Value")
            t.add_row("Title", basic.get("title", ""))
            t.add_row("Title length", str(basic.get("title_length", "")))
            t.add_row("Meta description", basic.get("meta_description", "")[:120] + ("..." if len(basic.get("meta_description",""))>120 else ""))
            t.add_row("H1 count", str(len(basic.get("h1", []))))
            t.add_row("H2 count", str(len(basic.get("h2", []))))
            rprint(t)

        wc = self.results.get("word_count")
        if wc is not None:
            rprint(f"[bold]Word Count:[/bold] {wc}")

        links = self.results.get("links")
        if links:
            rprint(f"[bold]Links on page:[/bold] total={links.get('total_links_on_page')}, internal={len(links.get('internal_links',[]))}, external={len(links.get('external_links',[]))}")
            if links.get("broken_internal"):
                rprint(f"[red]Broken internal links: {len(links.get('broken_internal'))}[/red]")
            if links.get("broken_external"):
                rprint(f"[red]Broken external links: {len(links.get('broken_external'))}[/red]")

        images = self.results.get("images")
        if images:
            rprint(f"[bold]Images:[/bold] total={images.get('total_images')}, missing_alt={images.get('missing_alt_count')}")

        sec = self.results.get("security")
        if sec:
            rprint(f"[bold]Security[/bold] HTTPS: {sec.get('https')}, status: {sec.get('status')}")

        perf = self.results.get("performance")
        if perf:
            rprint(f"[bold]Performance[/bold] TTFB: {perf.get('time_to_first_byte')}s, total_download: {perf.get('total_download')}s")

    def export(self, fmt, out_path):
        supported = ["json", "html", "pdf"]
        if fmt not in supported:
            raise ValueError("Unsupported format")

        if fmt == "json":
            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(self.results, f, indent=2, ensure_ascii=False)
            return

        # HTML generation: a simple readable report
        html = self._build_html()
        if fmt == "html":
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(html)
            return

        if fmt == "pdf":
            # create a temporary html and convert to pdf via pdfkit
            temp = out_path + ".tmp.html"
            with open(temp, "w", encoding="utf-8") as f:
                f.write(html)
            try:
                # pdfkit requires wkhtmltopdf installed on system
                pdfkit.from_file(temp, out_path)
            finally:
                if os.path.exists(temp):
                    os.remove(temp)
            return

    def _build_html(self):
        s = []
        s.append("<html><head><meta charset='utf-8'><title>SEO Report</title></head><body>")
        s.append(f"<h1>SEO Analyzer Report for {self.results.get('url','')}</h1>")
        basic = self.results.get("basic", {})
        s.append("<h2>Meta & Headings</h2><ul>")
        s.append(f"<li><strong>Title:</strong> {basic.get('title','')}</li>")
        s.append(f"<li><strong>Title length:</strong> {basic.get('title_length','')}</li>")
        s.append(f"<li><strong>Meta description:</strong> {basic.get('meta_description','')}</li>")
        s.append(f"<li><strong>H1 count:</strong> {len(basic.get('h1',[]))}</li>")
        s.append("</ul>")

        wc = self.results.get("word_count")
        if wc is not None:
            s.append(f"<h2>Word Count</h2><p>{wc}</p>")

        links = self.results.get("links")
        if links:
            s.append("<h2>Links</h2>")
            s.append(f"<p>Total on page: {links.get('total_links_on_page')}</p>")
            s.append("<h3>Broken Internal</h3>")
            s.append("<ul>")
            for b in links.get("broken_internal", []):
                s.append(f"<li>{b}</li>")
            s.append("</ul>")

        images = self.results.get("images")
        if images:
            s.append("<h2>Images</h2>")
            s.append(f"<p>Total images: {images.get('total_images')} — Missing alt: {images.get('missing_alt_count')}</p>")

        sec = self.results.get("security")
        if sec:
            s.append("<h2>Security</h2>")
            s.append(f"<p>HTTPS: {sec.get('https')}, Status: {sec.get('status')}</p>")

        perf = self.results.get("performance")
        if perf:
            s.append("<h2>Performance</h2>")
            s.append(f"<p>TTFB: {perf.get('time_to_first_byte')}s — Total download: {perf.get('total_download')}s</p>")

        s.append("</body></html>")
        return "\n".join(s)
