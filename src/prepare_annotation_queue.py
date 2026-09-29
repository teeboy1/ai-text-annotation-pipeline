from pathlib import Path
import pandas as pd

INPUT = Path("data/sample/customer_support_sample.csv")
OUTPUT = Path("data/annotation/annotation_queue.csv")

VALID_INTENTS = {
    "cancel_order",
    "change_order",
    "change_shipping_address",
    "check_cancellation_fee",
    "check_invoice",
    "check_payment_methods",
    "check_refund_policy",
    "complaint",
    "contact_customer_service",
    "contact_human_agent",
    "create_account",
    "delete_account",
    "delivery_options",
    "delivery_period",
    "edit_account",
    "get_invoice",
    "get_refund",
    "newsletter_subscription",
    "payment_issue",
    "place_order",
    "recover_password",
    "registration_problems",
    "review",
    "set_up_shipping_address",
    "switch_account",
    "track_order",
    "track_refund",
}


def main():
    df = pd.read_csv(INPUT, dtype=str).fillna("")

    missing = {"record_id", "instruction", "intent"} - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")

    invalid = set(df["intent"]) - VALID_INTENTS
    if invalid:
        raise ValueError(f"Unexpected source intents: {sorted(invalid)}")

    queue = df[
        [
            "record_id",
            "instruction",
            "category",
            "intent",
            "response",
            "flags",
        ]
    ].copy()

    # Independent review fields.
    # These remain blank until the instruction is actually reviewed.
    queue["reviewed_intent"] = ""
    queue["intent_match"] = ""
    queue["language_register"] = ""
    queue["ambiguity"] = ""
    queue["requires_human_review"] = ""
    queue["annotation_confidence"] = ""
    queue["review_notes"] = ""
    queue["annotation_status"] = "UNREVIEWED"

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    queue.to_csv(OUTPUT, index=False)

    print(f"Created annotation queue: {OUTPUT}")
    print(f"Records queued: {len(queue)}")
    print(f"Status: UNREVIEWED")


if __name__ == "__main__":
    main()

