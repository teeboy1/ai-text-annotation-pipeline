from pathlib import Path
import pandas as pd

INPUT = Path("data/sample/customer_support_sample.csv")
REPORT = Path("data/qa/annotation_validation.csv")

VALID_REGISTERS = {"FORMAL", "NEUTRAL", "POLITE", "COLLOQUIAL", "KEYWORD", "OTHER", ""}
VALID_MATCH = {"TRUE", "FALSE", "UNCERTAIN", ""}
VALID_BOOL = {"TRUE", "FALSE", ""}

def main():
    df = pd.read_csv(INPUT, dtype=str).fillna("")
    errors = []

    def check(condition, error_type, mask):
        for rid in df.loc[mask, "record_id"]:
            errors.append({"record_id": rid, "error_type": error_type})

    check(df["record_id"].duplicated(), "DUPLICATE_RECORD_ID", df["record_id"].duplicated())
    check(df["instruction"].str.strip().eq(""), "EMPTY_INSTRUCTION", df["instruction"].str.strip().eq(""))
    check(~df["intent"].isin(df["intent"].unique()), "INVALID_SOURCE_INTENT", ~df["intent"].isin(df["intent"].unique()))
    check(~df["language_register"].isin(VALID_REGISTERS), "INVALID_LANGUAGE_REGISTER", ~df["language_register"].isin(VALID_REGISTERS))
    check(~df["intent_match"].isin(VALID_MATCH), "INVALID_INTENT_MATCH", ~df["intent_match"].isin(VALID_MATCH))
    check(~df["ambiguity"].isin(VALID_BOOL), "INVALID_AMBIGUITY", ~df["ambiguity"].isin(VALID_BOOL))
    check(~df["requires_human_review"].isin(VALID_BOOL), "INVALID_REVIEW_FLAG", ~df["requires_human_review"].isin(VALID_BOOL))

    conf = pd.to_numeric(df["annotation_confidence"], errors="coerce")
    bad_conf = df["annotation_confidence"].ne("") & (conf.lt(0) | conf.gt(1) | conf.isna())
    check(bad_conf, "INVALID_CONFIDENCE", bad_conf)

    report = pd.DataFrame(errors, columns=["record_id", "error_type"])
    REPORT.parent.mkdir(parents=True, exist_ok=True)
    report.to_csv(REPORT, index=False)

    print(f"Records checked: {len(df)}")
    print(f"Validation errors: {len(report)}")
    if not report.empty:
        print(report["error_type"].value_counts())

if __name__ == "__main__":
    main()
