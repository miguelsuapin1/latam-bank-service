@AGENTS.md

# Project context
Hackathon: bilingual (ES/PT) LATAM banking customer-service system. Requirements: docs/meeting-notes.md. Decisions: docs/decisions.md.
- Supabase project `paguvqqelfwadcolocaq` (org "hackathon", sa-east-1). Schema changes go in supabase/migrations/.
- Vercel team `miguelsuapin-1909s-projects`, project `latam-bank-service`.
- Never commit customer data (data/raw is git-ignored) or secrets (.env* ignored except .env.example).
