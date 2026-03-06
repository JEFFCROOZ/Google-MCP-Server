---
article_number: 39
title: "A Brief History of Block Storage at AWS"
source_url: "https://www.allthingsdistributed.com/2024/08/continuous-reinvention-a-brief-history-of-block-storage-at-aws.html"
phase: 5
phase_name: "Engineering Thinking"
themes: ["AWS", "cloud storage", "engineering history", "first principles", "infrastructure"]
date_captured: "2026-03-06"
---

## Summary
This article chronicles EBS's evolution from shared HDDs to a distributed SSD fleet delivering 140 trillion daily operations, emphasizing how incremental iteration, first-principles thinking, and performance constraints drove architectural reinvention. For data leaders, it illustrates how foundational infrastructure decisions—particularly around performance, availability, and durability trade-offs—cascade directly into application reliability and the ability to scale data workloads at enterprise levels.

## Key Excerpts
> EBS now delivers more IOPS to a single EC2 instance than it could provide to an entire Availability Zone in its early HDD-based years.
> Unlike many storage systems that prioritize durability over performance, EBS treats availability and throughput as equally critical because storage performance directly shapes the end-user compute experience.
> Successive incremental iteration and distilling problems to first principles—not big-bang rewrites—were the primary mechanisms behind EBS's dramatic performance improvements over more than a decade.

## Annotations
