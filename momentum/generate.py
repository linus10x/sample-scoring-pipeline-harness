"""Deterministic synthetic daily metrics for invented creators. No real people or platforms."""
import datetime as dt, random

START = dt.date(2026, 7, 1)


def clean_rows(n_creators=40, days=42, seed=7):
    rng = random.Random(seed)
    rows = []
    for c in range(n_creators):
        cid = f"creator-{c:03d}"
        followers = rng.randint(1_000, 200_000)
        trend = rng.uniform(-0.01, 0.03)          # daily growth rate
        base_eng = followers * rng.uniform(0.005, 0.04)
        start_day = 0 if c % 10 else 30           # every tenth creator is new (short history)
        for d in range(start_day, days):
            followers = max(0, int(followers * (1 + trend + rng.uniform(-0.004, 0.004))))
            eng = max(0, int(base_eng * (1 + trend) ** d * rng.uniform(0.7, 1.3)))
            rows.append({"creator_id": cid, "date": (START + dt.timedelta(days=d)).isoformat(),
                         "followers": followers, "views": eng * rng.randint(8, 30), "engagements": eng})
    return rows


def inject_defects(rows, seed=11):
    """The kinds of defect an informally built pipeline usually lets through."""
    rng = random.Random(seed)
    bad = [dict(r) for r in rows]
    bad += [dict(r) for r in rng.sample(rows, 15)]                       # exact duplicates
    for r in rng.sample(bad, 5):
        r["engagements"] = -abs(r["engagements"]) - 1                    # negative counts
    for r in rng.sample(bad, 3):
        r["followers"] = None                                            # nulls
    for r in rng.sample(bad, 2):
        r["date"] = "2026-13-45"                                         # unparseable date
    bad.append({"creator_id": "creator-001", "date": "2027-01-01", "followers": 1, "views": 1, "engagements": 1})  # future
    for r in rng.sample(bad, 2):
        r["views"] = str(r["views"])                                     # wrong type
    return bad
