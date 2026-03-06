#!/usr/bin/env python3
"""
Populate article summaries and key excerpts using the Claude API.

For each article stub, this script:
  1. Reads the existing markdown file
  2. Skips articles that already have a summary (unless --force)
  3. Fetches the article URL (falls back to metadata-only if inaccessible)
  4. Calls claude-sonnet-4-6 to generate a 2-3 sentence summary + key excerpts
  5. Writes the result back to the markdown file

After running, re-run ingest.py to update the search_vector in PostgreSQL.

Usage:
    python knowledge_base/populate_summaries.py
    python knowledge_base/populate_summaries.py --phase 0
    python knowledge_base/populate_summaries.py --article 1
    python knowledge_base/populate_summaries.py --force
    python knowledge_base/populate_summaries.py --dry-run
"""

import os
import sys
import re
import time
import glob
import argparse
import yaml
from pathlib import Path
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env", override=True)

import anthropic
import requests
from html.parser import HTMLParser

# ---------------------------------------------------------------------------
# HTML -> plain text
# ---------------------------------------------------------------------------

class HTMLTextExtractor(HTMLParser):
    SKIP_TAGS = {"script", "style", "nav", "footer", "header", "aside", "noscript"}

    def __init__(self):
        super().__init__()
        self._skip_depth = 0
        self._skip_tag = None
        self.chunks = []

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag):
        if tag.lower() in self.SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data):
        if self._skip_depth == 0:
            stripped = data.strip()
            if stripped:
                self.chunks.append(stripped)

    def get_text(self):
        return "\n".join(self.chunks)


def html_to_text(html):
    # type: (str) -> str
    extractor = HTMLTextExtractor()
    try:
        extractor.feed(html)
    except Exception:
        pass
    return extractor.get_text()


# ---------------------------------------------------------------------------
# URL fetch
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


def fetch_article_text(url, timeout=10):
    # type: (str, int) -> str
    """Fetch URL and return plain text. Returns empty string on failure."""
    if not url:
        return ""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout, allow_redirects=True)
        resp.raise_for_status()
        content_type = resp.headers.get("content-type", "")
        if "text/html" in content_type or "text/plain" in content_type:
            return html_to_text(resp.text)
        return ""
    except Exception as exc:
        sys.stderr.write("  FETCH WARN: {} — {}\n".format(url, exc))
        return ""


# ---------------------------------------------------------------------------
# Claude API
# ---------------------------------------------------------------------------

def build_prompt(title, phase_name, themes, url, article_text):
    # type: (str, str, list, str, str) -> str
    themes_str = ", ".join(themes) if themes else "none"
    text_block = article_text[:6000].strip() if article_text else ""
    has_text = bool(text_block)

    context = (
        "Article title: {}\n"
        "Phase: {}\n"
        "Themes: {}\n"
        "URL: {}\n"
    ).format(title, phase_name, themes_str, url)

    if has_text:
        context += "\nArticle content (first 6000 chars):\n---\n{}\n---\n".format(text_block)
    else:
        context += "\n[Article content could not be fetched — summarize from title and themes only.]\n"

    instructions = (
        "You are building a professional knowledge base for a data leader. "
        "Write a concise knowledge base entry for this article. "
        "Output ONLY the following two sections, with no extra commentary:\n\n"
        "## Summary\n"
        "Write 2-3 sentences capturing: (1) the core argument or finding, "
        "(2) why it matters for data governance or data leadership. "
        "Be specific and substantive — avoid generic summaries.\n\n"
        "## Key Excerpts\n"
        "Write 2-3 lines, each starting with '> ', capturing the most important "
        "insight, claim, or principle from the article. "
        "Paraphrase rather than quote verbatim. Each line should be 15-35 words.\n"
    )

    return context + "\n" + instructions


def generate_summary(client, title, phase_name, themes, url, article_text):
    # type: (anthropic.Anthropic, str, str, list, str, str) -> str
    """Call Claude and return the raw ## Summary + ## Key Excerpts block."""
    prompt = build_prompt(title, phase_name, themes, url, article_text)
    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text.strip()


# ---------------------------------------------------------------------------
# Markdown file parsing + writing
# ---------------------------------------------------------------------------

