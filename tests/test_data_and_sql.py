import sqlite3
from src.data import load_records, build_sqlite
from src.config import DB_PATH
from src.query import structured_answer

def setup_module():
    records = load_records()
    assert len(records) == 238
    build_sqlite(records)

def test_record_counts():
    with sqlite3.connect(DB_PATH) as conn:
        counts = dict(conn.execute("SELECT kind, COUNT(*) FROM records GROUP BY kind").fetchall())
    assert counts == {"posts": 139, "reels": 43, "stories": 56}

def test_highest_reel_reach():
    answer = structured_answer("Which reel had the highest reach?")
    assert "reels_26" in answer
    assert "179,945" in answer

def test_average_reel_reach():
    answer = structured_answer("What is the average reach across reels?")
    assert "24,292.09" in answer

def test_story_count():
    answer = structured_answer("How many stories are indexed?")
    assert "56 stories" in answer
