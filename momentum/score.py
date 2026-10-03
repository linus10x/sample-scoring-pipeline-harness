"""Invented scores, not business recommendations. Call contract.validate() first.
Both require ALL latest 14 consecutive daily records; stale/sparse histories stay unranked.
v2 uses available validated daily records in the latest 28 days, always at least 14.
"""
import datetime as dt, math
from collections import defaultdict
MIN_HISTORY_DAYS = 14

def _by_creator(rows):
    out = defaultdict(dict)
    for r in rows:
        out[r["creator_id"]][dt.date.fromisoformat(r["date"])] = r
    return out

def _window(series, end, days):
    # The public date contract includes date.min. Never subtract past it.
    lookback = min(days, end.toordinal())
    return [series[end-dt.timedelta(days=i)] for i in range(lookback) if end-dt.timedelta(days=i) in series]

def _eligible(s, as_of):
    return len(_window(s, as_of, MIN_HISTORY_DAYS)) == MIN_HISTORY_DAYS

def _sigmoid100(x):
    if x >= 0:
        return 100/(1+math.exp(-x))
    e = math.exp(x)
    return 100*e/(1+e)

def score_v1(rows, as_of):
    res = {}
    for cid, s in sorted(_by_creator(rows).items()):
        if not _eligible(s, as_of):
            res[cid] = None; continue
        recent = sum(r["engagements"] for r in _window(s, as_of, 7))
        prior = sum(r["engagements"] for r in _window(s, as_of-dt.timedelta(days=7), 7))
        res[cid] = round(_sigmoid100(5*(recent-prior)/max(prior,1)),4)
    return res

def score_v2(rows, as_of, half_life_days=7.0):
    if isinstance(half_life_days, bool) or not isinstance(half_life_days, (float, int)) or not 0 < half_life_days <= 36500:
        raise ValueError("half_life_days must be positive, finite, and <= 36500 (sample limit)")
    res = {}
    for cid, s in sorted(_by_creator(rows).items()):
        if not _eligible(s, as_of):
            res[cid] = None; continue
        window = _window(s, as_of, 28)
        weighted_rate, total_weight = 0.0, 0.0
        for r in window:
            age = (as_of-dt.date.fromisoformat(r["date"])).days
            w = 0.5**(age/half_life_days)
            weighted_rate += w*r["engagements"]/max(r["followers"],1)
            total_weight += w
        rate = weighted_rate/total_weight
        first, last = window[-1]["followers"], window[0]["followers"]
        growth = (last-first)/max(first,1)
        raw = 0.7*math.log1p(rate*100)+0.3*growth*10
        res[cid] = round(_sigmoid100((raw-1)*2),4)
    return res
