from pathlib import Path
import sqlite3
import re

DATABASE = Path("data/qa/annotation_qa.db")
SQL_FILE = Path("sql/annotation_analysis.sql")


def remove_sql_comments(sql):
    lines = []

    for line in sql.splitlines():
        stripped = line.strip()

        if stripped.startswith("--"):
            continue

        lines.append(line)

    return "\n".join(lines)


def main():
    if not DATABASE.exists():
        raise FileNotFoundError(f"Database not found: {DATABASE}")

    if not SQL_FILE.exists():
        raise FileNotFoundError(f"SQL file not found: {SQL_FILE}")

    sql = SQL_FILE.read_text(encoding="utf-8")
    sql = remove_sql_comments(sql)

    statements = [
        statement.strip()
        for statement in sql.split(";")
        if statement.strip()
    ]

    query_number = 0

    with sqlite3.connect(DATABASE) as conn:

        for statement in statements:

            if not re.match(r"^\s*SELECT\b", statement, re.IGNORECASE):
                continue

            query_number += 1

            cursor = conn.execute(statement)
            rows = cursor.fetchall()

            print("\n" + "=" * 70)
            print(f"SQL QUERY {query_number}")
            print("=" * 70)

            if cursor.description:
                columns = [column[0] for column in cursor.description]

                print(" | ".join(columns))
                print("-" * 70)

                for row in rows:
                    print(" | ".join(str(value) for value in row))

    print("\nSQL analysis completed successfully.")


if __name__ == "__main__":
    main()