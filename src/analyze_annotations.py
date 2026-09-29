from pathlib import Path
import pandas as pd

INPUT = Path("data/annotation/annotation_candidates.csv")
OUTPUT = Path("data/qa/annotation_analysis.csv")
SUMMARY = Path("data/qa/annotation_summary.txt")


def main():
    df = pd.read_csv(INPUT, dtype=str).fillna("")

    required = {
        "record_id",
        "instruction",
        "source_intent",
        "proposed_intent",
        "proposal_confidence",
        "requires_human_review",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    # Compare independent proposal against the source label.
    df["intent_match"] = (
        (df["proposed_intent"] != "UNCERTAIN")
        & (df["proposed_intent"] == df["source_intent"])
    )

    df["analysis_status"] = "MATCH"

    df.loc[
        df["proposed_intent"] == "UNCERTAIN",
        "analysis_status"
    ] = "UNCERTAIN"

    df.loc[
        (df["proposed_intent"] != "UNCERTAIN")
        & (df["proposed_intent"] != df["source_intent"]),
        "analysis_status"
    ] = "MISMATCH"

    # Save record-level analysis.
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)

    total = len(df)
    matches = (df["analysis_status"] == "MATCH").sum()
    mismatches = (df["analysis_status"] == "MISMATCH").sum()
    uncertain = (df["analysis_status"] == "UNCERTAIN").sum()

    comparable = matches + mismatches

    if comparable:
        agreement = matches / comparable
    else:
        agreement = 0.0

    review_count = (
        df["requires_human_review"] == "TRUE"
    ).sum()

    summary = [
        "CUSTOMER SUPPORT ANNOTATION QA SUMMARY",
        "=" * 45,
        f"Total records: {total}",
        f"Matches: {matches}",
        f"Mismatches: {mismatches}",
        f"Uncertain: {uncertain}",
        f"Human review required: {review_count}",
        "",
        f"Agreement among non-uncertain proposals: {agreement:.2%}",
        "",
        "Analysis status distribution:",
        str(df["analysis_status"].value_counts()),
        "",
        "Source intent distribution:",
        str(df["source_intent"].value_counts().sort_index()),
        "",
        "Proposed intent distribution:",
        str(df["proposed_intent"].value_counts().sort_index()),
    ]

    SUMMARY.write_text("\n".join(summary), encoding="utf-8")

    print(f"Created record-level analysis: {OUTPUT}")
    print(f"Created summary: {SUMMARY}")

    print("\nQA SUMMARY")
    print("=" * 30)
    print(f"Total records: {total}")
    print(f"Matches: {matches}")
    print(f"Mismatches: {mismatches}")
    print(f"Uncertain: {uncertain}")
    print(f"Human review required: {review_count}")
    print(f"Agreement among non-uncertain proposals: {agreement:.2%}")


if __name__ == "__main__":
    main()