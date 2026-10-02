"""Data contract for the scoring input. Bad rows are quarantined with a reason, never silently fixed."""
import datetime as dt

FIELDS = {"creator_id": str, "date": str, "followers": int, "views": int, "engagements": int}


def validate(rows, as_of):
    good, quarantined, seen = [], [], set()
    for i, r in enumerate(rows):
        reason = None
        if set(r) != set(FIELDS):
            reason = "schema_mismatch"
        else:
            for k, t in FIELDS.items():
                if r[k] is None:
                    reason = f"null:{k}"; break
                if not isinstance(r[k], t) or isinstance(r[k], bool):
                    reason = f"type:{k}"; break
            if reason is None:
                try:
                    d = dt.date.fromisoformat(r["date"])
                except ValueError:
                    reason = "bad_date"
                else:
                    if d > as_of:
                        reason = "future_date"
                    elif min(r["followers"], r["views"], r["engagements"]) < 0:
                        reason = "negative_count"
                    elif (r["creator_id"], r["date"]) in seen:
                        reason = "duplicate_key"
        if reason:
            quarantined.append({"row": i, "reason": reason})
        else:
            seen.add((r["creator_id"], r["date"]))
            good.append(r)
    return good, quarantined
