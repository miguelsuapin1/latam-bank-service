"""Contact-reason analysis (challenge requirement #1: a problem supported by data).

Writes reports/contact_reasons.md from data/processed/bronze.duckdb. Numbers quoted in
docs/contact-reason-analysis.md come from this report.
"""
from datetime import datetime, timezone
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "data" / "processed" / "bronze.duckdb"
OUT = ROOT / "reports" / "contact_reasons.md"

QUERIES = {
    "Contact reasons: volume and service outcomes (call_center_interactions + CSAT)": """
        with i as (select *, duration_seconds::double dur, wait_time_seconds::double wt
                   from call_center_interactions),
        sv as (select interaction_id, avg(main_score::double) filter (where survey_type='CSAT') csat,
                      count(*) filter (where survey_type='CSAT') n_csat
               from satisfaction_surveys group by 1)
        select reason_category as reason, count(*) as contacts,
               round(100*count(*)/sum(count(*)) over (), 1) as share_pct,
               round(100*avg((was_resolved='True')::int), 1) as fcr_pct,
               round(100*avg((requires_followup='True')::int), 1) as followup_pct,
               round(100*avg((was_escalated='True')::int), 1) as escalated_pct,
               round(median(dur)/60, 1) as median_aht_min,
               round(sum(dur)/3600) as agent_hours,
               round(100*sum(dur)/sum(sum(dur)) over (), 1) as agent_hours_pct,
               round(100*avg((detected_sentiment in ('Negativo','Muy Negativo'))::int), 1) as negative_pct,
               round(avg(csat), 2) as csat_avg, sum(n_csat) as csat_n
        from i left join sv using (interaction_id)
        group by 1 order by contacts desc""",
    "Contact reasons by channel (share of each reason)": """
        select reason_category as reason, channel, count(*) as contacts,
               round(100*count(*)/sum(count(*)) over (partition by reason_category), 1) as pct_of_reason
        from call_center_interactions group by 1, 2 order by reason, contacts desc""",
    "Complaints (PQR) by category and subcategory": """
        select category, coalesce(subcategory, '(missing)') as subcategory, count(*) as cases,
               round(100*count(*)/sum(count(*)) over (), 1) as share_pct,
               round(100*avg((sla_breached='True')::int), 1) as sla_breach_pct,
               round(median(resolution_days::double), 1) as median_resolution_days,
               round(100*avg((status in ('Open','In Process','Escalated'))::int), 1) as still_open_pct,
               round(100*avg((claimed_amount is not null)::int), 1) as has_claimed_amount_pct,
               round(100*avg((reception_channel='Regulator')::int), 2) as via_regulator_pct
        from complaints group by 1, 2 order by cases desc""",
    "Complaints by case type": """
        select case_type, count(*) as cases, round(100*count(*)/sum(count(*)) over (), 1) as share_pct
        from complaints group by 1 order by cases desc""",
    "Transactions by status (context for payment inquiries and disputes)": """
        select transaction_status, count(*) as transactions,
               round(100*count(*)/sum(count(*)) over (), 2) as share_pct,
               round(100*avg((is_fraud='True')::int), 3) as fraud_pct
        from transactions group by 1 order by transactions desc""",
    "Products held (what customers can ask about)": """
        select product_type, product_status, count(*) as products
        from products group by 1, 2 order by product_type, products desc""",
    "Demand by weekday": """
        select dayname(interaction_date::timestamp) as weekday, count(*) as contacts,
               round(100*count(*)/sum(count(*)) over (), 1) as share_pct
        from call_center_interactions group by 1 order by contacts desc""",
    "Demand by month": """
        select strftime(interaction_date::timestamp, '%Y-%m') as month, count(*) as contacts
        from call_center_interactions group by 1 order by 1""",
    "Outcomes by country (fairness baseline)": """
        select c.country, count(*) as contacts, round(100*avg((was_resolved='True')::int), 1) as fcr_pct,
               round(100*avg((was_escalated='True')::int), 1) as escalated_pct,
               round(avg(sentiment_score::double), 3) as avg_sentiment
        from call_center_interactions i join customers c using (customer_id) group by 1 order by contacts desc""",
    "Outcomes by customer segment (fairness baseline)": """
        select c.segment, count(*) as contacts, round(100*avg((was_resolved='True')::int), 1) as fcr_pct,
               round(100*avg((was_escalated='True')::int), 1) as escalated_pct,
               round(avg(sentiment_score::double), 3) as avg_sentiment
        from call_center_interactions i join customers c using (customer_id) group by 1 order by contacts desc""",
}


def main():
    con = duckdb.connect(str(DB), read_only=True)
    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w") as f:
        f.write("# Contact-reason analysis\n\n")
        f.write(f"_Generated by `analysis/contact_reasons.py` on {datetime.now(timezone.utc):%Y-%m-%d %H:%M} UTC. "
                "Raw (bronze) data, before cleaning. Do not edit by hand._\n\n")
        for title, q in QUERIES.items():
            f.write(f"## {title}\n\n{con.sql(q).df().to_markdown(index=False)}\n\n")
    print(f"wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
