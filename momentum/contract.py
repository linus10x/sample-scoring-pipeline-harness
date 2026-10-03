"""Canonical daily contract. Identical retries collapse; conflicting keys quarantine ALL.
Counters are nonnegative integers <= 10**12 (explicit synthetic sample limit).
"""
import datetime as dt
from collections import defaultdict
FIELDS = {"creator_id": str, "date": str, "followers": int, "views": int, "engagements": int}

def validate(rows, as_of):
    if not isinstance(as_of, dt.date) or isinstance(as_of, dt.datetime):
        raise ValueError("as_of must be a date")
    groups, q, good = defaultdict(list), [], []
    for i, r in enumerate(rows):
        reason = None
        if not isinstance(r, dict) or set(r) != set(FIELDS):
            reason = "schema_mismatch"
        else:
            for k, t in FIELDS.items():
                if r[k] is None:
                    reason = "null:"+k; break
                if not isinstance(r[k], t) or isinstance(r[k], bool):
                    reason = "type:"+k; break
            if reason is None:
                try:
                    d = dt.date.fromisoformat(r["date"])
                except ValueError:
                    reason = "bad_date"
                else:
                    if d.isoformat() != r["date"]:
                        reason = "noncanonical_date"
                    elif not r["creator_id"].strip() or r["creator_id"] != r["creator_id"].strip() or len(r["creator_id"]) > 100:
                        reason = "bad_creator_id"
                    elif d > as_of:
                        reason = "future_date"
                    elif min(r[k] for k in ("followers", "views", "engagements")) < 0:
                        reason = "negative_count"
                    elif max(r[k] for k in ("followers", "views", "engagements")) > 10**12:
                        reason = "count_out_of_range"
        if reason:
            q.append({"row": i, "reason": reason})
        else:
            groups[(r["creator_id"], r["date"])].append((i, r))
    for k in sorted(groups):
        items = groups[k]
        if any(r != items[0][1] for _, r in items):
            q.extend({"row": i, "reason": "conflicting_duplicate"} for i, _ in items)
        else:
            good.append(dict(items[0][1]))
            q.extend({"row": i, "reason": "duplicate_key"} for i, _ in items[1:])
    return good, sorted(q, key=lambda x: x["row"])
