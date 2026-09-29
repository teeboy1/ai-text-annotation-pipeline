from pathlib import Path
import pandas as pd
from datasets import load_dataset

OUT = Path("data/sample/customer_support_sample.csv")
N = 300
RANDOM_STATE = 42

def main():
    print("Loading Bitext dataset...")
    ds = load_dataset(
        "bitext/Bitext-customer-support-llm-chatbot-training-dataset",
        split="train"
    )
    df = ds.to_pandas()

    required = {"instruction", "category", "intent", "response", "flags"}
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns: {sorted(missing)}")

    # Keep the sample balanced across intents as far as possible.
    # With 27 intents and N=300, most intents receive 11 rows and the
    # remainder receive 12 rows.
    per_intent = N // df["intent"].nunique()
    remainder = N % df["intent"].nunique()

    pieces = []
    for i, (intent, group) in enumerate(df.groupby("intent", sort=True)):
        take = per_intent + (1 if i < remainder else 0)
        if len(group) < take:
            raise ValueError(f"Not enough rows for intent: {intent}")
        pieces.append(group.sample(take, random_state=RANDOM_STATE))

    sample = pd.concat(pieces).sample(frac=1, random_state=RANDOM_STATE).reset_index(drop=True)
    sample.insert(0, "record_id", [f"CS-{i:04d}" for i in range(1, len(sample) + 1)])

    # Independent review fields start empty. They are not copied from the source.
    sample["reviewed_intent"] = ""
    sample["intent_match"] = ""
    sample["language_register"] = ""
    sample["ambiguity"] = ""
    sample["requires_human_review"] = ""
    sample["annotation_confidence"] = ""
    sample["review_notes"] = ""

    OUT.parent.mkdir(parents=True, exist_ok=True)
    sample.to_csv(OUT, index=False)

    print(f"Created {len(sample)} records at {OUT}")
    print("\nIntent distribution:")
    print(sample["intent"].value_counts().sort_index())

if __name__ == "__main__":
    main()
