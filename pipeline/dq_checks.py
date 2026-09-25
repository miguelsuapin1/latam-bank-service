"""Measure raw data against the organizer contracts and write reports/data_quality.md.

Run after `pipeline/bronze.py`. Every number in docs/data-issues.md comes from this report
or from analysis/contact_reasons.py, so findings are reproducible from data/raw.
"""
from datetime import datetime, timezone
from pathlib import Path

import duckdb
import pandas as pd

from contracts import DOMAINS, EXPECTED_ROWS, FOREIGN_KEYS, NOT_NULL, PRIMARY_KEYS

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "processed" / "bronze.duckdb"
OUT = ROOT / "reports" / "data_quality.md"
META = {"filename", "_loaded_at", "year", "month", "day"}


def columns(con, t):
    return [c for c, *_ in con.execute(f"describe {t}").fetchall() if c not in META]


def row_counts(con):
    rows = []
    for t, exp in EXPECTED_ROWS.items():
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        rows.append({"table": t, "expected": exp, "observed": n, "diff_pct": round(100 * (n - exp) / exp, 1)})
    return pd.DataFrame(rows)


def duplicates(con):
    rows = []
    for t in EXPECTED_ROWS:
        cols = columns(con, t)
        pk = PRIMARY_KEYS.get(t)
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        exact = n - con.execute(f"select count(*) from (select distinct {','.join(cols)} from {t})").fetchone()[0]
        content = [c for c in cols if c not in (pk, "process_date", "last_updated")]
        near = n - con.execute(f"select count(*) from (select distinct {','.join(content)} from {t})").fetchone()[0]
        dup_pk = n - con.execute(f"select count(distinct {pk}) from {t}").fetchone()[0] if pk else None
        rows.append({"table": t, "rows": n, "exact_dup": exact, "dup_pk": dup_pk, "same_content_new_id": near})
    return pd.DataFrame(rows)


def nulls(con):
    rows = []
    for t in EXPECTED_ROWS:
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        cols = columns(con, t)
        counts = con.execute("select " + ",".join(f"count(*)-count(nullif(trim({c}),''))" for c in cols) + f" from {t}").fetchone()
        for c, v in zip(cols, counts):
            if v:
                rows.append({"table": t, "column": c, "nulls": v, "pct": round(100 * v / n, 1),
                             "violates_not_null": c in NOT_NULL.get(t, [])})
    return pd.DataFrame(rows).sort_values(["violates_not_null", "pct"], ascending=False)


def domains(con):
    rows = []
    for (t, c), allowed in DOMAINS.items():
        for val, n in con.execute(f"select {c}, count(*) from {t} where {c} is not null group by 1 order by 2 desc").fetchall():
            if val not in allowed:
                rows.append({"table": t, "column": c, "value": val, "rows": n, "documented": ", ".join(allowed)})
    return pd.DataFrame(rows)


def foreign_keys(con):
    rows = []
    for t, c, rt, rc in FOREIGN_KEYS:
        n, orphans = con.execute(
            f"select count({c}), count({c}) filter (where {c} not in (select {rc} from {rt})) from {t}").fetchone()
        rows.append({"fk": f"{t}.{c} → {rt}", "non_null": n, "orphans": orphans,
                     "orphan_pct": round(100 * orphans / n, 2) if n else None})
    return pd.DataFrame(rows)


def consistency(con):
    checks = {
        "complaint.affected_product owned by another customer":
            "select count(*) from complaints c join products p on c.affected_product_id=p.product_id where c.customer_id<>p.customer_id",
        "complaints Resolved/Closed without resolution_date":
            "select count(*) from complaints where status in ('Resolved','Closed') and resolution_date is null",
        "complaints compensation_granted > claimed_amount":
            "select count(*) from complaints where compensation_granted::double > claimed_amount::double",
        "complaints currency set but claimed_amount null":
            "select count(*) from complaints where currency is not null and claimed_amount is null",
        "transactions of Mexican customers in MXN":
            "select count(*) from transactions t join customers c using(customer_id) where c.country='México' and t.currency='MXN'",
        "transactions of Mexican customers in USD":
            "select count(*) from transactions t join customers c using(customer_id) where c.country='México' and t.currency='USD'",
        "transactions non-USD with amount_usd null":
            "select count(*) from transactions where currency<>'USD' and amount_usd is null",
        "transactions non-Approved with null response_code":
            "select count(*) from transactions where transaction_status<>'Approved' and response_code is null",
        "transaction_country spelled 'Mexico' (vs 'México')":
            "select count(*) from transactions where transaction_country='Mexico'",
        "Mexican customers with document_type DNI (dictionary: CURP)":
            "select count(*) from customers where country='México' and document_type='DNI'",
        "NPS surveys with score 9-10 (Promoters)":
            "select count(*) from satisfaction_surveys where survey_type='NPS' and main_score::int>=9",
        "NPS surveys with null nps_category":
            "select count(*) from satisfaction_surveys where survey_type='NPS' and nps_category is null",
        "CSAT surveys with score 5":
            "select count(*) from satisfaction_surveys where survey_type='CSAT' and main_score::int=5",
        "interactions timestamped the day after process_date (08:00 UTC cutoff)":
            "select count(*) from call_center_interactions where interaction_date::date > process_date::date",
        "interactions logged > 0 days after event (true late arrivals)":
            "select count(*) from call_center_interactions where interaction_date::date < process_date::date",
        "distinct call_transcripts.customer_text":
            "select count(distinct customer_text) from call_transcripts",
        "distinct call_transcripts.detected_intents":
            "select count(distinct detected_intents) from call_transcripts",
        "distinct complaints.description":
            "select count(distinct description) from complaints",
        "distinct satisfaction_surveys.open_comments":
            "select count(distinct open_comments) from satisfaction_surveys",
        "interactions where contact_reason <> reason_category":
            "select count(*) from call_center_interactions where contact_reason<>reason_category",
    }
    return pd.DataFrame([{"check": k, "rows": con.execute(q).fetchone()[0]} for k, q in checks.items()])


def main():
    con = duckdb.connect(str(DB), read_only=True)
    sections = [
        ("Row counts vs dictionary", row_counts(con)),
        ("Duplicates", duplicates(con)),
        ("Null / blank values", nulls(con)),
        ("Values outside documented domains", domains(con)),
        ("Referential integrity", foreign_keys(con)),
        ("Consistency checks", consistency(con)),
    ]
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Raw data quality report\n\n")
        f.write(f"_Generated by `pipeline/dq_checks.py` on {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC "
                "from `data/processed/bronze.duckdb`. Do not edit by hand._\n\n")
        for title, df in sections:
            f.write(f"## {title}\n\n{df.to_markdown(index=False)}\n\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
