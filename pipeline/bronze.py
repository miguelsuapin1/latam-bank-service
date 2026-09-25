"""Bronze layer: load raw organizer CSVs into DuckDB verbatim (all VARCHAR) plus lineage columns.

No cleaning happens here. Every row keeps its source file and load timestamp so that
silver-layer decisions can be traced back to raw input.
"""
import duckdb
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RAW = ROOT / "data" / "raw"
DB = ROOT / "data" / "processed" / "bronze.duckdb"

PARTITIONED = [
    "transactions", "call_center_interactions", "call_transcripts",
    "satisfaction_surveys", "complaints", "campaign_sends",
]
SNAPSHOTS = [
    "customers", "products", "branches", "service_agents",
    "marketing_campaigns", "daily_exchange_rates",
]


def build() -> None:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB))
    for t in PARTITIONED:
        src = RAW / t / "**" / "*.csv"
        con.execute(f"""
            create or replace table {t} as
            select *, now() as _loaded_at
            from read_csv('{src}', union_by_name=true, filename=true,
                          hive_partitioning=true, all_varchar=true)
        """)
    for t in SNAPSHOTS:
        con.execute(f"""
            create or replace table {t} as
            select *, now() as _loaded_at
            from read_csv('{RAW / (t + ".csv")}', filename=true, all_varchar=true)
        """)
    for t in PARTITIONED + SNAPSHOTS:
        n = con.execute(f"select count(*) from {t}").fetchone()[0]
        print(f"{t:28s} {n:>10,}")
    con.close()


if __name__ == "__main__":
    build()
