#!/usr/bin/env python3
"""
Ingest script for the knowledge base.

Reads all .md files from knowledge_base/articles/, parses YAML frontmatter,
generates sentence-transformer embeddings, and upserts into PostgreSQL.

Usage:
    python knowledge_base/ingest.py
    python knowledge_base/ingest.py --dry-run
    python knowledge_base/ingest.py --phase 0
"""

import os
import sys
import argparse
import glob
import yaml
import psycopg2
import psycopg2.extras
from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from pathlib import Path
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST", "localhost"),
        port=int(os.environ.get("DB_PORT", "5432")),
        dbname=os.environ.get("DB_NAME", "knowledge_base"),
        user=os.environ.get("DB_USER", "postgres"),
        password=os.environ.get("DB_PASSWORD", ""),
    )

# ---------------------------------------------------------------------------
# Embedding model (lazy singleton)
# ---------------------------------------------------------------------------

_model = None

def get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading sentence-transformer model (all-MiniLM-L6-v2)...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
        print("Model loaded.")
    return _model

def generate_embedding(text):
    # type: (str) -> List[float]
    model = get_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

# ---------------------------------------------------------------------------
# Markdown parsing
# ---------------------------------------------------------------------------

def parse_markdown_file(filepath):
    # type: (str) -> Optional[Dict[str, Any]]
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    if not content.startswith("---"):
        print("  WARN: No frontmatter in {}, skipping.".format(filepath))
        return None

    parts = content.split("---", 2)
    if len(parts) < 3:
        print("  WARN: Malformed frontmatter in {}, skipping.".format(filepath))
        return None

    raw_frontmatter = parts[1].strip()
    body = parts[2].strip()

    try:
        frontmatter = yaml.safe_load(raw_frontmatter)
    except yaml.YAMLError as exc:
        print("  ERROR: YAML parse error in {}: {}".format(filepath, exc))
        return None

    if frontmatter is None:
        frontmatter = {}

    summary = _extract_section(body, "Summary")
    key_excerpts = _extract_excerpts(body)
    annotations = _extract_section(body, "Annotations")

    return {
        "article_number": frontmatter.get("article_number"),
        "title": frontmatter.get("title", ""),
        "source_url": frontmatter.get("source_url", ""),
        "phase": frontmatter.get("phase"),
        "phase_name": frontmatter.get("phase_name", ""),
        "themes": frontmatter.get("themes", []),
        "date_captured": frontmatter.get("date_captured"),
        "summary": summary,
        "key_excerpts": key_excerpts,
        "annotations": annotations,
    }


def _extract_section(body, section_name):
    # type: (str, str) -> Optional[str]
    lines = body.splitlines()
    in_section = False
    collected = []
    for line in lines:
        if line.strip().startswith("## " + section_name):
            in_section = True
            continue
        if in_section:
            if line.strip().startswith("## "):
                break
            collected.append(line)
    if not collected:
        return None
    text = "\n".join(collected).strip()
    return text if text else None


def _extract_excerpts(body):
    # type: (str) -> Optional[List[str]]
    section_text = _extract_section(body, "Key Excerpts")
    if not section_text:
        return None
    excerpts = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("> "):
            excerpts.append(stripped[2:].strip())
        elif stripped.startswith(">"):
            excerpts.append(stripped[1:].strip())
    return excerpts if excerpts else None

# ---------------------------------------------------------------------------
# Embedding text construction
# ---------------------------------------------------------------------------

def build_embedding_text(record):
    # type: (Dict[str, Any]) -> str
    parts = []
    title = (record.get("title") or "").strip()
    if title:
        parts.append(title)
    phase_name = (record.get("phase_name") or "").strip()
    if phase_name:
        parts.append(phase_name)
    themes = record.get("themes") or []
    if themes:
        parts.append(", ".join(str(t) for t in themes))
    summary = record.get("summary") or ""
    if summary.strip():
        parts.append(summary.strip()[:2000])
    return ". ".join(parts)

# ---------------------------------------------------------------------------
# Database upsert
# ---------------------------------------------------------------------------

