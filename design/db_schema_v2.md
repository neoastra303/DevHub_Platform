# Database Schema — Current State (v2)

This document describes the current database schema and the evolution from v1.

---

## Current Schema (14 tables)

```
User (AbstractUser)
├── Profile (OneToOne)
│   ├── SkillProficiency (M2M through)
│   └── Skill (M2M through SkillProficiency)
├── Project (FK: owner)
│   └── Technology (M2M)
├── Post (FK: author)
│   ├── PostMetric (OneToOne)
│   ├── PostLike (FK: user + post, unique constraint)
│   ├── ViewEvent (FK: post)
│   └── Comment (FK: post)
├── TransactionLog (FK: user)
├── AuditLog (FK: actor, GenericForeignKey to any model)
├── BackgroundJob (FK: requested_by)
└── Notification (FK: recipient)
```

### Model Details

| Model | Fields | Indexes |
| :--- | :--- | :--- |
| `User` | username, email (unique), password, first_name, last_name | PK on id, unique on username/email |
| `Profile` | user (O2O), headline, bio, avatar_seed, reputation, points, active_projects, skills (M2M), timestamps | PK on id, FK on user_id |
| `Skill` | name (unique), slug (unique, db_index) | PK, unique name, unique slug |
| `SkillProficiency` | profile (FK), skill (FK), level (1-5) | PK, unique_together(profile, skill) |
| `Technology` | name (unique), slug (unique, db_index) | PK, unique name, unique slug |
| `Project` | owner (FK), title, slug (unique, db_index), summary, description, technologies (M2M), demo_url, source_url, is_featured (db_index), timestamps | PK, FK on owner_id, unique slug |
| `Post` | author (FK), title, content, timestamps | PK, FK on author_id |
| `PostMetric` | post (O2O), views, likes | PK, FK on post_id |
| `PostLike` | user (FK), post (FK), created_at | PK, unique_constraint(user, post) |
| `ViewEvent` | post (FK), user (FK nullable), created_at | PK, FK on post_id |
| `TransactionLog` | user (FK), transaction_id (unique), amount, status, timestamps | PK, FK on user_id, unique transaction_id |
| `AuditLog` | actor (FK nullable), action (db_index), content_type (FK), object_id, metadata (JSON), timestamps | PK, FK on actor_id, FK on content_type_id |
| `BackgroundJob` | requested_by (FK), job_type (db_index), status (db_index), payload (JSON), result (JSON), error_message, timestamps | PK, FK on requested_by_id |
| `Comment` | author (FK), post (FK nullable), project (FK nullable), content, timestamps | PK, FK on author/post/project_id |
| `Notification` | recipient (FK), title, message, is_read, link, timestamps | PK, FK on recipient_id |

### Key Decisions

- **GenericForeignKey for AuditLog:** Enables querying audit events across any model without polymorphic tables or multiple FK columns
- **PostMetric as separate table:** Decouples frequently-written metrics from the Post row, reducing lock contention
- **Status state machines:** `TransactionLog.Status` (pending → completed/failed) and `BackgroundJob.Status` (queued → running → succeeded/failed) are `TextField` with `TextChoices` for readability
- **db_index on `action`, `status`, `job_type`:** These are frequently filtered in audit and job list views

---

## Migration History

### v1 → v2 (Completed)

| Change | Reason |
| :--- | :--- |
| Extract `views`/`likes_count` from `Post` → `PostMetric` | Decouple metrics, improve write performance |
| Add `ViewEvent` model | Record every view for accurate analytics |
| Add `SkillProficiency` through table | Track expertise levels (1-5) |
| Refactor `AuditLog` to `GenericForeignKey` | Integrity, better query support |
| Add `db_index` to slug, action, status, job_type fields | Query performance at scale |

### Proposed for v3

| Model | Change | Purpose |
| :--- | :--- | :--- |
| `Profile` | Add `follows` M2M | Social features |
| `Post` | Add `tags` M2M | Content categorization |
| `BackgroundJob` | Add `retry_count`, `scheduled_at` | Advanced job scheduling |
