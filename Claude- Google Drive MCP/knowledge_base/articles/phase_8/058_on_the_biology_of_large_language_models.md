---
article_number: 58
title: "On the Biology of Large Language Models"
source_url: "https://transformer-circuits.pub/2025/attribution-graphs/biology.html"
phase: 8
phase_name: "AI"
themes: ["LLMs", "mechanistic interpretability", "AI research", "neural networks"]
date_captured: "2026-03-06"
---

## Summary
This paper presents mechanistic interpretability research on Claude 3.5 Haiku, using "attribution graphs" to reverse-engineer how the model performs multi-step reasoning, planning, hallucination, refusal, and jailbreak behavior at the circuit level. For data leaders, this work matters because it moves AI audibility from black-box behavioral testing toward verifiable internal explanations—directly relevant to AI governance, risk assessment, and defensible deployment decisions.

## Key Excerpts
> Researchers can trace and manipulate intermediate reasoning steps inside the model, revealing that it constructs internal representations (e.g., "Texas") before producing outputs, making reasoning partially auditable.
> Hallucinations were linked to specific circuit misfires in entity recognition, offering a mechanistic—not just statistical—explanation for a major AI reliability risk.
> The model's refusal behavior relies on a generalized "harmful request" feature assembled during fine-tuning, suggesting safety alignment has identifiable, inspectable internal structure that could be monitored or tested.

## Annotations
