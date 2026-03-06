---
article_number: 37
title: "Towards an Understanding of Technical Debt"
source_url: "https://kellanem.com/notes/towards-an-understanding-of-technical-debt"
phase: 5
phase_name: "Engineering Thinking"
themes: ["technical debt", "engineering", "software quality", "refactoring"]
date_captured: "2026-03-06"
---

## Summary
The article argues that "technical debt" is a dangerously overloaded term that conflates at least five distinct phenomena—maintenance work, change-resistant code, operability failures, demoralizing code, and dependency friction—each requiring different remediation strategies. For data leaders, this distinction matters because misdiagnosing the root cause of engineering slowdowns leads to misdirected investment: refactoring sprints won't fix operability dysfunction, and "cleaning up messy code" won't address the fundamental reality that all code eventually becomes a liability as problem definitions evolve.

## Key Excerpts
> True technical debt—intentional shortcuts made knowingly—is relatively rare; most of what teams label as debt are categorically different problems requiring different solutions.
> Code is inherently a liability over time because it encodes a fixed solution to a problem that will inevitably change, making disposability an undervalued design goal.
> Poor operability—flaky tests, required coordination for releases, lack of metrics—suppresses change velocity just as much as poorly written code, yet is rarely treated as debt.

## Annotations
