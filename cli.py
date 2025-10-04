# cli.py
import argparse
import sys
import json
import pdfkit
from modules.fetcher import fetch_page
from modules.analyzer import run_full_analysis
from modules.report import ReportGenerator

# -------------------------
# Helper: format results to readable text
# -------------------------
def format_results_to_text(results):
    lines = [f"SEO Analysis Report for: {results.get('url')}\n"]
    
    # Basic info
    if "basic" in results:
        basic = results["basic"]
        lines.append("=== Basic Info ===")
        lines.append(f"Title: {basic['title']} (length: {basic['title_length']})")
        lines.append(f"Meta Description: {basic['meta_description']} (length: {basic['meta_description_length']})")
        lines.append(f"H1 tags: {', '.join(basic['h1']) or 'None'}")
        lines.append(f"H2 tags: {', '.join(basic['h2']) or 'None'}\n")
    
    # Word count
    if "word_count" in results:
        lines.append(f"Word count: {results['word_count']}\n")
    
    # Links
    if "links" in results:
        links = results["links"]
        lines.append("=== Links ===")
        lines.append(f"Total links on page: {links['total_links_on_page']}")
        lines.append(f"Internal links: {len(links['internal_links'])}, Broken: {len(links['broken_internal'])}")
        lines.append(f"External links: {len(links['external_links'])}, Broken: {len(links['broken_external'])}\n")
    
    # Images
    if "images" in results:
        images = results["images"]
        lines.append("=== Images ===")
        lines.append(f"Total images: {images['total_images']}")
        lines.append(f"Images missing alt: {images['missing_alt_count']}")
        if images['missing_alt_examples']:
            lines.append("Examples of missing alt:")
            for img in images['missing_alt_examples']:
                lines.append(f" - {img}")
        lines.append("")
    
    # Security
    if "security" in results:
        sec = results["security"]
        lines.append("=== Security ===")
        lines.append(f"HTTPS: {sec.get('https')}")
        lines.append(f"Status code: {sec.get('status_code')}")
        if sec.get("error"):
            lines.append(f"Error: {sec.get('error')}\n")
    
    # Performance
    if "performance" in results:
        perf = results["performance"]
        lines.append("=== Performance ===")
        lines.append(f"Time to first byte: {perf.get('time_to_first_byte')} sec")
        lines.append(f"Total download time: {perf.get('total_download')} sec")
        if perf.get("error"):
            lines.append(f"Error: {perf.get('error')}\n")
    
    return "\n".join(lines)

# -------------------------
# PDF helper function (pdfkit)
# -------------------------
def save_text_to_pdf_with_pdfkit(text, filename="seo_report.pdf"):
    # Convert plain text to simple HTML for better PDF formatting
    html_content = "<pre style='font-family: monospace; font-size: 12px'>" + text + "</pre>"
    try:
        pdfkit.from_string(html_content, filename)
        print(f"[OK] PDF saved as {filename}")
    except Exception as e:
        print(f"[ERROR] Failed to generate PDF: {e}")

# -------------------------
# Main CLI function
# -------------------------
def main():
    parser = argparse.ArgumentParser(
        prog="seo-analyzer",
        description="SEO Analyzer Tool - Analyze pages for SEO, performance, and security."
    )

    parser.add_argument(
        "command",
        choices=["analyze"],
        help="Main command (currently only 'analyze' is supported)."
    )
    parser.add_argument(
        "url",
        help="Target URL to analyze, e.g. https://example.org"
    )
    parser.add_argument(
        "--checks",
        type=str,
        default=None,
        help="Comma-separated list of checks (basic,wordcount,links,images,security,performance). Default: all"
    )
    parser.add_argument(
        "--report",
        type=str,
        choices=["console", "json", "html", "pdf"],
        default="console",
        help="Output format: console (default), json, html, pdf"
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="File path for saving report (only for json, html, pdf)"
    )
    parser.add_argument(
        "--pretty",
        action="store_true",
        help="Pretty-print JSON to console (only with --report json)"
    )

    args = parser.parse_args()

    # ----------------------
    # Fetch HTML
    # ----------------------
    html = fetch_page(args.url)
    if not html:
        print(f"[ERROR] Failed to fetch {args.url}")
        sys.exit(1)

    # ----------------------
    # Run analysis
    # ----------------------
    results = run_full_analysis(html, args.url, args.checks)

    # ----------------------
    # Handle output
    # ----------------------
    if args.report == "console":
        print("=== SEO Analyzer Results ===\n")
        print(format_results_to_text(results))

    elif args.report == "json":
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"[OK] JSON report saved to {args.output}")
        else:
            if args.pretty:
                print(json.dumps(results, indent=2, ensure_ascii=False))
            else:
                print(json.dumps(results, ensure_ascii=False))

    elif args.report == "html":
        rg = ReportGenerator(results)
        outfile = args.output or "seo_report.html"
        rg.to_html(outfile)
        print(f"[OK] HTML report saved to {outfile}")

    elif args.report == "pdf":
        text_report = format_results_to_text(results)
        outfile = args.output or "seo_report.pdf"
        save_text_to_pdf_with_pdfkit(text_report, outfile)

# -------------------------
# Run main
# -------------------------
if __name__ == "__main__":
    main()
