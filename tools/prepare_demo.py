"""Prepare two explicitly mock runs; optionally launch the offline web demo.

    python -X utf8 tools/prepare_demo.py --serve
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--serve", action="store_true", help="open the local offline demo server")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    # Keep demo output and its index separate from the archived hackathon experiments.
    output = ROOT / "code_kit/cobalt/outputs/demo"
    output.mkdir(parents=True, exist_ok=True)
    locked = json.loads((ROOT / "team-04_decisions.json").read_text(encoding="utf-8"))
    decisions = output / "hackathon_decisions.json"
    decisions.write_text(json.dumps({"decisions": locked["run_decisions"], "filters": {}},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
    runs = []
    for kind in ("plan", "nodecision"):
        command = [sys.executable, "-X", "utf8", "-m", "code_kit.cobalt.run",
                   "--type", kind, "--seed", "1", "--weeks", "10", "--no-probe",
                   "--persona-set", "20261024-123642_v2",
                   "--decisions", str(decisions), "--label", "offline_demo",
                   "--set", f'paths.outputs={json.dumps(output.as_posix())}',
                   "--set", 'llm.provider="mock"']
        result = subprocess.run(command, cwd=ROOT, check=True, capture_output=True,
                                text=True, encoding="utf-8")
        print(result.stdout, end="")
        run = Path(result.stdout.strip().splitlines()[-1])
        if not (run / "weekly.jsonl").is_file():
            raise RuntimeError(f"Missing simulation output: {run}")
        runs.append(run)

    command = [sys.executable, "-X", "utf8", "tools/demo_ui.py", "--run", str(runs[0]),
               "--other", str(runs[1]), "--offline", "--port", str(args.port)]
    print("\nMOCK DEMO: synthetic offline output, not the recorded hackathon results.", flush=True)
    print(subprocess.list2cmdline(command), flush=True)
    if args.serve:
        try:
            subprocess.run(command, cwd=ROOT, check=True)
        except KeyboardInterrupt:
            pass


if __name__ == "__main__":
    main()
