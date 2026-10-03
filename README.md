# SAMPLE: validation harness for creator-momentum scoring

> **Illustrative sample on synthetic data by Kunjar Bhaduri, Bhaduri Advisory. Every creator and metric is synthetic. Invented formulas; no client relationship, client code or result. Built by AI coding tools under my direction. Revised October 2, 2026 (America/Chicago).**

This supports the [Engineering Analytics fractional CTO mandate](https://www.gofractional.com/job/fractional-cto-cmu3aud7): establish how a fragile scoring pipeline behaves and make changes reviewable. It puts a deterministic contract and regression checks around two invented formulas. It does not establish real-world creator-scoring accuracy. The MCP gateway is the separate SnapLogic AI Architect sample.

## Run

Python 3.10+, standard library only. From this repository:

```bash
python3 harness.py --report REPORT.md
python3 -m unittest discover -s tests -v
```

Exit 0 requires every blocking check to pass. [REPORT.md](REPORT.md) separates run timestamp, Python version and synthetic-data cutoff. [VERIFICATION.md](VERIFICATION.md) records test results. The CI workflow repeats these commands; its presence does not establish a hosted CI pass.

## Input and ranking contract

Rows have exactly `creator_id`, ISO `YYYY-MM-DD` date, followers, views and engagements. IDs are trimmed, nonblank strings of at most 100 characters. Counters are nonnegative integers, excluding booleans, and at most `10**12` (explicit sample limit). The full calendar range through `date.min` is accepted, with lookback clamped at that boundary; insufficient history remains unranked. Future dates, nulls, nonmapping rows and schema/type errors are quarantined with reasons.

Identical retries collapse to one accepted row; extras are reported as `duplicate_key`. If valid rows conflict for a creator/date, **all valid rows for that key** are quarantined as `conflicting_duplicate`. Invalid rows quarantine independently. Accepted rows sort canonically; ingestion order cannot choose a score. Quarantine indices refer to input order.

Both scorers require all latest 14 consecutive days ending at the cutoff. Stale/sparse histories are unranked (`None`); absent creators produce no key. Run `contract.validate` first. Direct scorer functions assume validated input.

v1 compares latest-seven engagement with the preceding seven, divides growth by `max(prior,1)`, then applies `100*logistic(5*growth)`. v2 uses available records in the latest 28 days, weights engagement/follower rate with a seven-day half-life, blends `0.7*ln(1+100*rate)` with `0.3*10*follower_growth`, then applies `100*logistic(2*(raw-1))`. Latest 14 days must be complete; missing days 15-28 contribute no record. Zero-follower denominators use one. Half-life is positive, finite and at most 36,500 days. These are sample conventions, not business recommendations.

## Checks

| Check | Evidence within the sample |
|---|---|
| Contract | Clean input accepted; defective rows quarantined; conflicting duplicates rejected in either order |
| Repeatability | Same input repeats; clean and dirty end-to-end row orders produce identical scores |
| Retry invariance | Identical retries cannot inflate scores after validation |
| Response | Recent engagement does not lower scores in tested data; unsaturated fixtures require a strict increase |
| Bounds/freshness | Finite scores in 0-100; new/stale histories unranked |
| Golden fixtures | Both versions match specified flat/up/drop expectations; v2 follower-increase/decrease fixtures also verify the growth term, independently evaluated with 50/60-digit Decimal arithmetic |
| Mutations | Constant-v2, inverted-v1 and dropped-follower-growth v2 are injected into the actual harness; tests require blocking failures |
| Drift | Top-ten overlap plus tie-aware Spearman correlation; undefined correlation returns `None` |

The six-shared-top-ten threshold is illustrative and advisory. A pass does not approve replacing a production formula. Product sign-off must use the actual score definition, approved representative data and customer impact.

## Use on an engagement

Preserve the existing scorer first. Agree the contract and golden cases with product, investigate failures/quarantine rates, then add real fixtures, release gates and freshness/latency monitoring. Investor evidence should show reproducible results, unresolved risks and the actual scope covered.

This verifies implemented mathematical and contract behavior on synthetic examples. It does not validate a client's formula, causal outcome, fairness, production latency or commercial accuracy. Publication requires owner approval.
