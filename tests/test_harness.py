import datetime as dt, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import harness
from momentum import contract, generate, score

class HarnessTests(unittest.TestCase):
    def test_all_blocking_reference_checks(self):
        rs=harness.run()
        self.assertTrue(all(r['ok'] for r in rs if r['blocking']))
        self.assertEqual(len(harness.run()),len(rs))

    def test_contract_defect_reasons(self):
        _, q=contract.validate(generate.inject_defects(generate.clean_rows()),harness.AS_OF)
        self.assertTrue({'duplicate_key','negative_count','null:followers','bad_date','future_date','type:views'} <= {x['reason'] for x in q})

    def test_conflicting_duplicates_are_order_independent(self):
        rows=harness.golden_rows()
        conflict=dict(rows[0],engagements=123)
        a,q=contract.validate(rows+[conflict],harness.AS_OF)
        b,r=contract.validate(list(reversed(rows+[conflict])),harness.AS_OF)
        self.assertEqual(a,b)
        self.assertEqual(sum(x['reason']=='conflicting_duplicate' for x in q),2)
        for fn in (score.score_v1,score.score_v2):
            self.assertEqual(fn(a,harness.AS_OF),fn(b,harness.AS_OF))
            self.assertIsNone(fn(a,harness.AS_OF)['g-up'])

    def test_nonmapping_rows_quarantine(self):
        good,q=contract.validate([None,[],7,'bad',{}],harness.AS_OF)
        self.assertFalse(good)
        self.assertEqual(len(q),5)

    def test_stale_sparse_and_empty(self):
        rows=harness.golden_rows()
        stale=[dict(r,date=(dt.date.fromisoformat(r['date'])-dt.timedelta(days=90)).isoformat()) for r in rows]
        for fn in (score.score_v1,score.score_v2):
            self.assertEqual(fn([],harness.AS_OF),{})
            self.assertTrue(all(v is None for v in fn(stale,harness.AS_OF).values()))
            self.assertIsNone(fn(rows[1:],harness.AS_OF)['g-up'])

    def test_harness_rejects_constant_v2_mutant(self):
        def constant(rows, as_of):
            return {k:50.0 if v is not None else None for k,v in score.score_v1(rows,as_of).items()}
        rs=harness.run(v2=constant)
        failed={r['id'] for r in rs if r['blocking'] and not r['ok']}
        self.assertTrue({'C7-v2','C9-v2'} <= failed)

    def test_harness_rejects_wrong_v1_formula(self):
        def wrong(rows,as_of):
            return {k:None if v is None else 100-v for k,v in score.score_v1(rows,as_of).items()}
        self.assertTrue(any(r['blocking'] and not r['ok'] for r in harness.run(v1=wrong)))

    def test_tie_aware_spearman_and_degenerate_cases(self):
        self.assertAlmostEqual(harness.spearman({'a':1,'b':1,'c':2},{'a':1,'b':2,'c':3}),0.8660254037844386)
        self.assertEqual(harness.spearman({'a':1,'b':2},{'a':2,'b':1}),-1)
        self.assertIsNone(harness.spearman({},{}))
        self.assertIsNone(harness.spearman({'a':1},{'a':2}))
        self.assertIsNone(harness.spearman({'a':1,'b':1},{'a':1,'b':2}))

    def test_half_life_validation(self):
        for h in (0,-1,float('nan'),float('inf'),True,'7'):
            with self.assertRaises(ValueError):
                score.score_v2(harness.golden_rows(),harness.AS_OF,h)

    def test_earliest_and_latest_calendar_boundaries(self):
        row = {"creator_id":"edge", "followers":1000, "views":100, "engagements":10}
        for cutoff in (dt.date.min,dt.date.max):
            good,q = contract.validate([dict(row,date=cutoff.isoformat())],cutoff)
            self.assertFalse(q)
            for fn in (score.score_v1,score.score_v2):
                self.assertEqual(fn(good,cutoff),{"edge":None})
        rows = [dict(row,date=dt.date(1,1,day).isoformat()) for day in range(1,15)]
        for day in range(1,14):
            cutoff = dt.date(1,1,day)
            good,q = contract.validate(rows[:day],cutoff)
            self.assertFalse(q)
            for fn in (score.score_v1,score.score_v2):
                self.assertEqual(fn(good,cutoff),{"edge":None})
        self.assertEqual(score.score_v1(rows,dt.date(1,1,14)),{"edge":50.0})
        self.assertEqual(score.score_v2(rows,dt.date(1,1,14)),{"edge":26.3163})

    def test_harness_blocks_dropped_follower_growth_term(self):
        import ast,inspect
        tree = ast.parse(inspect.getsource(score.score_v2))
        changed = 0
        for node in ast.walk(tree):
            if isinstance(node,ast.Constant) and node.value == 0.3:
                node.value = 0.0
                changed += 1
        self.assertEqual(changed,1,"Mutation must change exactly the growth coefficient")
        namespace = dict(vars(score))
        exec(compile(tree,'<dropped-growth-mutant>','exec'),namespace)
        results = harness.run(v2=namespace['score_v2'])
        self.assertTrue(any(r['id']=='C13' and r['blocking'] and not r['ok'] for r in results))

    def test_counter_and_id_boundaries(self):
        row=harness.golden_rows()[0]
        for bad in (dict(row,followers=True),dict(row,followers=10**12+1),dict(row,creator_id=' '),dict(row,date='20260811')):
            good,q=contract.validate([bad],harness.AS_OF)
            self.assertFalse(good)
            self.assertEqual(len(q),1)

if __name__=='__main__':
    unittest.main()
