"""SAMPLE validation harness for a scoring pipeline (synthetic data).
Usage: python3 harness.py [--report REPORT.md]   Exit 0 only if every blocking check passes."""
import datetime as dt, hashlib, json, math, random, sys

from momentum import contract, generate, score

AS_OF = generate.START + dt.timedelta(days=41)
results = []  # compatibility; run() resets this list each time


def check(cid, name, ok, detail, blocking=True):
    results.append({"id": cid, "name": name, "ok": bool(ok), "detail": detail, "blocking": blocking})


def digest(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True).encode()).hexdigest()[:16]


def golden_rows():
    rows = []
    for cid, prior, recent in (("g-up", 10, 20), ("g-flat", 10, 10), ("g-drop", 10, 0)):
        for d in range(14):
            day = AS_OF - dt.timedelta(days=13 - d)
            rows.append({"creator_id": cid, "date": day.isoformat(), "followers": 1000, "views": 100,
                         "engagements": prior if d < 7 else recent})
    return rows

def follower_rows():
    """Only the latest follower count changes; engagement stays at 10 each day."""
    rows = []
    for cid, prior, latest in (("f-up", 1000, 2000), ("f-drop", 2000, 1000)):
        for age in range(14):
            rows.append({"creator_id": cid, "date": (AS_OF-dt.timedelta(days=age)).isoformat(),
                         "followers": latest if age == 0 else prior, "views": 100, "engagements": 10})
    return rows


def spearman(a, b):
    """Pearson correlation of average ranks; None when a rank vector is constant."""
    keys = sorted(k for k in a if a[k] is not None and b.get(k) is not None)
    if len(keys) < 2:
        return None
    def ranks(scores):
        order = sorted(keys, key=lambda k: scores[k])
        r, i = {}, 0
        while i < len(order):
            j = i+1
            while j < len(order) and scores[order[j]] == scores[order[i]]:
                j += 1
            for k in order[i:j]:
                r[k] = (i+j-1)/2
            i = j
        return r
    ra, rb = ranks(a), ranks(b)
    mean = (len(keys)-1)/2
    va = sum((ra[k]-mean)**2 for k in keys)
    vb = sum((rb[k]-mean)**2 for k in keys)
    if not va or not vb:
        return None
    return sum((ra[k]-mean)*(rb[k]-mean) for k in keys)/math.sqrt(va*vb)

def top(s, n=10):
    return [k for k, _ in sorted(((k, v) for k, v in s.items() if v is not None), key=lambda kv: (-kv[1], kv[0]))[:n]]


