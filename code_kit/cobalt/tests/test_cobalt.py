"""Offline tests (mock LLM, no API). Run: .venv/bin/python -m pytest -q code_kit/cobalt/tests"""
import asyncio
import copy
import json

import pytest

from code_kit.cobalt import config, crisis, metrics, personas, support_queue
from code_kit.cobalt import params as P
from code_kit.cobalt.llm import LLM
from code_kit.cobalt.run import run_one


@pytest.fixture(scope="module")
def p(tmp_path_factory):
    out = tmp_path_factory.mktemp("out")
    return P.load(sets=[f'paths.outputs="{out}"', f'paths.personas_dir="{out}/personas"',
                        'paths.announcements="code_kit/cobalt/tests/announcements_test.json"'])


def plan(p):
    return config.load_decisions(p, "plan")[0]


def test_unknown_param_and_type_rejected():
    with pytest.raises(P.ParamError):
        P.load(sets=["netwrk.feed_size=3"])
    with pytest.raises(P.ParamError):
        P.load(sets=["network.feed_size=true"])
    assert P.load(sets=["metrics.k_rating=1"])["metrics"]["k_rating"] == 1.0


def test_budget_and_menu(p):
    d = plan(p)
    assert config.budget_check(p, d)["total_usd"] == 2_100_000
    bad = copy.deepcopy(d)
    bad[1]["actions"] = [{"action": "Debit card cash back for 4 weeks", "level": "2%, up to $10"},
                         {"action": "Savings rate boost for 4 weeks, balances up to $50,000", "level": "+0.75 points"}]
    with pytest.raises(config.DecisionError):
        config.budget_check(p, bad)  # 1.3M + 2.2M + 2.4M > 4M
    bad = copy.deepcopy(d)
    bad[0]["actions"][0]["level"] = "+1 point"
    with pytest.raises(config.DecisionError):
        config.budget_check(p, bad)
    bad = copy.deepcopy(d)
    bad[0]["message"] = "x" * 601
    with pytest.raises(config.DecisionError):
        config.budget_check(p, bad)


def test_classify_migration(p):
    assert "A01_migration_overrun" in crisis.classify(p, "The switch is still read-only and may run hours longer")


def test_weights_reconcile(p):
    people = personas.build_fields(p)
    assert len(people) == 75
    assert abs(sum(f["weight_customers"] for f in people) - 2_100_000) < 10
    assert abs(sum(f["w_active"] for f in people) - 1_000_000) < 2_000
    dep, dormant = metrics._deposit_weights(p, people)
    assert abs(dep.sum() + dormant - 6.0e9) < 1e3


def test_queue_calibrated():
    cfg = P.load()["support"]
    assert abs(support_queue.week_wait(cfg, cfg["base_contact_share"], 0)["wait_min"] - cfg["target_wait_min"]) < 0.2
    assert support_queue.week_wait(cfg, 0.1, 150)["wait_min"] < support_queue.week_wait(cfg, 0.1, 0)["wait_min"]


def test_full_mock_run_never_overwrites(p):
    asyncio.run(personas.build_set(p, live=False, label="t"))
    llm = LLM(p, live=False)
    a = asyncio.run(run_one(p, llm, run_type="plan", seed=1, decisions_file="plan", quiet=True))
    b = asyncio.run(run_one(p, llm, run_type="plan", seed=1, decisions_file="plan", quiet=True))
    assert a != b and a.exists() and b.exists()
    before = (a / "weekly.jsonl").read_bytes()
    nd = asyncio.run(run_one(p, llm, run_type="nodecision", seed=1, decisions_file=None, quiet=True))
    assert (a / "weekly.jsonl").read_bytes() == before
    # decision message reaches personas word for word, never in nodecision, never before its week
    msg = plan(p)[0]["message"]
    calls = [json.loads(l) for l in (a / "calls.jsonl").read_text().splitlines()]
    assert any(msg in c["prompt"] for c in calls if c["week"] >= 5)
    assert not any(msg in c["prompt"] for c in calls if 1 <= c["week"] < 5)
    ncalls = [json.loads(l) for l in (nd / "calls.jsonl").read_text().splitlines()]
    assert not any(msg in c["prompt"] for c in ncalls)
    # analyst-only calibration anchors never reach a persona
    assert not any("TSB" in c["prompt"] or "SVB" in c["prompt"] for c in calls)
    m = json.loads((a / "metrics.json").read_text())
    assert all(isinstance(m[k], float) for k in ("goal_1", "goal_2", "goal_3", "goal_3b"))
    idx = (P.path(p, "outputs") / "index.csv").read_text().splitlines()
    assert len(idx) == 4  # header + 3 runs


def test_network_switch_removes_other_personas_text(p):
    q = P.merge(p, {"network": {"enabled_ties": False, "enabled_feed": False}})
    llm = LLM(q, live=False)
    d = asyncio.run(run_one(q, llm, run_type="plan", seed=3, decisions_file="plan", quiet=True, weeks=7, probe=False))
    inter = (d / "interactions.jsonl").read_text().strip()
    assert inter == ""