UPSERT_SQL = """
INSERT INTO articles (
    article_number, title, source_url, phase, phase_name,
    themes, summary, key_excerpts, annotations, date_captured, embedding
)
VALUES (
    %(article_number)s, %(title)s, %(source_url)s, %(phase)s, %(phase_name)s,
    %(themes)s, %(summary)s, %(key_excerpts)s, %(annotations)s, %(date_captured)s, %(embedding)s
)
ON CONFLICT (article_number) DO UPDATE SET
    title          = EXCLUDED.title,
    source_url     = EXCLUDED.source_url,
    phase          = EXCLUDED.phase,
    phase_name     = EXCLUDED.phase_name,
    themes         = EXCLUDED.themes,
    summary        = EXCLUDED.summary,
    key_excerpts   = EXCLUDED.key_excerpts,
    annotations    = EXCLUDED.annotations,
    date_captured  = EXCLUDED.date_captured,
    embedding      = EXCLUDED.embedding,
    updated_at     = NOW()
RETURNING id, (xmax = 0) AS inserted;
"""


def upsert_article(cursor, record, embedding):
    from pgvector.psycopg2 import register_vector
    date_captured = record.get("date_captured")
    if isinstance(date_captured, str):
        try:
            date_captured = date.fromisoformat(str(date_captured))
        except ValueError:
            date_captured = None

    params = {
        "article_number": record["article_number"],
        "title": record["title"],
        "source_url": record.get("source_url") or None,
        "phase": record["phase"],
        "phase_name": record["phase_name"],
        "themes": record.get("themes") or [],
        "summary": record.get("summary") or None,
        "key_excerpts": record.get("key_excerpts") or None,
        "annotations": record.get("annotations") or None,
        "date_captured": date_captured,
        "embedding": embedding,
    }
    cursor.execute(UPSERT_SQL, params)
    row = cursor.fetchone()
    return row[0], row[1]  # (id, inserted)

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def find_article_files(articles_dir, phase_filter):
    if phase_filter is not None:
        pattern = str(articles_dir / "phase_{}".format(phase_filter) / "*.md")
    else:
        pattern = str(articles_dir / "**" / "*.md")
    return sorted(glob.glob(pattern, recursive=True))


def run_ingest(dry_run=False, phase_filter=None):
    articles_dir = SCRIPT_DIR / "articles"
    if not articles_dir.exists():
        print("ERROR: Articles directory not found: {}".format(articles_dir))
        sys.exit(1)

    files = find_article_files(articles_dir, phase_filter)
    print("Found {} article files to process.".format(len(files)))
    if not files:
        print("Nothing to do.")
        return

    if dry_run:
        print("DRY RUN — no database writes.")

    conn = None
    cursor = None
    if not dry_run:
        conn = get_connection()
        from pgvector.psycopg2 import register_vector
        register_vector(conn)
        cursor = conn.cursor()

    inserted = updated = skipped = errors = 0

    for filepath in files:
        rel_path = Path(filepath).relative_to(PROJECT_ROOT)
        print("\nProcessing: {}".format(rel_path))

        record = parse_markdown_file(filepath)
        if record is None:
            skipped += 1
            continue

        if record.get("article_number") is None:
            print("  WARN: Missing article_number, skipping.")
            skipped += 1
            continue
        if not record.get("title"):
            print("  WARN: Missing title, skipping.")
            skipped += 1
            continue
        if record.get("phase") is None:
            print("  WARN: Missing phase, skipping.")
            skipped += 1
            continue

        embed_text = build_embedding_text(record)
        print("  #{} — {}".format(record["article_number"], record["title"][:60]))

        if dry_run:
            print("  [DRY RUN] embed text: {}...".format(embed_text[:80]))
            continue

        try:
            embedding = generate_embedding(embed_text)
            db_id, was_inserted = upsert_article(cursor, record, embedding)
            conn.commit()
            if was_inserted:
                print("  INSERTED (id={})".format(db_id))
                inserted += 1
            else:
                print("  UPDATED (id={})".format(db_id))
                updated += 1
        except Exception as exc:
            print("  ERROR: {}".format(exc))
            conn.rollback()
            errors += 1

    print("\n" + "=" * 50)
    print("Ingestion complete.")
    print("  Inserted : {}".format(inserted))
    print("  Updated  : {}".format(updated))
    print("  Skipped  : {}".format(skipped))
    print("  Errors   : {}".format(errors))
    print("  Total    : {}".format(len(files)))

    if cursor:
        cursor.close()
    if conn:
        conn.close()


def main():
    parser = argparse.ArgumentParser(description="Ingest knowledge base articles into PostgreSQL.")
    parser.add_argument("--dry-run", action="store_true", help="Parse but do not write to DB.")
    parser.add_argument("--phase", type=int, default=None, help="Only ingest a specific phase number.")
    args = parser.parse_args()
    run_ingest(dry_run=args.dry_run, phase_filter=args.phase)


if __name__ == "__main__":
    main()
