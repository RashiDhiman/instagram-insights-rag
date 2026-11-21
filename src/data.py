import json, re, sqlite3
from pathlib import Path
import pandas as pd
from src.config import DATA_DIR, STORAGE_DIR, DB_PATH

FILES = {"reels": "reels_dataset.csv", "stories": "stories_dataset.csv", "posts": "posts_dataset.csv"}
METRIC_COLUMNS = {
    "accounts_reached": ["Accounts reached_num", "Accounts reached"],
    "plays": ["Instagram plays_num", "Instagram plays"],
    "likes": ["Instagram likes_num", "Instagram likes"],
    "comments": ["Instagram comments_num", "Instagram comments"],
    "shares": ["Instagram shares_num", "Instagram shares", "Shares_num", "Shares"],
    "saves": ["Instagram saves_num", "Instagram saves"],
    "impressions": ["Impressions_num", "Impressions"],
    "profile_visits": ["Profile visits_num", "Profile visits"],
    "replies": ["Replies_num", "Replies"],
    "reactions": ["Reactions_num", "Reactions"],
    "external_link_taps": ["External link taps_num", "External link taps"],
    "follows": ["Follows_num", "Follows"],
}

def clean_text(value):
    if value is None or pd.isna(value):
        return ""
    return re.sub(r"\s+", " ", str(value)).strip()

def number_from(row, candidates):
    for key in candidates:
        if key in row:
            value = row.get(key)
            if value is not None and not pd.isna(value):
                try:
                    return float(str(value).replace(",", "").replace("%", "").strip())
                except (ValueError, TypeError):
                    pass
    return None

def load_records():
    records = []
    for kind, filename in FILES.items():
        path = DATA_DIR / filename
        if not path.exists():
            continue
        df = pd.read_csv(path)
        for _, series in df.iterrows():
            row = series.to_dict()
            rid = clean_text(row.get("record_id")) or str(len(records) + 1)
            caption = clean_text(row.get("Caption") or row.get("Media thumbnail"))
            # Use raw_text as a fallback, but avoid embedding raw metric boilerplate where a caption exists.
            raw_text = clean_text(row.get("raw_text"))
            content = caption or raw_text
            published = clean_text(row.get("published_at") or row.get("Upload timestamp") or row.get("Creation timestamp") or row.get("Creation time") or row.get("Update time"))
            metrics = {name: number_from(row, cols) for name, cols in METRIC_COLUMNS.items()}
            metrics = {k: v for k, v in metrics.items() if v is not None}
            semantic_parts = [f"Content type: {kind[:-1] if kind.endswith('s') else kind}"]
            if published:
                semantic_parts.append(f"Published: {published}")
            if content:
                semantic_parts.append(f"Content: {content}")
            if kind == "posts":
                for field in ["Publish mode", "Paid partnership", "Is an advertisement"]:
                    val = clean_text(row.get(field))
                    if val:
                        semantic_parts.append(f"{field}: {val}")
            # Stable source IDs preserve provenance. Export row IDs are not assumed globally unique.
            record_id = f"{kind}_{rid}"
            records.append({
                "id": record_id, "kind": kind, "record_id": str(rid),
                "published_at": published, "caption": content,
                "semantic_text": "\n".join(semantic_parts),
                "metrics": metrics, "raw": {str(k): (None if pd.isna(v) else v) for k, v in row.items()}
            })
    return records

def build_sqlite(records):
    STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""CREATE TABLE IF NOT EXISTS records (
            id TEXT PRIMARY KEY, kind TEXT NOT NULL, record_id TEXT,
            published_at TEXT, caption TEXT, semantic_text TEXT,
            metrics_json TEXT NOT NULL, raw_json TEXT NOT NULL
        )""")
        conn.execute("DELETE FROM records")
        rows = [(r["id"], r["kind"], r["record_id"], r["published_at"], r["caption"],
                 r["semantic_text"], json.dumps(r["metrics"]), json.dumps(r["raw"], default=str)) for r in records]
        conn.executemany("INSERT INTO records VALUES (?, ?, ?, ?, ?, ?, ?, ?)", rows)
        conn.commit()
    return len(records)
