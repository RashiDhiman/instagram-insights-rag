
import re
import sqlite3
import sys

from src.config import DB_PATH
from src.answer import generate_answer
def structured_answer(question):
    q = question.lower()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row

        kind = (
            "reels" if re.search(r"\breel(s)?\b", q)
            else "stories" if re.search(r"\bstor(y|ies)\b", q)
            else "posts" if re.search(r"\bposts?\b", q)
            else None
        )

        # Detect requests for the top N records.
        number_words = {
            "one": 1, "two": 2, "three": 3, "four": 4,
            "five": 5, "six": 6, "seven": 7, "eight": 8,
            "nine": 9, "ten": 10
        }

        top_match = re.search(
            r"\b(?:top|highest|best|greatest)\s+"
            r"(one|two|three|four|five|six|seven|eight|nine|ten|\d+)",
            q
        )

        # Also recognise phrases such as "five highest-reach reels".
        if not top_match:
            top_match = re.search(
                r"\b(one|two|three|four|five|six|seven|eight|nine|ten|\d+)"
                r"\s+(?:highest|top|best|greatest)(?:[- ]\w+)*",
                q
            )

        if top_match and any(
            word in q for word in ["reach", "plays", "likes", "saves", "comments", "shares"]
        ):
            raw_n = top_match.group(1)
            limit = number_words.get(raw_n, int(raw_n) if raw_n.isdigit() else 5)

            metric_name = next(
                x for x in ["reach", "plays", "likes", "saves", "comments", "shares"]
                if x in q
            )

            metric_key = {
                "reach": "accounts_reached",
                "plays": "plays",
                "likes": "likes",
                "saves": "saves",
                "comments": "comments",
                "shares": "shares"
            }[metric_name]

            sql = f"""
                SELECT id, kind, published_at, caption,
                       CAST(json_extract(metrics_json, '$.{metric_key}') AS REAL) AS metric
                FROM records
                WHERE json_extract(metrics_json, '$.{metric_key}') IS NOT NULL
            """

            params = []

            if kind:
                sql += " AND kind=?"
                params.append(kind)

            sql += " ORDER BY metric DESC LIMIT ?"
            params.append(limit)

            rows = conn.execute(sql, params).fetchall()

            if rows:
                output = [
                    f"Top {len(rows)} {kind or 'records'} by {metric_name}:"
                ]

                for i, row in enumerate(rows, 1):
                    output.append(
                        f"{i}. {row['id']} | "
                        f"{metric_name}={row['metric']:,.0f} | "
                        f"date={row['published_at']} | "
                        f"caption={row['caption']}"
                    )

                if "average" in q:
                    avg = sum(row["metric"] for row in rows) / len(rows)
                    output.append(
                        f"\nAverage {metric_name} across these "
                        f"{len(rows)} records: {avg:,.2f}"
                    )

                return "\n".join(output)

        # Single highest-reach request.
        if any(x in q for x in [
            "highest reach", "highest-reach", "most reach",
            "maximum reach", "top reach", "greatest reach"
        ]):
            sql = """
                SELECT id, kind, published_at, caption,
                       CAST(json_extract(metrics_json, '$.accounts_reached') AS REAL) AS metric
                FROM records
                WHERE json_extract(metrics_json, '$.accounts_reached') IS NOT NULL
            """

            params = []

            if kind:
                sql += " AND kind=?"
                params.append(kind)

            row = conn.execute(
                sql + " ORDER BY metric DESC LIMIT 1", params
            ).fetchone()

            if row:
                return (
                    f"Highest reach: {row['id']} | "
                    f"reach={row['metric']:,.0f} | "
                    f"date={row['published_at']} | "
                    f"caption={row['caption']}"
                )

        # Average across all records.
        if "average" in q and any(
            x in q for x in ["reach", "plays", "likes", "saves", "comments", "shares"]
        ):
            metric = next(
                x for x in ["reach", "plays", "likes", "saves", "comments", "shares"]
                if x in q
            )

            key = {
                "reach": "accounts_reached",
                "plays": "plays",
                "likes": "likes",
                "saves": "saves",
                "comments": "comments",
                "shares": "shares"
            }[metric]

            sql = f"""
                SELECT AVG(CAST(json_extract(metrics_json, '$.{key}') AS REAL))
                FROM records
                WHERE json_extract(metrics_json, '$.{key}') IS NOT NULL
            """

            params = []

            if kind:
                sql += " AND kind=?"
                params.append(kind)

            value = conn.execute(sql, params).fetchone()[0]

            if value is not None:
                return (
                    f"Average {metric}{' for ' + kind if kind else ''}: "
                    f"{value:,.2f} across records with that metric."
                )

        if any(x in q for x in ["how many", "count", "number of"]):
            if kind:
                n = conn.execute(
                    "SELECT COUNT(*) FROM records WHERE kind=?", (kind,)
                ).fetchone()[0]

                note = (
                    " Post export entries are not guaranteed to represent "
                    "unique published posts."
                    if kind == "posts" else ""
                )

                return f"Indexed {n} {kind} records.{note}"

    return None
    return None


def ask(question, top_k=5):
    exact = structured_answer(question)

    if exact:
        return exact, []

    from src.retriever import Retriever

    hits = Retriever().search(question, top_k=top_k)
    return generate_answer(question, hits), hits


def main():
    if len(sys.argv) < 2:
        raise SystemExit('Usage: python -m src.query "your question"')

    answer, hits = ask(" ".join(sys.argv[1:]))

    print(answer)

    if hits:
        print("\nRetrieved source IDs:", ", ".join(h["id"] for h in hits))


if __name__ == "__main__":
    main()
