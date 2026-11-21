import sqlite3, json
from collections import Counter
from src.data import load_records, build_sqlite
from src.config import DB_PATH

def main():
    records = load_records()
    counts = Counter(r["kind"] for r in records)
    print("DATASET AUDIT")
    print("Total records:", len(records))
    for kind, count in sorted(counts.items()):
        subset = [r for r in records if r["kind"] == kind]
        with_text = sum(bool(r["caption"]) for r in subset)
        print(f"- {kind}: {count} records; {with_text} with usable text")
    ids = [r["id"] for r in records]
    print("Duplicate IDs:", len(ids) - len(set(ids)))
    print("Records with dates:", sum(bool(r["published_at"]) for r in records))
    print("Records with metrics:", sum(bool(r["metrics"]) for r in records))
    build_sqlite(records)
    with sqlite3.connect(DB_PATH) as conn:
        print("SQLite rows:", conn.execute("SELECT COUNT(*) FROM records").fetchone()[0])
        print("Kinds:", conn.execute("SELECT kind, COUNT(*) FROM records GROUP BY kind").fetchall())
        print("Reel reach coverage:", conn.execute("SELECT COUNT(*) FROM records WHERE kind='reels' AND json_extract(metrics_json,'$.accounts_reached') IS NOT NULL").fetchone()[0])
if __name__ == "__main__":
    main()
