# SAMPLE: validation harness for a proprietary scoring pipeline

> **Sample / illustrative work by Kunjar Bhaduri (Bhaduri Advisory). Synthetic data only; every "creator" is invented. Not a client deliverable and not based on any real company's code or data.** Built October 2, 2026, with AI coding assistance under my direction; I reviewed, ran and tested it.

## Which bids it answers
Written as a work sample for fractional CTO postings where an early-stage analytics company has a fragile, AI-patched scoring pipeline and needs it validated before investor diligence, and for analytics SaaS roles that ask for pipeline reliability and accuracy checks. **Illustrative sample on synthetic data. No client relationship.**

## The problem it shows
A startup's ranking or scoring system is usually the thing investors and customers trust least, because nobody can show it behaves. When the pipeline was built quickly (and patched with AI-generated fixes), the first job is not to rewrite it. It is to put a harness around it that proves, on every change, that the score is stable, explainable and protected from bad data. This sample shows that harness on an invented "creator momentum" score.

## What the harness checks
| Check | Why an investor or customer cares |
|---|---|
| C1 Data contract: schema, types, nulls, negative counts, bad or future dates, duplicate keys. Bad rows are quarantined with a reason, never silently fixed | Garbage in can't quietly move a ranking |
| C2 Determinism: same input in any row order gives the same output digest | Re-running the pipeline can't reshuffle the leaderboard |
| C3 Duplicate invariance once the contract runs | Retries and double-loads don't inflate anyone |
| C4 Monotonicity: doubling a creator's last-week engagement never lowers their score | The score moves the way the business says it does |
| C5 Bounds: finite, within 0 to 100 | No NaN or overflow reaching the UI |
| C6 Cold start: creators with under 14 days of history are not ranked | New accounts can't spike to the top on thin data |
| C7 Golden fixtures with hand-computed expected values | Anyone can verify the maths by hand |
| C8 Version drift (advisory): v1 vs v2 top-10 overlap and Spearman correlation | A scoring change customers will notice needs a named product sign-off |

## Run it (Python 3.10+, standard library only)
```bash
python3 harness.py --report REPORT.md     # exit 0 only if every blocking check passes
python3 -m unittest discover -s tests     # 4 tests
```
Result on Oct 2, 2026 (Linux box, Python 3.13.5): 13/13 blocking checks passed, the advisory drift check passed at the threshold (top-10 overlap 6/10, Spearman 0.55), 4 unit tests passed. See `REPORT.md`.

## How I'd use this on a real engagement
Week 1: wrap the existing scoring code as-is (no rewrite), write the data contract from what the data actually looks like, and add golden fixtures the founders agree are correct. Week 2: run it in CI on every change, and turn the report into a one-page "how we know the score is right" exhibit for investor diligence.

## Limits
- Synthetic data and invented scoring formulas. Neither formula is a recommendation.
- The checks are examples; a real harness is built around the client's actual score definition and data.
- No claim about any real platform's accuracy or performance.

## Where it lives
Private repository github.com/linus10x/sample-scoring-pipeline-harness until it has been reviewed; it becomes public only after that review.
