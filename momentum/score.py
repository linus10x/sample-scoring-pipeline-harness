"""Two versions of an invented 'momentum' score (0-100), so the harness can show version drift.
Neither is a recommendation; they exist to be tested."""
import datetime as dt, math
from collections import defaultdict

MIN_HISTORY_DAYS = 14


def _by_creator(rows):
    out = defaultdict(dict)
    for r in rows:
        out[r["creator_id"]][dt.date.fromisoformat(r["date"])] = r
    return out


def _window(series, end, days):
    return [series[end - dt.timedelta(days=i)] for i in range(days) if end - dt.timedelta(days=i) in series]


def score_v1(rows, as_of):
    """Last 7 days of engagement vs the 7 before, squashed to 0-100."""
    res = {}
    for cid, s in sorted(_by_creator(rows).items()):
        if len(s) < MIN_HISTORY_DAYS:
            res[cid] = None
            continue
        recent = sum(r["engagements"] for r in _window(s, as_of, 7))
        prior = sum(r["engagements"] for r in _window(s, as_of - dt.timedelta(days=7), 7))
        growth = (recent - prior) / max(prior, 1)
        res[cid] = round(100 / (1 + math.exp(-5 * growth)), 4)
    return res


def score_v2(rows, as_of, half_life_days=7.0):
    """Recency-weighted engagement rate per follower, log-scaled, blended with follower growth."""
    res = {}
    for cid, s in sorted(_by_creator(rows).items()):
        if len(s) < MIN_HISTORY_DAYS:
            res[cid] = None
            continue
        window = _window(s, as_of, 28)
        w_sum = rate = 0.0
        for r in window:
            age = (as_of - dt.date.fromisoformat(r["date"])).days
            w = 0.5 ** (age / half_life_days)
            rate += w * r["engagements"] / max(r["followers"], 1)
            w_sum += w
        rate = rate / w_sum if w_sum else 0.0
        first, last = window[-1]["followers"], window[0]["followers"]
        f_growth = (last - first) / max(first, 1)
        raw = 0.7 * math.log1p(rate * 100) + 0.3 * f_growth * 10
        res[cid] = round(100 / (1 + math.exp(-(raw - 1.0) * 2)), 4)
    return res
