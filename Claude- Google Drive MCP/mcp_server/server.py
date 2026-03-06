#!/usr/bin/env python3
"""
Knowledge Base MCP Server.

Exposes three tools to Claude:
  - semantic_search(query, limit)  — full-text search using PostgreSQL tsvector
  - get_by_phase(phase)            — return all articles in a given phase
  - get_article(article_number)    — return one article by its number

Run:
    python mcp_server/server.py
"""

import os
import sys
from typing import Optional, List, Dict, Any
from pathlib import Path
from dotenv import load_dotenv

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
load_dotenv(PROJECT_ROOT / ".env")

import psycopg2
import psycopg2.extras
from mcp.server.fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Global DB connection — lazy singleton
# ---------------------------------------------------------------------------

_conn = None  # type: Optional[psycopg2.extensions.connection]


def get_connection():
    # type: () -> psycopg2.extensions.connection
    global _conn
    if _conn is None or _conn.closed:
        _conn = psycopg2.connect(
            host=os.environ.get("DB_HOST", "localhost"),
            port=int(os.environ.get("DB_PORT", "5432")),
            dbname=os.environ.get("DB_NAME", "knowledge_base"),
            user=os.environ.get("DB_USER", "postgres"),
            password=os.environ.get("DB_PASSWORD", ""),
            cursor_factory=psycopg2.extras.RealDictCursor,
        )
    return _conn


def clean_row(row):
    # type: (Any) -> Dict[str, Any]
    result = dict(row)
    result.pop("search_vector", None)
    if result.get("date_captured") is not None:
        result["date_captured"] = str(result["date_captured"])
    if result.get("created_at") is not None:
        result["created_at"] = result["created_at"].isoformat()
    if result.get("updated_at") is not None:
        result["updated_at"] = result["updated_at"].isoformat()
    return result


# ---------------------------------------------------------------------------
# MCP server
# ---------------------------------------------------------------------------

mcp = FastMCP(
    name="knowledge-base",
    instructions=(
        "A curated knowledge base of 90 articles on data infrastructure, "
        "data governance, and AI/ML — covering 20 years of industry evolution. "
        "Use semantic_search to find articles by concept or question, "
        "get_by_phase to browse a specific learning phase (0-9), and "
        "get_article to retrieve a full article record by number."
    ),
)


# ---------------------------------------------------------------------------
# MCP Tools
# ---------------------------------------------------------------------------

@mcp.tool()
def semantic_search(query, limit=5):
    # type: (str, int) -> List[Dict[str, Any]]
    """
    Search the knowledge base using full-text search.

    Embeds the query against article titles, themes, summaries, and annotations
    using PostgreSQL tsvector and returns ranked results.

    Args:
        query: A natural language question or concept (e.g. "what is data mesh?")
        limit: Maximum results to return (default 5, max 20)

    Returns:
        List of articles ordered by relevance, each with article_number, title,
        source_url, phase, phase_name, themes, summary, key_excerpts,
        annotations, date_captured, and similarity_score.
    """
    limit = min(max(1, limit), 20)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT
            id, article_number, title, source_url, phase, phase_name,
            themes, summary, key_excerpts, annotations, date_captured,
            created_at, updated_at,
            ts_rank(search_vector, query) AS similarity_score
        FROM articles, plainto_tsquery('english', %(q)s) query
        WHERE search_vector @@ query
        ORDER BY ts_rank(search_vector, query) DESC
        LIMIT %(l)s;
        """,
        {"q": query, "l": limit},
    )
    rows = cur.fetchall()
    cur.close()
    return [clean_row(r) for r in rows]


@mcp.tool()
def get_by_phase(phase):
    # type: (int) -> List[Dict[str, Any]]
    """
    Retrieve all articles belonging to a specific learning phase.

    Phases:
        0 - Get Grounded (MAD Landscape history 2014-2024)
        1 - The Evolution (dbt, a16z, Airbyte, data engineering history)
        2 - How The Thinking Changed (MDS, composable CDP, stories)
        3 - Purple People (who the changes empower)
        4 - Understanding People & Decisions (behavior models, Fogg, Munger)
        5 - Engineering Thinking (Amazon, technical debt, Maslow, AWS)
        6 - Building Data Products (AI hierarchy, analytics engineering)
        7 - Data Governance & Strategy (semantic layer, catalogs, enablement)
        8 - AI (LLMs, RAG, MCP, hallucination, biology of LLMs)
        9 - Future, Culture & Teams (TikTok algorithm, culture, dbt/Snowflake)

    Args:
        phase: Phase number (0-9)

    Returns:
        List of articles in that phase ordered by article_number.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, article_number, title, source_url, phase, phase_name,
               themes, summary, key_excerpts, annotations, date_captured,
               created_at, updated_at
        FROM articles
        WHERE phase = %(phase)s
        ORDER BY article_number;
        """,
        {"phase": phase},
    )
    rows = cur.fetchall()
    cur.close()
    return [clean_row(r) for r in rows]


@mcp.tool()
def get_article(article_number):
    # type: (int) -> Optional[Dict[str, Any]]
    """
    Retrieve the full record for a single article by its number.

    Args:
        article_number: The unique article number (1-90)

    Returns:
        Full article record including all fields, or None if not found.
    """
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, article_number, title, source_url, phase, phase_name,
               themes, summary, key_excerpts, annotations, date_captured,
               created_at, updated_at
        FROM articles
        WHERE article_number = %(n)s;
        """,
        {"n": article_number},
    )
    row = cur.fetchone()
    cur.close()
    return clean_row(row) if row else None


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    sys.stderr.write("Starting knowledge base MCP server...\n")
    mcp.run()
