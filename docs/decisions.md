# Decision log

## D-001 — Start on Supabase + Vercel (2026-09-25)
**Status:** accepted (provisional)
**Context:** Organizers recommend Snowflake / AWS / Azure / Databricks; we don't have accounts yet and data + exact instructions are pending.
**Decision:** Next.js on Vercel for the service/UI, Supabase (Postgres, sa-east-1 São Paulo) for data, RLS-based customer-record isolation, and migrations.
**Revisit when:** we have access to a recommended platform. Evaluate: managed ETL/lineage (Databricks/Snowflake), eval tooling, judging bonus for using a recommended platform, migration cost.

## D-002 — Use case
**Status:** open — choose one of: account/payment inquiries, card support, transaction disputes, credit-product eligibility. Decide once the dataset arrives.
