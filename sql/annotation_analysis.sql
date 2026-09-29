-- Customer Support AI Annotation Project
-- SQL-based QA analysis
-- Source: data/qa/annotation_analysis.csv
-- SQLite table: annotations

-- 1. Overall annotation QA summary
SELECT
    COUNT(*) AS total_records,

    SUM(
        CASE
            WHEN analysis_status = 'MATCH'
            THEN 1 ELSE 0
        END
    ) AS matches,

    SUM(
        CASE
            WHEN analysis_status = 'MISMATCH'
            THEN 1 ELSE 0
        END
    ) AS mismatches,

    SUM(
        CASE
            WHEN analysis_status = 'UNCERTAIN'
            THEN 1 ELSE 0
        END
    ) AS uncertain,

    SUM(
        CASE
            WHEN requires_human_review = 'TRUE'
            THEN 1 ELSE 0
        END
    ) AS human_review_required

FROM annotations;


-- 2. Agreement among non-uncertain proposals
SELECT
    ROUND(
        100.0 *
        SUM(
            CASE
                WHEN analysis_status = 'MATCH'
                THEN 1 ELSE 0
            END
        )
        /
        NULLIF(
            SUM(
                CASE
                    WHEN analysis_status IN ('MATCH', 'MISMATCH')
                    THEN 1 ELSE 0
                END
            ),
            0
        ),
        2
    ) AS agreement_percentage

FROM annotations;


-- 3. Source intent distribution
SELECT
    source_intent,
    COUNT(*) AS record_count

FROM annotations

GROUP BY source_intent

ORDER BY record_count DESC, source_intent;


-- 4. Proposed intent distribution
SELECT
    proposed_intent,
    COUNT(*) AS record_count

FROM annotations

GROUP BY proposed_intent

ORDER BY record_count DESC, proposed_intent;


-- 5. Human-review workload by source intent
SELECT
    source_intent,
    COUNT(*) AS review_count

FROM annotations

WHERE requires_human_review = 'TRUE'

GROUP BY source_intent

ORDER BY review_count DESC, source_intent;


-- 6. Confidence distribution
SELECT
    CASE
        WHEN CAST(proposal_confidence AS REAL) >= 0.90
            THEN 'HIGH'
        WHEN CAST(proposal_confidence AS REAL) >= 0.70
            THEN 'MEDIUM'
        ELSE 'LOW'
    END AS confidence_band,

    COUNT(*) AS records

FROM annotations

GROUP BY confidence_band

ORDER BY
    CASE confidence_band
        WHEN 'HIGH' THEN 1
        WHEN 'MEDIUM' THEN 2
        WHEN 'LOW' THEN 3
    END;


-- 7. Uncertain records requiring human review
SELECT
    record_id,
    instruction,
    source_intent,
    proposed_intent,
    proposal_confidence,
    requires_human_review,
    proposal_notes

FROM annotations

WHERE analysis_status = 'UNCERTAIN'

ORDER BY CAST(proposal_confidence AS REAL) ASC;


-- 8. Remaining mismatches
SELECT
    record_id,
    instruction,
    source_intent,
    proposed_intent,
    proposal_confidence,
    proposal_notes

FROM annotations

WHERE analysis_status = 'MISMATCH'

ORDER BY CAST(proposal_confidence AS REAL) ASC;