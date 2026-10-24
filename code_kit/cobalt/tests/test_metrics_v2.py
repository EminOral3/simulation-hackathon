"""Pure recorded-data/unit tests. No simulation engine or LLM requests are executed."""
import copy
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path

import numpy as np

from code_kit.cobalt import config, metrics, metrics_v2, personas
from code_kit.cobalt import params as P
from code_kit.cobalt.package import validate_submission_runs
from code_kit.cobalt.recompute_metrics import recalculate, paired_deltas


class MetricsV2Tests(unittest.TestCase):
    def setUp(self):
        # the test fixtures are built from w4t_T25_lock: pin that as reference, independent of the default lock
        self.p = P.load(sets=["metrics.bootstrap_n=0", "metrics_v2.canonical_decisions=\"w4t/w4t_T25_lock\""])
        _, people, _ = personas.load_set(self.p, "manual40")
        self.people = copy.deepcopy(people)
        self.weekly = [
            {"persona": f["id"], "week": w, "status": "main bank", "money": "kept",
             "added_money": "none", "review_stars": 0, "cfpb": False, "parsed": True,
             "actions": [], "contacted_support": False}
            for f in self.people for w in range(1, 11)]
        self.run = {"company": "cobalt", "type": "plan", "seed": 1, "model": "recorded-model",
                    "decisions": config.load_decisions(self.p, "w4t/w4t_T25_lock")[0]}
        self.meta = {"status": "ok", "failed_parses": 0, "git": {"commit": "fixture"}}

    def evaluate(self, weekly=None, p=None):
        return metrics_v2.evaluate(p or self.p, self.people, weekly or self.weekly,
                                   run=self.run, meta=self.meta, bootstrap=False)

    def test_targets_and_budget_stay_fixed(self):
        r = self.evaluate()
        self.assertEqual(r["targets"], metrics_v2.TARGETS)
        self.assertAlmostEqual(r["goal_1"], 100)
        self.assertAlmostEqual(r["goal_2"], 100)
        self.assertEqual(r["budget"]["total_cost_usd"], 3_600_000)
        self.assertEqual(r["budget"]["remaining_budget_usd"], 400_000)
        self.assertTrue(r["budget"]["final_decision_count_valid"])

    def test_missing_duplicate_or_unparsed_records_are_invalid(self):
        for weekly in (self.weekly[:-1], self.weekly + [self.weekly[0]],
                       [{**self.weekly[0], "parsed": False}] + self.weekly[1:],
                       [{**self.weekly[0], "money": "unknown"}] + self.weekly[1:]):
            r = self.evaluate(weekly)
            self.assertFalse(r["validity"]["valid"])
            self.assertIsNone(r["goal_1"])
            self.assertIsNone(r["all_targets_met"])

    def test_28_day_proxy_does_not_erase_recent_status_on_closure(self):
        self.p["metrics"]["exit_conversion"] = 1.
        for r in self.weekly:
            r["status"] = "dormant"
        # One persona used an active relationship state in week 8 and closed in week 10.
        self.weekly[7]["status"] = "second bank"
        self.weekly[9]["status"] = "left"
        r = self.evaluate()
        expected = 100 * self.people[0]["w_active"] / sum(f["w_active"] for f in self.people)
        self.assertAlmostEqual(r["goal_1"], expected)
        self.assertEqual(r["active_proxy"]["relationship_preserving_28d_pct"], 0)
        self.assertEqual(r["active_proxy"]["window_days"], 28)
        self.assertFalse(r["active_proxy"]["observed_app_usage"])
        self.p["metrics_v2"]["exclude_closed"] = True
        self.assertEqual(self.evaluate()["goal_1"], 0)

    def test_activity_before_window_is_not_counted(self):
        self.p["metrics"]["exit_conversion"] = 1.
        for r in self.weekly:
            r["status"] = "dormant"
        self.weekly[5]["status"] = "main bank"  # week 6, outside weeks 7-10
        self.assertEqual(self.evaluate()["goal_1"], 0)

    def test_repeat_money_statements_are_not_summed(self):
        self.p["metrics"]["exit_conversion"] = 1.
        for r in self.weekly[:10]:
            r["money"] = "moved most"
        dep, dormant = metrics._deposit_weights(self.p, self.people)
        expected = 100 * (dep.sum() + dormant - .8 * dep[0]) / 6e9
        self.assertAlmostEqual(self.evaluate()["goal_2"], expected)
        self.assertIn("maximum", self.evaluate()["assumptions"]["goal_2"])

    def test_week_three_crisis_does_not_enter_reference(self):
        for r in self.weekly:
            if r["persona"] == self.people[0]["id"] and r["week"] in (3, 5, 6, 7, 8, 9, 10):
                r["review_stars"] = 1
        r = self.evaluate()
        self.assertEqual(r["assumptions"]["base_weeks"], [1, 2])
        self.assertLess(r["goal_3"], r["legacy_values"]["goal_3"])
        self.assertEqual(self.p["metrics"]["base_weeks"], [1, 3])  # input remains unchanged

    def test_sparse_cfpb_is_unknown_not_pass(self):
        r = self.evaluate()
        self.assertEqual(r["cfpb_evidence"]["raw_events"], 0)
        self.assertEqual(r["goal_3b"], 120)
        self.assertTrue(r["numeric_threshold_met"]["goal_3b"])
        self.assertIsNone(r["met"]["goal_3b"])
        self.assertIsNone(r["all_targets_met"])

    def test_known_failure_is_not_hidden_by_unknown_cfpb(self):
        self.p["metrics"]["exit_conversion"] = 1.
        for row in self.weekly:
            row["status"] = "left"
        r = self.evaluate()
        self.assertIsNone(r["met"]["goal_3b"])
        self.assertFalse(r["all_targets_met"])

    def test_sensitivity_groups_and_resampling_label(self):
        r = self.evaluate()
        self.assertEqual(set(r["sensitivity"]), {"0.69", "1.0"})
        self.assertEqual(len(r["groups"]), 5)
        self.assertIn("network dependence ignored", r["ci_method"])
        self.assertAlmostEqual(sum(g["ending_deposits_usd"] for g in r["groups"].values()), 6e9)

    def test_bootstrap_interval_matches_new_proxy(self):
        p = copy.deepcopy(self.p)
        p["metrics"]["bootstrap_n"] = 5
        r = metrics_v2.evaluate(p, self.people, self.weekly, run=self.run, meta=self.meta)
        np.testing.assert_allclose(r["goal_1_ci95"], [100, 100])

    def write_recorded_fixture(self, d):
        (d / "run.json").write_text(json.dumps(self.run))
        (d / "meta.json").write_text(json.dumps(self.meta))
        (d / "params.resolved.json").write_text(json.dumps(self.p))
        (d / "announcements.snapshot.json").write_text("[]")
        (d / "personas.jsonl").write_text("".join(json.dumps(f) + "\n" for f in self.people))
        (d / "weekly.jsonl").write_text("".join(json.dumps(r) + "\n" for r in self.weekly))
        (d / "metrics.json").write_text(json.dumps({"goal_1": 123}))

    def test_offline_recalculation_preserves_every_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.write_recorded_fixture(d)
            before = {f.name: hashlib.sha256(f.read_bytes()).hexdigest() for f in d.iterdir()}
            r = recalculate(d)
            self.assertEqual(r["original_saved_values"]["goal_1"], 123)
            for name, digest in before.items():
                self.assertEqual(hashlib.sha256((d / name).read_bytes()).hexdigest(), digest)
            self.assertTrue((d / "metrics_v2.json").exists())
            with self.assertRaises(FileExistsError):
                recalculate(d)

    def test_pairs_require_same_recorded_context(self):
        result = self.evaluate()
        sig = {"seed": 1, "model": "x", "source_commit": "c", "personas": "p",
               "announcements": "a", "metric_settings": "s", "v2_settings": "v"}
        result["comparison_signature"] = sig
        control = copy.deepcopy(result)
        control["source_run"]["type"] = "nodecision"
        pairs = paired_deltas([(Path("p"), result), (Path("c"), control)])
        self.assertEqual(len(pairs), 1)
        control["comparison_signature"]["model"] = "other"
        self.assertEqual(paired_deltas([(Path("p"), result), (Path("c"), control)]), [])

    def test_packaging_rejects_old_plan_instead_of_silently_using_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            wrong = copy.deepcopy(self.run)
            wrong["decisions"] = config.load_decisions(self.p, "plan")[0]  # old 2.1M plan
            (d / "run.json").write_text(json.dumps(wrong))
            with self.assertRaisesRegex(ValueError, "locked reference"):
                validate_submission_runs(self.p, {"plan_1": d}, "v2")

    def test_packaging_accepts_matching_reference_with_cfpb_warning(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            self.write_recorded_fixture(d)
            _, filters = config.load_decisions(self.p, "w4t/w4t_T25_lock")
            (d / "decisions.json").write_text(json.dumps({"decisions": self.run["decisions"], "filters": filters}))
            (d / "metrics_v2.json").write_text(json.dumps(self.evaluate()))
            log = io.StringIO()
            with contextlib.redirect_stdout(log):
                validate_submission_runs(self.p, {"plan_1": d}, "v2")
            self.assertIn("unmeasurable", log.getvalue())


if __name__ == "__main__":
    unittest.main()