def parse_frontmatter(filepath):
    # type: (str) -> tuple
    """Returns (frontmatter_dict, raw_frontmatter_str, body_after_frontmatter)."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        return {}, "", content

    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}, "", content

    raw_fm = parts[1].strip()
    body = parts[2].strip()
    try:
        fm = yaml.safe_load(raw_fm) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, raw_fm, body


def has_summary(body):
    # type: (str) -> bool
    """Return True if the ## Summary section has non-empty content."""
    lines = body.splitlines()
    in_summary = False
    for line in lines:
        if line.strip() == "## Summary":
            in_summary = True
            continue
        if in_summary:
            if line.strip().startswith("## "):
                break
            if line.strip():
                return True
    return False


def write_article(filepath, raw_frontmatter, claude_output):
    # type: (str, str, str) -> None
    """Reconstruct the markdown file with the new Claude-generated sections."""
    # Normalise: ensure the output has exactly the two section headers we expect
    if "## Summary" not in claude_output:
        claude_output = "## Summary\n" + claude_output
    if "## Key Excerpts" not in claude_output:
        claude_output += "\n\n## Key Excerpts\n"

    new_content = (
        "---\n"
        + raw_frontmatter
        + "\n---\n\n"
        + claude_output.strip()
        + "\n\n## Annotations\n"
    )
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(new_content)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_article_files(articles_dir, phase_filter, article_filter):
    # type: (Path, object, object) -> list
    if article_filter is not None:
        pattern = str(articles_dir / "**" / "{:03d}_*.md".format(article_filter))
        return sorted(glob.glob(pattern, recursive=True))
    if phase_filter is not None:
        pattern = str(articles_dir / "phase_{}".format(phase_filter) / "*.md")
    else:
        pattern = str(articles_dir / "**" / "*.md")
    return sorted(glob.glob(pattern, recursive=True))


def run(phase_filter=None, article_filter=None, force=False, dry_run=False):
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key and not dry_run:
        print("ERROR: ANTHROPIC_API_KEY not set in .env or environment.")
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key) if not dry_run else None

    articles_dir = SCRIPT_DIR / "articles"
    files = find_article_files(articles_dir, phase_filter, article_filter)
    print("Found {} article files.".format(len(files)))

    processed = skipped = errors = 0

    for filepath in files:
        fm, raw_fm, body = parse_frontmatter(filepath)
        title = fm.get("title", filepath)
        article_number = fm.get("article_number", "?")
        url = fm.get("source_url", "")
        phase_name = fm.get("phase_name", "")
        themes = fm.get("themes", [])

        rel = Path(filepath).relative_to(PROJECT_ROOT)
        print("\n[{}] {}".format(article_number, title[:70]))

        if has_summary(body) and not force:
            print("  SKIP — summary already exists (use --force to overwrite)")
            skipped += 1
            continue

        if dry_run:
            print("  [DRY RUN] would fetch {} and call Claude".format(url))
            processed += 1
            continue

        # Fetch article text
        print("  Fetching URL...")
        article_text = fetch_article_text(url)
        if article_text:
            print("  Fetched {} chars of text.".format(len(article_text)))
        else:
            print("  Could not fetch content — using metadata only.")

        # Call Claude
        print("  Calling Claude API...")
        try:
            claude_output = generate_summary(client, title, phase_name, themes, url, article_text)
        except Exception as exc:
            print("  ERROR calling Claude: {}".format(exc))
            errors += 1
            time.sleep(2)
            continue

        # Write back
        write_article(filepath, raw_fm, claude_output)
        print("  Written.")
        processed += 1

        # Small delay to avoid hitting rate limits
        time.sleep(0.5)

    print("\n" + "=" * 50)
    print("Done.")
    print("  Processed : {}".format(processed))
    print("  Skipped   : {}".format(skipped))
    print("  Errors    : {}".format(errors))
    if processed > 0 and not dry_run:
        print("\nNext step: run ingest.py to refresh search_vector in PostgreSQL.")


def main():
    parser = argparse.ArgumentParser(description="Populate article summaries via Claude API.")
    parser.add_argument("--phase", type=int, default=None, help="Only process a specific phase (0-9).")
    parser.add_argument("--article", type=int, default=None, help="Only process a specific article number.")
    parser.add_argument("--force", action="store_true", help="Overwrite existing summaries.")
    parser.add_argument("--dry-run", action="store_true", help="Show what would happen without making changes.")
    args = parser.parse_args()
    run(
        phase_filter=args.phase,
        article_filter=args.article,
        force=args.force,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    main()
