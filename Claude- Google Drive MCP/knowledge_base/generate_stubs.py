#!/usr/bin/env python3
"""
One-time script to generate all 90 article stub markdown files.
Run once: python knowledge_base/generate_stubs.py
"""
import os
from pathlib import Path

BASE = Path(__file__).resolve().parent / "articles"

ARTICLES = [
    # (article_number, phase, phase_name, title, url, themes)
    # --- Phase 0: Get Grounded ---
    (1, 0, "Get Grounded", "The Future of the Modern Data Stack", "https://www.getdbt.com/blog/future-of-the-modern-data-stack", ["modern data stack", "data infrastructure", "dbt", "data engineering"]),
    (2, 0, "Get Grounded", "MAD Landscape 2014: The State of Big Data", "https://mattturck.com/the-state-of-big-data-in-2014-a-chart/", ["MAD landscape", "big data", "market landscape", "data ecosystem"]),
    (3, 0, "Get Grounded", "MAD Landscape 2016: Big Data Landscape", "https://mattturck.com/big-data-landscape/", ["MAD landscape", "big data", "market landscape", "data ecosystem"]),
    (4, 0, "Get Grounded", "MAD Landscape 2017: Big Data 2017", "https://mattturck.com/bigdata2017/", ["MAD landscape", "big data", "market landscape", "data ecosystem"]),
    (5, 0, "Get Grounded", "MAD Landscape 2018: Big Data 2018", "https://mattturck.com/bigdata2018/", ["MAD landscape", "big data", "market landscape", "data ecosystem"]),
    (6, 0, "Get Grounded", "MAD Landscape 2019: Data 2019", "https://mattturck.com/data2019/", ["MAD landscape", "data ecosystem", "market landscape"]),
    (7, 0, "Get Grounded", "MAD Landscape 2019: 2019 Trends", "https://mattturck.com/2019trends/", ["MAD landscape", "data trends", "market landscape"]),
    (8, 0, "Get Grounded", "MAD Landscape 2020: Data 2020", "https://mattturck.com/data2020/", ["MAD landscape", "data ecosystem", "market landscape"]),
    (9, 0, "Get Grounded", "MAD Landscape 2021: Data 2021", "https://mattturck.com/data2021/", ["MAD landscape", "data ecosystem", "market landscape"]),
    (10, 0, "Get Grounded", "MAD Landscape 2023: Part I", "https://mattturck.com/mad2023/", ["MAD landscape", "AI", "machine learning", "data ecosystem"]),
    (11, 0, "Get Grounded", "MAD Landscape 2023: Part II", "https://mattturck.com/mad2023-part-ii/", ["MAD landscape", "AI", "machine learning", "data ecosystem"]),
    (12, 0, "Get Grounded", "MAD Landscape 2023: Part III", "https://mattturck.com/mad2023-part-iii/", ["MAD landscape", "AI", "machine learning", "data ecosystem"]),
    (13, 0, "Get Grounded", "MAD Landscape 2023: Part IV", "https://mattturck.com/mad2023-part-iv/", ["MAD landscape", "AI", "machine learning", "data ecosystem"]),
    (14, 0, "Get Grounded", "MAD Landscape 2024", "https://mattturck.com/mad2024/", ["MAD landscape", "AI", "data ecosystem", "market landscape"]),
    # --- Phase 1: The Evolution ---
    (15, 1, "The Evolution", "Building a Mature Analytics Workflow", "https://www.getdbt.com/blog/building-a-mature-analytics-workflow", ["analytics engineering", "modern data stack", "dbt", "data workflow"]),
    (16, 1, "The Evolution", "Is the Modern Data Stack Still a Thing?", "https://roundup.getdbt.com/p/is-the-modern-data-stack-still-a", ["modern data stack", "data engineering", "industry trends"]),
    (17, 1, "The Evolution", "Emerging Architectures for Modern Data Infrastructure (2020)", "https://a16z.com/emerging-architectures-for-modern-data-infrastructure-2020/", ["data infrastructure", "architecture", "a16z", "modern data stack"]),
    (18, 1, "The Evolution", "Emerging Architectures for Modern Data Infrastructure (Updated)", "https://a16z.com/emerging-architectures-for-modern-data-infrastructure/", ["data infrastructure", "architecture", "a16z", "modern data stack"]),
    (19, 1, "The Evolution", "Data Engineering: Past, Present, and Future", "https://airbyte.com/blog/data-engineering-past-present-and-future", ["data engineering", "history", "future of data", "ELT"]),
    (20, 1, "The Evolution", "What Happened to Big Data?", "https://www.confluent.io/blog/what-happened-to-big-data/", ["big data", "data engineering", "Kafka", "streaming", "history"]),
    (21, 1, "The Evolution", "The Rise of the Composable CDP", "https://a16z.com/the-rise-of-the-composable-cdp/", ["CDP", "composable", "data infrastructure", "a16z", "customer data"]),
    # --- Phase 2: How The Thinking Changed ---
    (22, 2, "How The Thinking Changed", "The Data Team: A Short Story", "https://erikbern.com/2021/07/07/the-data-team-a-short-story.html", ["data teams", "organizational dynamics", "data culture", "parable"]),
    (23, 2, "How The Thinking Changed", "Purple People: A Presentation", "https://docs.google.com/presentation/d/1NlV4wDwTjDQru4DfqiPKaU39BIhzW1PTJTzBHz7t3vY/edit", ["purple people", "data roles", "data culture", "cross-functional"]),
    # --- Phase 3: Purple People ---
    (24, 3, "Purple People", "Purple People (TDWI)", "https://tdwi.org/blogs/tdwi-blog/2010/04/purple-people.aspx", ["purple people", "data roles", "business intelligence", "data culture"]),
    (25, 3, "Purple People", "We, The Purple People", "https://www.getdbt.com/blog/we-the-purple-people", ["purple people", "analytics engineering", "data roles", "dbt"]),
    (26, 3, "Purple People", "Rise of the Data Product Manager", "https://medium.com/@treycausey/rise-of-the-data-product-manager-2fb9961b21d1", ["data product manager", "data products", "data roles", "product management"]),
    # --- Phase 4: Understanding People & Decisions ---
    (27, 4, "Understanding People & Decisions", "Know Your Customer's Jobs to Be Done", "https://hbr.org/2016/09/know-your-customers-jobs-to-be-done", ["jobs to be done", "customer understanding", "product thinking", "HBR"]),
    (28, 4, "Understanding People & Decisions", "The XY Problem", "https://xyproblem.info/", ["problem framing", "communication", "debugging", "mental models"]),
    (29, 4, "Understanding People & Decisions", "The Scientists Who Make Apps Addictive", "https://www.economist.com/1843/2016/10/20/the-scientists-who-make-apps-addictive", ["behavior design", "engagement", "technology", "human behavior"]),
    (30, 4, "Understanding People & Decisions", "Captology: The Fogg Behavior Model", "https://www.demenzemedicinagenerale.net/images/mens-sana/Captology_Fogg_Behavior_Model.pdf", ["Fogg behavior model", "captology", "behavior change", "persuasion"]),
    (31, 4, "Understanding People & Decisions", "Strong Opinions, Weakly Held", "https://medium.com/@ameet/strong-opinions-weakly-held-a-framework-for-thinking-6530d417e364", ["decision making", "mental models", "frameworks", "epistemics"]),
    (32, 4, "Understanding People & Decisions", "The Psychology of Human Misjudgment (Munger)", "https://fs.blog/great-talks/psychology-human-misjudgment/", ["mental models", "cognitive biases", "Charlie Munger", "decision making"]),
    (33, 4, "Understanding People & Decisions", "Amazon CEO Andy Jassy 2023 Letter to Shareholders", "https://www.aboutamazon.com/news/company-news/amazon-ceo-andy-jassy-2023-letter-to-shareholders", ["Amazon", "leadership", "technology strategy", "AI", "organizational thinking"]),
    (34, 4, "Understanding People & Decisions", "Simple Sabotage for Software", "https://erikbern.com/2023/12/13/simple-sabotage-for-software", ["engineering culture", "organizational dysfunction", "software teams", "leadership"]),
    # --- Phase 5: Engineering Thinking ---
    (35, 5, "Engineering Thinking", "TBM 220: Effort vs. Value Curves", "https://cutlefish.substack.com/p/tbm-220-effort-vs-value-curves", ["product management", "prioritization", "value", "effort", "decision making"]),
    (36, 5, "Engineering Thinking", "Choose Boring Technology", "https://boringtechnology.club/", ["engineering", "technology choices", "innovation tokens", "simplicity"]),
    (37, 5, "Engineering Thinking", "Towards an Understanding of Technical Debt", "https://kellanem.com/notes/towards-an-understanding-of-technical-debt", ["technical debt", "engineering", "software quality", "refactoring"]),
    (38, 5, "Engineering Thinking", "Designing for a Hierarchy of Needs", "https://www.smashingmagazine.com/2010/04/designing-for-a-hierarchy-of-needs/", ["Maslow hierarchy", "product design", "UX", "user needs"]),
    (39, 5, "Engineering Thinking", "A Brief History of Block Storage at AWS", "https://www.allthingsdistributed.com/2024/08/continuous-reinvention-a-brief-history-of-block-storage-at-aws.html", ["AWS", "cloud storage", "engineering history", "first principles", "infrastructure"]),
    # --- Phase 6: Building Data Products ---
    (40, 6, "Building Data Products", "The AI Hierarchy of Needs", "https://hackernoon.com/the-ai-hierarchy-of-needs-18f111fcc007", ["AI", "machine learning", "data infrastructure", "hierarchy of needs", "MLOps"]),
    (41, 6, "Building Data Products", "4 Pillars of Analytics", "https://medium.com/analytics-and-data/4-pillars-of-analytics-1ee79e2e5f5f", ["analytics", "data products", "frameworks", "data teams"]),
    (42, 6, "Building Data Products", "DataOps Principles", "https://retina.ai/blog/dataops-principles/", ["DataOps", "data pipelines", "data quality", "engineering"]),
    (43, 6, "Building Data Products", "Quasi-Mystical Arts of Data and the Analytics Engineer", "https://roundup.getdbt.com/p/quasi-mystical-arts-of-data-and-the", ["analytics engineering", "dbt", "data products", "craft"]),
    (44, 6, "Building Data Products", "Data Systems Tend Towards Production", "https://ian-macomber.medium.com/data-systems-tend-towards-production-be5a86f65561", ["data systems", "production", "data engineering", "system design"]),
    (45, 6, "Building Data Products", "The Future of Notebooks", "https://deepnote.com/blog/future-of-notebooks", ["notebooks", "data science", "tooling", "analytics"]),
    # --- Phase 7: Data Governance & Strategy ---
    (46, 7, "Data Governance & Strategy", "What's Your Data Strategy?", "https://hbr.org/2017/05/whats-your-data-strategy", ["data strategy", "HBR", "data governance", "organizational data"]),
    (47, 7, "Data Governance & Strategy", "The Semantic Layer as the Data Interface", "https://roundup.getdbt.com/p/semantic-layer-as-the-data-interface", ["semantic layer", "data governance", "metrics", "dbt"]),
    (48, 7, "Data Governance & Strategy", "Are Data Catalogs Curing the Symptom or the Disease?", "https://web.archive.org/web/20210218004246/https://kaminsky.rocks/2020/12/are-data-catalogs-curing-the-symptom-or-the-disease/", ["data catalog", "data governance", "metadata", "data quality"]),
    (49, 7, "Data Governance & Strategy", "The Five Laws of Data Enablement", "https://locallyoptimistic.com/post/the-five-laws-of-data-enablement-how-the-father-of-library-science-would-make-his-data-team-indispensable/", ["data enablement", "data governance", "library science", "data products"]),
    # --- Phase 8: AI ---
    (50, 8, "AI", "Vibe Check: Latest AI Models", "https://every.to/vibe-check/vibe-check-genie-3-claude-4-1-gpt-oss-and-gpt-5", ["AI models", "LLMs", "model evaluation", "AI capabilities"]),
    (51, 8, "AI", "China's AI Plus Policy", "https://www.geopolitechs.org/p/china-releases-ai-plus-policy-a-brief", ["AI policy", "China", "geopolitics", "AI strategy"]),
    (52, 8, "AI", "How O3 and Grok Accidentally Vindicated Symbolic AI", "https://garymarcus.substack.com/p/how-o3-and-grok-4-accidentally-vindicated", ["AI", "symbolic AI", "LLMs", "reasoning", "Gary Marcus"]),
    (53, 8, "AI", "State of AI in Business 2025 Report", "https://mlq.ai/media/quarterly_decks/v0.1_State_of_AI_in_Business_2025_Report.pdf", ["AI", "business AI", "enterprise AI", "2025 trends"]),
    (54, 8, "AI", "What Is ChatGPT Doing and Why Does It Work?", "https://writings.stephenwolfram.com/2023/02/what-is-chatgpt-doing-and-why-does-it-work/", ["ChatGPT", "LLMs", "AI explainability", "Stephen Wolfram"]),
    (55, 8, "AI", "What Is Retrieval Augmented Generation (RAG)?", "https://www.mckinsey.com/featured-insights/mckinsey-explainers/what-is-retrieval-augmented-generation-rag", ["RAG", "retrieval augmented generation", "LLMs", "AI", "knowledge retrieval"]),
    (56, 8, "AI", "Introducing the Model Context Protocol (MCP)", "https://www.anthropic.com/news/model-context-protocol", ["MCP", "model context protocol", "AI agents", "Anthropic", "tool use"]),
    (57, 8, "AI", "Why Language Models Hallucinate", "https://openai.com/index/why-language-models-hallucinate/", ["hallucination", "LLMs", "AI reliability", "OpenAI"]),
    (58, 8, "AI", "On the Biology of Large Language Models", "https://transformer-circuits.pub/2025/attribution-graphs/biology.html", ["LLMs", "mechanistic interpretability", "AI research", "neural networks"]),
    (59, 8, "AI", "Horseless Carriages: How We Think About New Technology", "https://koomen.dev/essays/horseless-carriages/", ["technology adoption", "AI", "mental models", "innovation"]),
    (60, 8, "AI", "Cursor Isn't Just for Coding: How AI-Native PMs Work", "https://maven.com/p/0a96cb/cursor-isn-t-just-for-coding-how-ai-native-pms-work", ["AI tools", "product management", "AI-native", "workflow"]),
    (61, 8, "AI", "GitHub MCP Exploited: Security Implications", "https://simonwillison.net/2025/May/26/github-mcp-exploited/", ["MCP", "AI security", "prompt injection", "GitHub"]),
    (62, 8, "AI", "A New Invisible Hand: AI and Market Dynamics", "https://benn.substack.com/p/a-new-invisible-hand", ["AI", "economics", "market dynamics", "benn.substack"]),
    (63, 8, "AI", "How AI Will Disrupt Data Engineering", "https://roundup.getdbt.com/p/how-ai-will-disrupt-data-engineering", ["AI", "data engineering", "disruption", "dbt", "future of data"]),
    (64, 8, "AI", "How AI Will Disrupt BI as We Know It", "https://roundup.getdbt.com/p/how-ai-will-disrupt-bi-as-we-know", ["AI", "business intelligence", "disruption", "dbt", "analytics"]),
    (65, 8, "AI", "Let's Talk About AI", "https://roundup.getdbt.com/p/lets-talk-about-ai", ["AI", "data teams", "dbt", "practical AI", "LLMs"]),
    # --- Phase 6 continued: Analytics Engineering (in document after AI) ---
    (66, 6, "Building Data Products", "The Analytics Development Lifecycle (ADLC)", "https://www.getdbt.com/resources/the-analytics-development-lifecycle", ["analytics engineering", "ADLC", "dbt", "data workflow", "development lifecycle"]),
    (67, 6, "Building Data Products", "The Analytics Development Lifecycle (PDF)", "https://8698602.fs1.hubspotusercontent-na1.net/hubfs/8698602/The%20Analytics%20Development%20Lifecycle.pdf", ["analytics engineering", "ADLC", "dbt", "data workflow"]),
    (68, 6, "Building Data Products", "How to Review an Analytics Pull Request", "https://www.getdbt.com/blog/how-to-review-an-analytics-pull-request", ["analytics engineering", "code review", "dbt", "data quality", "collaboration"]),
    (69, 6, "Building Data Products", "The Data Quality Flywheel", "https://www.datafold.com/blog/the-data-quality-flywheel", ["data quality", "flywheel", "data testing", "analytics engineering"]),
    (70, 6, "Building Data Products", "Scaling Self-Serve Analytics", "https://www.conordewey.com/blog/scaling-self-serve-analytics/", ["self-serve analytics", "data democratization", "analytics", "data products"]),
    # --- Phase 7 continued: Governance ---
    (71, 7, "Data Governance & Strategy", "Most Data Work Seems Fundamentally Worthless", "https://ludic.mataroa.blog/blog/most-data-work-seems-fundamentally-worthless/", ["data teams", "impact", "data governance", "incentive alignment"]),
    (72, 7, "Data Governance & Strategy", "Whom the Gods Would Destroy, They First Give Real-Time Analytics", "https://mcfunley.com/whom-the-gods-would-destroy-they-first-give-real-time-analytics", ["real-time analytics", "data architecture", "business case", "data governance"]),
    # --- Phase 9: Culture, Teams & Future ---
    (73, 9, "Culture, Teams & Future", "Don't Fuck Up the Culture", "https://medium.com/@bchesky/dont-fuck-up-the-culture-597cde9ee9d4", ["culture", "leadership", "organizational culture", "Brian Chesky", "Airbnb"]),
    (74, 9, "Culture, Teams & Future", "Cost Center to Profit Driver: Repositioning Data Teams", "https://www.getdbt.com/blog/cost-center-profit-driver-data-teams", ["data teams", "data ROI", "organizational strategy", "dbt", "revenue"]),
    (75, 9, "Culture, Teams & Future", "Shopify's Data Science Hierarchy of Needs", "https://shopify.engineering/shopify-unique-data-science-hierarchy-of-needs", ["data science", "hierarchy of needs", "Shopify", "data teams", "value delivery"]),
    (76, 9, "Culture, Teams & Future", "On Vibe Coding and the Future of Software Development", "https://arxiv.org/pdf/2506.00202", ["vibe coding", "AI", "software development", "future of coding"]),
    (77, 9, "Culture, Teams & Future", "Revenge of the Junior Developer", "https://sourcegraph.com/blog/revenge-of-the-junior-developer", ["AI", "junior developers", "software engineering", "future of work"]),
    (78, 9, "Culture, Teams & Future", "The Brute Squad: AI and Engineering Teams", "https://sourcegraph.com/blog/the-brute-squad", ["AI", "software engineering", "developer tools", "future of work"]),
    (79, 9, "Culture, Teams & Future", "Macroeconomics and the Data Industry", "https://roundup.getdbt.com/p/macroeconomics-and-the-data-industry", ["data industry", "economics", "data market", "dbt", "industry trends"]),
    (80, 9, "Culture, Teams & Future", "Corporate Data Wars Intensify", "https://www.theinformation.com/articles/corporate-data-wars-intensify", ["data competition", "corporate strategy", "data as asset", "industry"]),
    (81, 9, "Culture, Teams & Future", "2025 Data Predictions", "https://www.getdbt.com/blog/2025-data-predictions", ["data trends", "predictions", "2025", "data industry", "future of data"]),
    (82, 9, "Culture, Teams & Future", "Which Way From Here? The Future of the Data Industry", "https://benn.substack.com/p/which-way-from-here", ["data industry", "future of data", "benn.substack", "strategy"]),
    (83, 9, "Culture, Teams & Future", "AI Eats the World", "https://static1.squarespace.com/static/50363cf324ac8e905e7df861/t/68348f5da204754d5222cf67/1748275041033/AI+eats+the+world.pdf", ["AI", "future", "technology", "disruption", "AI transformation"]),
    (84, 9, "Culture, Teams & Future", "The AI Report (Bond Cap)", "https://www.bondcap.com/reports/tai", ["AI", "market research", "AI industry", "investment", "trends"]),
    (85, 9, "Culture, Teams & Future", "How Snowflake Fails", "https://benn.substack.com/p/how-snowflake-fails", ["Snowflake", "data warehouse", "cloud data", "benn.substack", "critique"]),
    (86, 9, "Culture, Teams & Future", "How dbt Fails", "https://benn.substack.com/p/how-dbt-fails", ["dbt", "analytics engineering", "benn.substack", "critique"]),
    (87, 9, "Culture, Teams & Future", "TikTok and the Sorting Hat", "https://www.eugenewei.com/blog/2020/8/3/tiktok-and-the-sorting-hat", ["TikTok", "algorithms", "recommendation systems", "social media", "Eugene Wei"]),
    (88, 9, "Culture, Teams & Future", "Seeing Like an Algorithm", "https://www.eugenewei.com/blog/2020/9/18/seeing-like-an-algorithm", ["algorithms", "recommendation systems", "social media", "product thinking", "Eugene Wei"]),
    (89, 9, "Culture, Teams & Future", "American Idle: Why Short Video is So Compelling", "https://www.eugenewei.com/blog/2021/2/15/american-idle", ["short video", "attention economy", "social media", "product thinking", "Eugene Wei"]),
    (90, 9, "Culture, Teams & Future", "Status as a Service", "https://www.eugenewei.com/blog/2019/2/19/status-as-a-service", ["social networks", "status", "network effects", "product thinking", "Eugene Wei"]),
]