def run(v1=None, v2=None):
    results.clear()
    v1, v2 = v1 or score.score_v1, v2 or score.score_v2
    clean = generate.clean_rows()
    dirty = generate.inject_defects(clean)

    # C1 contract
    good, q = contract.validate(clean, AS_OF)
    check("C1a", "Clean input passes the data contract", not q and len(good) == len(clean), f"{len(good)} rows, {len(q)} quarantined")
    good_d, q_d = contract.validate(dirty, AS_OF)
    reasons = sorted({x["reason"] for x in q_d})
    check("C1b", "Defective input is quarantined with reasons", len(q_d) >= 25 and "duplicate_key" in reasons and "negative_count" in reasons,
          f"{len(q_d)} of {len(dirty)} rows quarantined; reasons: {', '.join(reasons)}")

    for ver, fn in (("v1", v1), ("v2", v2)):
        s = fn(good, AS_OF)
        # C2 determinism and input-order independence
        shuffled = good[:]; random.Random(3).shuffle(shuffled)
        check(f"C2-{ver}", f"{ver}: same input, any row order, same output", digest(s) == digest(fn(good, AS_OF)) == digest(fn(shuffled, AS_OF)),
              f"output digest {digest(s)}")
        # C3 duplicates cannot change the score once the contract runs
        dup_good, _ = contract.validate(good + good[:50], AS_OF)
        check(f"C3-{ver}", f"{ver}: duplicated rows do not change scores", digest(fn(dup_good, AS_OF)) == digest(s), "50 duplicate rows added, then contract applied")
        # C4 monotonicity: more recent engagement never lowers a score
        viol = 0; tested = 0
        for cid in [k for k, v in s.items() if v is not None][:15]:
            bumped = [dict(r, engagements=r["engagements"] * 2) if r["creator_id"] == cid and
                      (AS_OF - dt.date.fromisoformat(r["date"])).days < 7 else r for r in good]
            tested += 1
            viol += fn(bumped, AS_OF)[cid] < s[cid]
        check(f"C4-{ver}", f"{ver}: doubling last-week engagement never lowers a score", viol == 0, f"{tested} creators tested, {viol} violations")
        # C5 bounds
        vals = [v for v in s.values() if v is not None]
        check(f"C5-{ver}", f"{ver}: scores finite and within 0-100", all(math.isfinite(v) and 0 <= v <= 100 for v in vals), f"min {min(vals):.2f}, max {max(vals):.2f}")
        # C6 cold start
        short = [k for k, v in s.items() if v is None]
        check(f"C6-{ver}", f"{ver}: creators with < {score.MIN_HISTORY_DAYS} days are not ranked", short == [f"creator-{i:03d}" for i in range(0, 40, 10)],
              f"unranked: {', '.join(short)}")
        if ver == "v1":
            s1 = s
        else:
            s2 = s

    # C7 golden fixtures (hand-computed for v1)
    g = v1(golden_rows(), AS_OF)
    want = {"g-up": round(100 / (1 + math.exp(-5)), 4), "g-flat": 50.0, "g-drop": round(100 / (1 + math.exp(5)), 4)}
    check("C7", "v1 matches hand-computed golden fixtures", g == want, json.dumps(g))

    # v2 independent oracle: flat 1% daily engagement, no follower growth.
    # rate=0.01; raw=0.7*ln(2); sigmoid((raw-1)*2) = 26.3162833541...
    flat = [dict(r, engagements=10) for r in golden_rows() if r["creator_id"] == "g-flat"]
    # For the up/drop fixtures, geometric weights give rates 1/60 and 1/300.
    # These constants were evaluated independently with 50-digit Decimal ln/exp.
    want_v2 = {"g-up": 34.8228, "g-flat": 26.3163, "g-drop": 16.8367}
    check("C7-v2", "v2 matches independent golden fixtures", v2(golden_rows(), AS_OF) == want_v2, str(v2(golden_rows(), AS_OF)))
    # Independently evaluated at 60-digit Decimal precision using weights 2**(-age/7).
    # Growth is +1 or -0.5; these fixtures exercise the previously uncovered 0.3 term.
    want_growth = {"f-up": 99.2795, "f-drop": 1.2433}
    got_growth = v2(follower_rows(), AS_OF)
    check("C13", "v2 follower-growth term matches independent oracles", got_growth == want_growth, str(got_growth))
    for ver, fn in (("v1", v1), ("v2", v2)):
        base = fn(flat, AS_OF)["g-flat"]
        bump = fn([dict(r, engagements=20) if (AS_OF-dt.date.fromisoformat(r["date"])).days < 7 else r for r in flat], AS_OF)["g-flat"]
        check("C9-"+ver, ver+": unsaturated fixture responds strictly to new engagement", base is not None and bump is not None and bump > base, f"{base} -> {bump}")
        stale = [dict(r, date=(dt.date.fromisoformat(r["date"])-dt.timedelta(days=90)).isoformat()) for r in flat]
        check("C10-"+ver, ver+": stale history is unranked", fn(stale, AS_OF) == {"g-flat": None}, str(fn(stale, AS_OF)))
        shuffled_dirty = dirty[:]; random.Random(13).shuffle(shuffled_dirty)
        accepted, _ = contract.validate(shuffled_dirty, AS_OF)
        check("C11-"+ver, ver+": dirty input order does not change accepted rows or scores", accepted == good_d and fn(accepted, AS_OF) == fn(good_d, AS_OF), "Full contract + scoring path")

    conflict_rows = golden_rows() + [dict(golden_rows()[0], engagements=123)]
    accepted, conflicts = contract.validate(conflict_rows, AS_OF)
    reversed_accepted, _ = contract.validate(list(reversed(conflict_rows)), AS_OF)
    check("C12", "Conflicting duplicates quarantine all rows for the key", accepted == reversed_accepted and sum(q["reason"] == "conflicting_duplicate" for q in conflicts) == 2, "Conflicting key excluded in either input order")
    # C8 version drift: illustrative threshold, not client-agreed; sign-off always needed.
    overlap = len(set(top(s1)) & set(top(s2)))
    rho = spearman(s1, s2)
    check("C8", "v1 -> v2 drift within illustrative threshold (top-10 overlap >= 6)", overlap >= 6,
          f"top-10 overlap {overlap}/10, tie-aware Spearman rho {rho if rho is not None else 'undefined'}. Product sign-off required before either version changes a real ranking, regardless of this advisory result.", blocking=False)
    return [dict(r) for r in results]


def report(rs):
    lines = ["# SAMPLE harness report (synthetic data)", "",
             f"Synthetic data as-of: {AS_OF.isoformat()}. Run UTC: {dt.datetime.now(dt.timezone.utc).isoformat()}. Python: {sys.version.split()[0]}.", "",
             "| Check | Result | Blocking | Detail |", "|---|---|---|---|"]
    for r in rs:
        lines.append(f"| {r['id']} {r['name']} | {'PASS' if r['ok'] else 'FAIL'} | {'yes' if r['blocking'] else 'advisory'} | {r['detail']} |")
    b = [r for r in rs if r["blocking"]]
    lines += ["", f"Blocking checks passed: {sum(r['ok'] for r in b)}/{len(b)}. Advisory checks failing: {sum(not r['ok'] for r in rs if not r['blocking'])}."]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    rs = run()
    text = report(rs)
    print(text)
    if "--report" in sys.argv:
        with open(sys.argv[sys.argv.index("--report") + 1], "w") as f:
            f.write(text)
    sys.exit(0 if all(r["ok"] for r in rs if r["blocking"]) else 1)
