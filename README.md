# LATAM Bank Service

A bilingual (🇪🇸 Spanish / 🇧🇷 Portuguese) **banking customer-service system** — not a chatbot. It understands the customer, uses the right tools, verifies that actions happened, knows when *not* to act, and hands off to a human with a structured summary.

> Status: **scaffolding.** Dataset and final challenge instructions are pending. See [docs/meeting-notes.md](docs/meeting-notes.md) for requirements and [docs/decisions.md](docs/decisions.md) for open decisions.

**Live:** https://latam-bank-service.vercel.app (auto-deploys from `main`)

## Stack (provisional)
| Layer | Choice |
|---|---|
| App / API | Next.js (App Router, TypeScript) on Vercel |
| Data | Supabase Postgres — region `sa-east-1` (São Paulo) |
| LLM | TBD |

Recommended platforms (Snowflake / AWS / Azure / Databricks) to be evaluated later — see D-001.

## Repo layout
```
src/            Next.js app + API routes
src/lib/        shared clients (supabase, ...)
supabase/       SQL migrations (source of truth for schema + RLS)
data/raw/       raw inputs — git-ignored, never commit customer data
data/processed/ reproducible outputs of the prep pipeline
evals/          baseline vs. system evaluation (strict train/eval isolation)
docs/           meeting notes, decisions, honest "what's missing"
```

## Getting started
```bash
npm install
cp .env.example .env.local   # fill in server-only secrets
npm run dev
```

## What's missing (keep this honest)
- [ ] Dataset + final instructions
- [ ] Use case choice (D-002)
- [ ] Baseline, system, evaluation harness
- [ ] Observability, security (prompt-injection defenses, RLS), structured human handoff