PHASE_DIR = {
    0: "phase_0",
    1: "phase_1",
    2: "phase_2",
    3: "phase_3",
    4: "phase_4",
    5: "phase_5",
    6: "phase_6",
    7: "phase_7",
    8: "phase_8",
    9: "phase_9",
}

STUB_TEMPLATE = """---
article_number: {article_number}
title: "{title}"
source_url: "{source_url}"
phase: {phase}
phase_name: "{phase_name}"
themes: {themes}
date_captured: "2026-03-06"
---

## Summary


## Key Excerpts


## Annotations

"""

def main():
    created = 0
    for (num, phase, phase_name, title, url, themes) in ARTICLES:
        phase_dir = BASE / PHASE_DIR[phase]
        phase_dir.mkdir(parents=True, exist_ok=True)

        slug = title.lower()
        slug = slug.replace("'", "").replace(",", "").replace("?", "").replace(":", "").replace("/", "-").replace("(", "").replace(")", "")
        slug = " ".join(slug.split())
        slug = slug.replace(" ", "_")[:50].rstrip("_")

        filename = "{:03d}_{}.md".format(num, slug)
        filepath = phase_dir / filename

        themes_yaml = "[" + ", ".join('"{}"'.format(t) for t in themes) + "]"
        content = STUB_TEMPLATE.format(
            article_number=num,
            title=title.replace('"', '\\"'),
            source_url=url,
            phase=phase,
            phase_name=phase_name,
            themes=themes_yaml,
        )

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)

        print("Created: {}".format(filepath.relative_to(BASE.parent.parent)))
        created += 1

    print("\nDone. Created {} stubs.".format(created))

if __name__ == "__main__":
    main()
