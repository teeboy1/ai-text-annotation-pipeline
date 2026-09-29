# Annotation & Review Guidelines

## Purpose

These guidelines define the independent review layer applied to a sample of customer-support utterances.

The source dataset already provides an `intent` label. Reviewers assess whether the supplied label appears consistent with the meaning of the customer instruction and flag cases requiring adjudication.

## Review fields

### reviewed_intent
The intent that best represents the customer's primary request after independent review.

### intent_match
- `TRUE`: source intent and reviewed intent agree.
- `FALSE`: reviewer believes another intent better represents the request.
- `UNCERTAIN`: insufficient context or overlapping intent.

### language_register
Use one of:
- `FORMAL`
- `NEUTRAL`
- `POLITE`
- `COLLOQUIAL`
- `KEYWORD`
- `OTHER`

### ambiguity
- `TRUE`: two or more plausible intents exist.
- `FALSE`: one intent is clearly primary.

### requires_human_review
Set `TRUE` when the case is ambiguous, the reviewer is uncertain, or the source label appears potentially inconsistent.

### annotation_confidence
A value from 0.00 to 1.00 representing reviewer confidence in the reviewed intent.

## Primary-intent rule

When a message contains multiple requests, identify the issue that best represents the customer's main requested action. If no single intent can be established reliably, mark the record ambiguous and send it for human review.

## Quality principles

1. Do not infer facts that are not present in the message.
2. Do not use the response text to invent a customer intent that is absent from the instruction.
3. Preserve the source text.
4. Record uncertainty rather than forcing a label.
5. Use the same rule consistently across similar examples.
6. Escalate genuinely ambiguous examples rather than guessing.
