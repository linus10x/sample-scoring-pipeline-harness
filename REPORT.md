# SAMPLE harness report (synthetic data)

Synthetic data as-of: 2026-08-11. Run UTC: 2026-10-03T05:14:38.404476+00:00. Python: 3.12.14.

| Check | Result | Blocking | Detail |
|---|---|---|---|
| C1a Clean input passes the data contract | PASS | yes | 1560 rows, 0 quarantined |
| C1b Defective input is quarantined with reasons | PASS | yes | 28 of 1576 rows quarantined; reasons: bad_date, duplicate_key, future_date, negative_count, null:followers, type:views |
| C2-v1 v1: same input, any row order, same output | PASS | yes | output digest 4baa51cbe81a584c |
| C3-v1 v1: duplicated rows do not change scores | PASS | yes | 50 duplicate rows added, then contract applied |
| C4-v1 v1: doubling last-week engagement never lowers a score | PASS | yes | 15 creators tested, 0 violations |
| C5-v1 v1: scores finite and within 0-100 | PASS | yes | min 29.20, max 86.19 |
| C6-v1 v1: creators with < 14 days are not ranked | PASS | yes | unranked: creator-000, creator-010, creator-020, creator-030 |
| C2-v2 v2: same input, any row order, same output | PASS | yes | output digest 0b28bf905802b7ce |
| C3-v2 v2: duplicated rows do not change scores | PASS | yes | 50 duplicate rows added, then contract applied |
| C4-v2 v2: doubling last-week engagement never lowers a score | PASS | yes | 15 creators tested, 0 violations |
| C5-v2 v2: scores finite and within 0-100 | PASS | yes | min 11.40, max 99.91 |
| C6-v2 v2: creators with < 14 days are not ranked | PASS | yes | unranked: creator-000, creator-010, creator-020, creator-030 |
| C7 v1 matches hand-computed golden fixtures | PASS | yes | {"g-drop": 0.6693, "g-flat": 50.0, "g-up": 99.3307} |
| C7-v2 v2 matches independent golden fixtures | PASS | yes | {'g-drop': 16.8367, 'g-flat': 26.3163, 'g-up': 34.8228} |
| C13 v2 follower-growth term matches independent oracles | PASS | yes | {'f-drop': 1.2433, 'f-up': 99.2795} |
| C9-v1 v1: unsaturated fixture responds strictly to new engagement | PASS | yes | 50.0 -> 99.3307 |
| C10-v1 v1: stale history is unranked | PASS | yes | {'g-flat': None} |
| C11-v1 v1: dirty input order does not change accepted rows or scores | PASS | yes | Full contract + scoring path |
| C9-v2 v2: unsaturated fixture responds strictly to new engagement | PASS | yes | 26.3163 -> 34.8228 |
| C10-v2 v2: stale history is unranked | PASS | yes | {'g-flat': None} |
| C11-v2 v2: dirty input order does not change accepted rows or scores | PASS | yes | Full contract + scoring path |
| C12 Conflicting duplicates quarantine all rows for the key | PASS | yes | Conflicting key excluded in either input order |
| C8 v1 -> v2 drift within illustrative threshold (top-10 overlap >= 6) | PASS | advisory | top-10 overlap 6/10, tie-aware Spearman rho 0.5523809523809524. Product sign-off required before either version changes a real ranking, regardless of this advisory result. |

Blocking checks passed: 22/22. Advisory checks failing: 0.
