# Database Schema v2 Design

This document outlines the proposed changes to the DevHub Platform database architecture to enhance analytics, scalability, and social interactivity.

## Proposed Changes

| Model | Changes | Purpose |
| :--- | :--- | :--- |
| **`Post`** | Remove `views`, `likes_count` | Decouple metrics, improve write performance. |
| **`ViewEvent`** | **NEW** (FK to Post, User) | Record every view for accurate analytics. |
| **`PostMetric`** | **NEW** (FK to Post, aggregated) | Fast lookup for dashboard charts. |
| **`Profile`** | Add `follows` M2M | Social features. |
| **`SkillProficiency`**| **NEW** (Through table) | Track expertise levels (1-5). |
| **`AuditLog`** | Refactor to `GenericForeignKey`| Integrity, better queries. |

## Migration Strategy

1.  **Drafting:** Ensure all new models are defined.
2.  **Data Migration:** 
    - Create a data migration to move current `likes_count` and `views` from `Post` into new `PostMetric` entries.
    - Migrate existing `AuditLog` records to the new `GenericForeignKey` structure.
3.  **Application:** Apply schema changes.
4.  **Refactoring:** Update `services.py` and views to use the new `ViewEvent` and `PostMetric` models instead of direct writes to `Post`.
