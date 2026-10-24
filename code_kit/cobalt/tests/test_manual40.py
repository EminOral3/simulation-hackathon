"""Static/offline integration checks only: no mock simulation and no API calls."""
import copy
import hashlib
import json
from collections import Counter

import math
import unittest

from code_kit.cobalt import agent, metrics, personas
from code_kit.cobalt import params as P
from code_kit.cobalt.manual40 import adapt


def test_default_selection_excludes_reference_panel():
    p = P.load()
    assert p["personas"]["persona_set"] == "latest"
    d = personas.resolve_set(p)
    assert d.parent == P.path(p, "personas_dir")
    assert d != personas.resolve_set(p, "manual40")
    assert len(personas.load_set(p, "manual40")[1]) == 40


def test_original_source_and_runtime_narratives_are_preserved():
    p = P.load()
    d, people, calls = personas.load_set(p, "manual40")
    source = json.loads((d / "source.json").read_text(encoding="utf-8"))
    original = {f["id"]: f for f in source["personas"]}
    assert calls == []
    assert Counter(f["group"] for f in people) == Counter({g: 8 for g in original_group_names(original)})
    assert len({f["id"] for f in people}) == 40
    for f in people:
        assert f["reference_source"] == original[f["id"]]
        assert f["narrative"] == original[f["id"]]["narrative"]
        assert f["provenance"]["human_reviewed"] is False


def original_group_names(original):
    return {f["group"] for f in original.values()}


def test_adapter_does_not_mutate_source_and_is_deterministic():
    p = P.load()
    d = personas.resolve_set(p, "manual40")
    source = json.loads((d / "source.json").read_text(encoding="utf-8"))
    before = copy.deepcopy(source)
    assert adapt(source, p) == adapt(source, p)
    assert source == before


def test_engine_fields_weights_and_prompt_compatibility():
    p = P.load()
    _, people, _ = personas.load_set(p, "manual40")
    assert math.isclose(sum(f["weight_customers"] for f in people), 2_100_000)
    assert math.isclose(sum(f["w_active"] for f in people), 999492)
    dep, dormant = metrics._deposit_weights(p, people)
    assert math.isclose(dep.sum() + dormant, 6_000_000_000)
    names = {f["id"]: f["name"] for f in people}
    for f in people:
        assert f["switch_cost"] and f["design_levels"]
        block = agent.persona_block(f, f["ties"], names)
        assert f["narrative"] in block
        assert f["location"] in block
        if f["paycheck_into_cobalt"] == "no":
            assert f["payday"] == "not paid into Cobalt"


def test_network_is_self_contained_and_production_files_stay_identical():
    p = P.load()
    production = P.path(p, "personas_dir")
    before = {str(f): hashlib.sha256(f.read_bytes()).hexdigest()
              for f in production.rglob("*") if f.is_file()}
    _, people, _ = personas.load_set(p, "manual40")
    by_id = {f["id"]: f for f in people}
    for f in people:
        assert f["ties"]
        for tie in f["ties"]:
            assert tie["id"] in by_id and tie["id"] != f["id"]
            assert any(back["id"] == f["id"] for back in by_id[tie["id"]]["ties"])
    after = {str(f): hashlib.sha256(f.read_bytes()).hexdigest()
             for f in production.rglob("*") if f.is_file()}
    assert before == after


def test_overlay_and_comparison_spec_are_opt_in():
    import tomllib
    p = P.load(["code_kit/cobalt/params/personas/manual40.toml"])
    assert p["personas"]["persona_set"] == "manual40"
    assert p["paths"]["outputs"].endswith("/manual40")
    spec = tomllib.loads((P.PKG / "params/experiments/manual40_compare.toml").read_text())
    assert len(spec["variant"]) == 4
    assert {v["persona_set"] for v in spec["variant"]} == {"manual40", "20261024-123642_v2"}
    assert P.load()["personas"]["persona_set"] == "latest"


def load_tests(loader, tests, pattern):
    """Also run with stdlib unittest when pytest is not installed."""
    return unittest.TestSuite(unittest.FunctionTestCase(fn) for name, fn in globals().items()
                              if name.startswith("test_") and callable(fn))


if __name__ == "__main__":
    unittest.main()
