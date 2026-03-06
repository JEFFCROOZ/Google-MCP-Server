# Knowledge Base MCP Server

A durable, queryable knowledge base built from a curated 90-article reading list covering data infrastructure, data governance, and AI/ML evolution over 20 years. Designed as a semantic retrieval layer that Claude can query to support data governance leadership, strategic planning, and continuous learning.

## Architecture

```
knowledge_base/articles/   ← Markdown files (source of truth, git-versioned)
         +
PostgreSQL + pgvector       ← Embedding store for semantic retrieval
         +
mcp_server/server.py        ← MCP server exposing tools to Claude
```

**Two-layer design:**
- Markdown files preserve content safely from link rot and are human-readable
- pgvector enables natural-language semantic search over embedded article summaries

## Knowledge Base Structure

90 articles organized into 10 learning phases:

| Phase | Name | Topics |
|-------|------|--------|
| 0 | Get Grounded | MAD Landscape history 2014–2024 |
| 1 | The Evolution | dbt, a16z, Airbyte, data engineering history |
| 2 | How The Thinking Changed | MDS, composable CDP, short stories |
| 3 | Purple People | Who the changes empower |
| 4 | Understanding People & Decisions | Behavior models, Fogg, Munger |
| 5 | Engineering Thinking | Amazon, technical debt, Maslow, AWS |
| 6 | Building Data Products | AI hierarchy, analytics engineering |
| 7 | Data Governance & Strategy | Semantic layer, catalogs, enablement |
| 8 | AI | LLMs, RAG, MCP, hallucination, biology of LLMs |
| 9 | Future, Culture & Teams | TikTok algorithm, culture, dbt/Snowflake |

## Prerequisites

- **Python 3.10+** (Python 3.12 recommended)
- **PostgreSQL 14+** with **pgvector** extension
  - [Postgres.app](https://postgresapp.com/) for macOS includes pgvector out of the box
- **Git**

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/Google-MCP-Server.git
cd Google-MCP-Server
```

### 2. Create and activate a Python virtual environment

```bash
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### 3. Set up PostgreSQL

Create the database and apply the schema:

```bash
createdb -U postgres knowledge_base
psql -U postgres -d knowledge_base -f knowledge_base/schema.sql
```

### 4. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```
DB_HOST=localhost
DB_PORT=5432
DB_NAME=knowledge_base
DB_USER=postgres
DB_PASSWORD=your_password_here
```

### 5. Run the ingest pipeline

This parses all 90 markdown article stubs, generates embeddings using `all-MiniLM-L6-v2`, and loads them into PostgreSQL:

```bash
python knowledge_base/ingest.py
```

Expected output:
```
Inserted : 90
Updated  : 0
Skipped  : 0
Errors   : 0
```

Options:
- `--dry-run` — parse files without writing to the database
- `--phase N` — only ingest a specific phase (0–9)

### 6. Register the MCP server with Claude Desktop

Add the following to your Claude Desktop config file:

**macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "knowledge-base": {
      "command": "/path/to/project/.venv/bin/python",
      "args": ["/path/to/project/mcp_server/server.py"],
      "env": {
        "DB_HOST": "localhost",
        "DB_PORT": "5432",
        "DB_NAME": "knowledge_base",
        "DB_USER": "postgres",
        "DB_PASSWORD": "your_password_here"
      }
    }
  }
}
```

Replace `/path/to/project/` with the absolute path to this repository on your machine.

Restart Claude Desktop after editing the config.

## MCP Tools

Once registered, Claude can use three tools:

| Tool | Arguments | Description |
|------|-----------|-------------|
| `semantic_search` | `query: str, limit: int = 5` | Natural-language semantic search using cosine similarity |
| `get_by_phase` | `phase: int` | Return all articles in a given phase (0–9) |
| `get_article` | `article_number: int` | Fetch a single article record by its number (1–90) |

**Example queries Claude can answer:**
- "What do you know about the modern data stack evolution?"
- "Find articles related to data governance strategy"
- "Show me everything in phase 8 about AI"

## Adding Article Content

Article stubs are pre-created with frontmatter and empty sections. Fill them in over time:

```markdown
---
article_number: 1
title: "The Future of the Modern Data Stack"
source_url: "https://..."
phase: 0
phase_name: "Get Grounded"
themes: ["modern data stack", "data infrastructure"]
date_captured: "2026-03-06"
---

## Summary
Your 2–3 sentence summary here.

## Key Excerpts
> Key quote from the article.
> Another relevant quote.

## Annotations
Personal notes and connections to other articles.
```

After updating articles, re-run the ingest to refresh embeddings:

```bash
python knowledge_base/ingest.py
```

## Project Structure

```
.
├── .env.example                    # Environment variable template
├── .gitignore
├── README.md
├── requirements.txt
├── knowledge_base/
│   ├── schema.sql                  # PostgreSQL schema with pgvector
│   ├── ingest.py                   # Parse + embed + upsert pipeline
│   └── articles/
│       ├── phase_0/                # 14 articles: MAD Landscape
│       ├── phase_1/                # 7 articles: The Evolution
│       ├── phase_2/                # 2 articles: How The Thinking Changed
│       ├── phase_3/                # 3 articles: Purple People
│       ├── phase_4/                # 8 articles: People & Decisions
│       ├── phase_5/                # 5 articles: Engineering Thinking
│       ├── phase_6/                # 10 articles: Building Data Products
│       ├── phase_7/                # 6 articles: Data Governance & Strategy
│       ├── phase_8/                # 16 articles: AI
│       └── phase_9/                # 18 articles: Culture, Teams & Future
└── mcp_server/
    └── server.py                   # FastMCP server
```

## Tech Stack

| Component | Technology |
|-----------|------------|
| Embeddings | `sentence-transformers` / `all-MiniLM-L6-v2` (384 dims, local) |
| Vector store | PostgreSQL 15 + pgvector (IVFFlat cosine index) |
| MCP framework | `FastMCP` (Python SDK) |
| DB client | `psycopg2-binary` + `pgvector` Python client |

## License

MIT
