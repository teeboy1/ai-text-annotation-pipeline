from pathlib import Path
import re
import pandas as pd

INPUT = Path("data/annotation/annotation_queue.csv")
OUTPUT = Path("data/annotation/annotation_candidates.csv")


def normalize(text):
    text = str(text).lower()

    replacements = {
        "purhase": "purchase",
        "acount": "account",
        "fopr": "for",
        "ur": "your",
        "assistat": "assistant",
        "cvases": "cases",
        "correcing": "correcting",
        "restitution": "refund",
        "reimbursement": "refund",
        "rebate": "refund",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(r"\s+", " ", text)
    return text.strip()


def propose_intent(text):
    text = normalize(text)

    # ---------------------------------------------------------
    # HIGH-PRIORITY RULES
    # These rules resolve known overlaps before general rules.
    # ---------------------------------------------------------
    # Existing purchase/order modification
    if (
        any(word in text for word in [
            "purchase",
            "order",
        ])
        and any(word in text for word in [
            "change",
            "changing",
            "correct",
            "correcting",
            "edit",
            "editing",
            "modify",
            "modification",
            "add",
            "remove",
            "delete",
        ])
    ):
        return (
            "change_order",
            0.96,
            "FALSE",
            "Existing purchase/order modification detected.",
        )

    # Switching between account categories/types
    if (
        "account" in text
        and any(phrase in text for phrase in [
            "change to",
            "switch to",
            "move to",
        ])
    ):
        return (
            "switch_account",
            0.96,
            "FALSE",
            "Account-type switching language detected.",
        )

    # Ambiguous account-opening language
    if (
        "account" in text
        and any(word in text for word in [
            "opening",
            "open",
        ])
        and not any(word in text for word in [
            "create",
            "creating",
            "new",
        ])
    ):
        return (
            "UNCERTAIN",
            0.50,
            "TRUE",
            "Account-opening language may indicate creation or registration assistance.",
        )

    # Ambiguous refund destination/request wording
    if (
        any(phrase in text for phrase in [
            "where to get my money back",
            "where can i get my money back",
            "where do i get my money back",
        ])
    ):
        return (
            "UNCERTAIN",
            0.50,
            "TRUE",
            "Refund request versus refund-status intent is ambiguous.",
        )
    # Existing delivery/shipping address is being changed.
    if (
        "address" in text
        and any(word in text for word in [
            "change",
            "changing",
            "edit",
            "editing",
            "update",
            "updating",
            "correct",
            "correcting",
            "modify",
            "modification",
        ])
    ):
        return (
            "change_shipping_address",
            0.95,
            "FALSE",
            "Existing delivery/shipping address modification detected.",
        )

    # Refund policy / eligibility.
    if (
        any(word in text for word in [
            "refund",
            "money back",
            "reimbursement",
        ])
        and any(word in text for word in [
            "policy",
            "policies",
            "situation",
            "situations",
            "case",
            "cases",
            "condition",
            "conditions",
            "eligible",
            "eligibility",
            "rules",
        ])
    ):
        return (
            "check_refund_policy",
            0.96,
            "FALSE",
            "Refund policy or eligibility language detected.",
        )

    # Tracking an existing refund.
    if (
        any(word in text for word in [
            "refund",
            "money back",
            "reimbursement",
            "rebate",
        ])
        and any(word in text for word in [
            "track",
            "tracking",
            "status",
            "news",
            "when",
            "expect",
            "expected",
        ])
    ):
        return (
            "track_refund",
            0.96,
            "FALSE",
            "Refund tracking/status language detected.",
        )

    # Removing an item/product from an existing order.
    if (
        any(word in text for word in [
            "delete",
            "remove",
        ])
        and any(word in text for word in [
            "item",
            "product",
        ])
        and any(word in text for word in [
            "order",
            "purchase",
        ])
    ):
        return (
            "change_order",
            0.96,
            "FALSE",
            "Existing order modification detected.",
        )

    # Opening a new account.
    if (
        any(word in text for word in [
            "open",
            "create",
            "new",
        ])
        and "account" in text
        and not any(word in text for word in [
            "problem",
            "issue",
            "error",
            "cannot",
            "can't",
            "unable",
        ])
    ):
        return (
            "create_account",
            0.94,
            "FALSE",
            "New account creation language detected.",
        )

    # ---------------------------------------------------------
    # GENERAL RULES
    # ---------------------------------------------------------

    rules = {
        "cancel_order": [
            ["cancel", "cancelling", "cancellation"],
            ["order", "purchase"],
        ],

        "check_cancellation_fee": [
            ["cancellation", "termination", "cancel"],
            ["fee", "charge", "penalty"],
        ],

        "check_invoice": [
            ["check", "see", "view", "look"],
            ["invoice", "bill"],
        ],

        "check_payment_methods": [
            ["payment", "pay"],
            ["method", "methods", "ways"],
        ],

        "complaint": [
            ["complaint", "complain"],
        ],

        "contact_customer_service": [
            ["customer service", "customer assistance"],
        ],

        "contact_human_agent": [
            ["human", "person", "agent", "assistant"],
            ["talk", "speak", "contact"],
        ],

        "delete_account": [
            ["delete", "close", "remove"],
            ["account"],
        ],

        "delivery_options": [
            ["delivery", "shipping"],
            ["option", "options", "choice", "choices"],
        ],

        "delivery_period": [
            ["when", "how long", "time"],
            ["arrive", "delivery", "shipment", "item"],
        ],

        "edit_account": [
            ["edit", "change", "update", "correct", "modify"],
            ["account", "information", "data"],
        ],

        "get_invoice": [
            ["download", "get", "receive"],
            ["invoice", "bill"],
        ],

        "get_refund": [
            ["refund", "money back"],
            ["request", "ask", "want", "get"],
        ],

        "newsletter_subscription": [
            ["newsletter"],
        ],

        "payment_issue": [
            ["payment", "pay"],
            ["problem", "issue", "error", "unable", "cannot"],
        ],

        "place_order": [
            ["buy", "purchase", "shop", "order"],
            ["product", "item", "article"],
        ],

        "recover_password": [
            ["reset", "forgot", "forgotten", "recover"],
            ["password", "pin", "key"],
        ],

        "registration_problems": [
            ["registration", "register"],
            ["problem", "issue", "error", "cannot", "unable"],
        ],

        "review": [
            ["review", "feedback"],
        ],

        "set_up_shipping_address": [
            ["set", "setup", "add", "submit"],
            ["shipping address", "delivery address"],
        ],

        "switch_account": [
            ["switch"],
            ["account"],
        ],

        "track_order": [
            ["track", "status", "where"],
            ["order", "shipment", "item"],
        ],
    }

    confidence = {
        "cancel_order": 0.92,
        "check_cancellation_fee": 0.92,
        "check_invoice": 0.90,
        "check_payment_methods": 0.90,
        "complaint": 0.95,
        "contact_customer_service": 0.90,
        "contact_human_agent": 0.92,
        "delete_account": 0.93,
        "delivery_options": 0.90,
        "delivery_period": 0.90,
        "edit_account": 0.88,
        "get_invoice": 0.92,
        "get_refund": 0.92,
        "newsletter_subscription": 0.95,
        "payment_issue": 0.92,
        "place_order": 0.85,
        "recover_password": 0.93,
        "registration_problems": 0.92,
        "review": 0.90,
        "set_up_shipping_address": 0.90,
        "switch_account": 0.85,
        "track_order": 0.92,
    }

    candidates = []

    for intent, groups in rules.items():

        matched = 0

        for group in groups:
            if any(term in text for term in group):
                matched += 1

        if matched == len(groups):
            candidates.append(
                (
                    intent,
                    confidence[intent],
                )
            )

    if not candidates:
        return (
            "UNCERTAIN",
            0.0,
            "TRUE",
            "No rule matched the instruction.",
        )

    candidates.sort(key=lambda x: x[1], reverse=True)

    if len(candidates) > 1:
        top = candidates[0]
        second = candidates[1]

        if abs(top[1] - second[1]) < 0.08:
            return (
                "UNCERTAIN",
                round(top[1], 2),
                "TRUE",
                f"Conflicting intent signals: {top[0]}, {second[0]}",
            )

    best_intent, best_score = candidates[0]

    return (
        best_intent,
        best_score,
        "FALSE",
        "Intent proposed from instruction text using rule-based signals.",
    )


def main():

    df = pd.read_csv(INPUT, dtype=str).fillna("")

    required = {
        "record_id",
        "instruction",
        "intent",
    }

    missing = required - set(df.columns)

    if missing:
        raise ValueError(
            f"Missing required columns: {sorted(missing)}"
        )

    results = []

    for _, row in df.iterrows():

        (
            proposed,
            confidence,
            review_required,
            notes,
        ) = propose_intent(row["instruction"])

        results.append(
            {
                "record_id": row["record_id"],
                "instruction": row["instruction"],
                "source_intent": row["intent"],
                "proposed_intent": proposed,
                "proposal_confidence": confidence,
                "requires_human_review": review_required,
                "proposal_notes": notes,
            }
        )

    output = pd.DataFrame(results)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    output.to_csv(
        OUTPUT,
        index=False,
    )

    print(
        f"Created annotation candidates: {OUTPUT}"
    )

    print(
        f"Records analyzed: {len(output)}"
    )

    print("\nProposed intent distribution:")
    print(
        output["proposed_intent"].value_counts()
    )

    print("\nHuman-review distribution:")
    print(
        output["requires_human_review"].value_counts()
    )


if __name__ == "__main__":
    main()