from pathlib import Path
import sqlite3
import pandas as pd

INPUT = Path("data/qa/annotation_analysis.csv")
DATABASE = Path("data/qa/annotation_qa.db")


def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT}")

    df = pd.read_csv(INPUT, dtype=str).fillna("")

    DATABASE.parent.mkdir(parents=True, exist_ok=True)

    with sqlite3.connect(DATABASE) as conn:
        df.to_sql(
            "annotations",
            conn,
            if_exists="replace",
            index=False,
        )

    print(f"Created SQLite database: {DATABASE}")
    print("Table: annotations")
    print(f"Records loaded: {len(df)}")


if __name__ == "__main__":
    main()