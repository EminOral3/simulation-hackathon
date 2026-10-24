"""Parameters: default.toml -> partial overlays (--params) -> single overrides (--set a.b=value).
Unknown keys and type mismatches raise, so a typo never falls back silently to a default.

    python -m code_kit.cobalt.params --show [--params x.toml] [--set network.feed_size=3]
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import tomllib
from pathlib import Path

PKG = Path(__file__).resolve().parent
ROOT = PKG.parents[1]
DEFAULT = PKG / "params" / "default.toml"


class ParamError(ValueError):
    pass


def _check_type(path: str, old, new):
    if isinstance(old, bool) or isinstance(new, bool):
        if not (isinstance(old, bool) and isinstance(new, bool)):
            raise ParamError(f"{path}: expected {type(old).__name__}, got {new!r}")
        return new
    if isinstance(old, float) and isinstance(new, int):
        return float(new)
    if isinstance(old, list) and isinstance(new, list):
        return new
    if type(old) is not type(new):
        raise ParamError(f"{path}: expected {type(old).__name__}, got {type(new).__name__} {new!r}")
    return new


def merge(base: dict, over: dict, prefix: str = "") -> dict:
    out = copy.deepcopy(base)
    for k, v in over.items():
        path = f"{prefix}{k}"
        if k not in out:
            raise ParamError(f"unknown parameter '{path}'")
        if isinstance(out[k], dict):
            if not isinstance(v, dict):
                raise ParamError(f"{path}: expected a table")
            out[k] = merge(out[k], v, path + ".")
        else:
            out[k] = _check_type(path, out[k], v)
    return out


def parse_set(item: str) -> dict:
    if "=" not in item:
        raise ParamError(f"--set needs key=value, got {item!r}")
    key, raw = item.split("=", 1)
    try:
        value = tomllib.loads(f"v = {raw}")["v"]
    except tomllib.TOMLDecodeError:
        value = raw  # bare string
    node: dict = {}
    cur = node
    parts = key.strip().split(".")
    for p in parts[:-1]:
        cur[p] = {}
        cur = cur[p]
    cur[parts[-1]] = value
    return node


def load(overlays: list[str] | None = None, sets: list[str] | None = None) -> dict:
    p = tomllib.loads(DEFAULT.read_text())
    for ov in overlays or []:
        path = Path(ov)
        if not path.is_absolute() and not path.exists():
            path = ROOT / ov
        p = merge(p, tomllib.loads(path.read_text()))
    for s in sets or []:
        p = merge(p, parse_set(s))
    return p


def path(p: dict, key: str) -> Path:
    v = Path(p["paths"][key])
    return v if v.is_absolute() else ROOT / v


def model_id(p: dict, which: str | None = None) -> str:
    w = which or p["llm"]["model"]
    if w == "experiment":
        return p["llm"]["model_experiment"]
    if w == "final":
        return p["llm"]["model_final"]
    return w


def digest(obj) -> str:
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=False).encode()).hexdigest()[:12]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", action="store_true")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    p = load(a.params, a.set)
    print(json.dumps(p, indent=2, ensure_ascii=False))
    print("hash", digest(p))


if __name__ == "__main__":
    main()
