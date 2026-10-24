"""Build the hand-in by COPYING chosen runs into outputs/submissions/<timestamp>_<team>/ (originals untouched),
add code + docs, scan for the key, run check.py on the folder and on the ZIP.

    python -m code_kit.cobalt.package --auto --model gemini-3.7-flash
    python -m code_kit.cobalt.package --plan_1 <run_dir> --plan_2 ... --nodecision_1 ... --nodecision_2 ... --plan_nosurprises ...
"""
from __future__ import annotations

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from . import params as P
from .llm import load_env

SLOTS = {"plan_1": ("plan", 1), "plan_2": ("plan", 2), "nodecision_1": ("nodecision", 1),
         "nodecision_2": ("nodecision", 2), "plan_nosurprises": ("plan_nosurprises", None)}
RUN_FILES = ["run.json", "personas.jsonl", "calls.jsonl", "weekly.jsonl", "metrics.json", "probe.jsonl",
             "interactions.jsonl", "queue.jsonl", "meta.json", "params.resolved.json", "announcements.snapshot.json"]


def auto_pick(p: dict, model: str | None) -> dict:
    rows = list(csv.DictReader((P.path(p, "outputs") / "index.csv").open()))
    rows = [r for r in rows if r["status"] == "ok" and (not model or model in r["model"])]
    picked = {}
    for slot, (typ, seed) in SLOTS.items():
        cand = [r for r in rows if r["type"] == typ and (seed is None or int(r["seed"]) == seed)]
        if slot in ("plan_1", "nodecision_1"):  # probe runs need probe.jsonl
            cand = [r for r in cand if (P.path(p, "outputs") / "runs" / r["folder"] / "probe.jsonl").exists()]
        if not cand:
            raise SystemExit(f"no finished run for {slot} (type {typ}, seed {seed}, model {model})")
        picked[slot] = P.path(p, "outputs") / "runs" / cand[-1]["folder"]
    return picked


def copy_code(dst: Path, p: dict):
    pkg = P.PKG
    ignore = shutil.ignore_patterns("outputs", "__pycache__", "*.pyc", "*_mock", ".pytest_cache")
    shutil.copytree(pkg, dst / "code_kit" / "cobalt", ignore=ignore)
    for f in ("sim_core.py", "validation.py"):
        shutil.copy2(pkg.parent / f, dst / "code_kit" / f)
    shutil.copytree(P.path(p, "talp_db") / "data", dst / "docs" / "talp_db" / "data")
    (dst / "README.md").write_text(
        "Cobalt Bank persona simulation. From this folder:\n\n"
        "    pip install google-genai pydantic numpy scipy\n"
        "    export TALP_KEY=...\n"
        "    python -m code_kit.cobalt.personas build --live --label v1\n"
        "    python -m code_kit.cobalt.run --type plan --seed 1 --decisions plan --live --model final\n\n"
        "Parameters: code_kit/cobalt/params/default.toml (override with --params / --set).\n")


def scan_key(root: Path) -> list[str]:
    load_env()
    keys = [k for k in (os.environ.get("TALP_KEY"), os.environ.get("VERTEX_AI_KEY"), os.environ.get("OPENAI_KEY")) if k]
    bad = []
    for f in root.rglob("*"):
        if f.is_file():
            b = f.read_bytes()
            if re.search(rb"AQ\.[A-Za-z0-9_-]{40}", b) or any(k.encode() in b for k in keys):
                bad.append(str(f.relative_to(root)))
    return bad


def main():
    ap = argparse.ArgumentParser()
    for s in SLOTS:
        ap.add_argument(f"--{s}")
    ap.add_argument("--auto", action="store_true", help="latest finished run per slot from outputs/index.csv")
    ap.add_argument("--model", help="with --auto: substring the run's model must contain")
    ap.add_argument("--params", action="append", default=[])
    ap.add_argument("--set", action="append", default=[])
    a = ap.parse_args()
    p = P.load(a.params, a.set)
    picked = auto_pick(p, a.model) if a.auto else {}
    for s in SLOTS:
        if getattr(a, s):
            picked[s] = Path(getattr(a, s))
    missing = [s for s in SLOTS if s not in picked]
    if missing:
        raise SystemExit(f"missing runs for: {missing}")
    team = p["run"]["team"]
    root = P.path(p, "outputs") / "submissions" / f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_{team}"
    sub = root / "submission"
    sub.mkdir(parents=True, exist_ok=False)
    for slot, src in picked.items():
        d = sub / "runs" / slot
        d.mkdir(parents=True)
        for f in RUN_FILES:
            if (src / f).exists():
                shutil.copy2(src / f, d / f)
        (d / "SOURCE.txt").write_text(f"{src.name}\n")
        print(f"{slot:17s} <- {src.name}")
    for key, name in (("client_memo", "CLIENT_MEMO.md"), ("team_doc", "TEAM_DOC.md")):
        src = P.path(p, key)
        if src.exists():
            shutil.copy2(src, sub / name)
        else:
            print(f"WARNING: {src} missing; {name} not included")
    copy_code(sub / "code", p)
    bad = scan_key(sub)
    if bad:
        raise SystemExit(f"KEY FOUND in {bad}; aborting")
    check = P.path(p, "check_py")
    subprocess.run([sys.executable, str(check), str(sub)])
    zp = root / f"{team}_submission.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(sub.rglob("*")):
            if f.is_file():
                z.write(f, f.relative_to(sub).as_posix())
    r = subprocess.run([sys.executable, str(check), str(zp)], capture_output=True, text=True)
    print(r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr)
    print(zp)


if __name__ == "__main__":
    main()
