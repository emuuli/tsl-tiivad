"""Run every fixture scenario and compare its output against expected.json.

Scope: execution only. Nothing here compiles, generates or rewrites anything --
it runs `compiled.py` against `student.py` and diffs the result. Every file it
touches inside the repo is read-only.

Each directory under `test/fixtures/` that holds a `compiled.py` is one
scenario:

    test/fixtures/<family>/<test_type>/<scenario>/
        student.py     the submission under test
        compiled.py    the Python emitted from tsl.json (prints Results JSON)
        expected.json  the Results JSON this scenario should produce
        tsl.json       the source envelope -- not read here

For each scenario: `student.py` + `compiled.py` are copied into a fresh temp
dir, `compiled.py` runs in a subprocess, its printed JSON is normalised and
compared to `expected.json`. The subprocess matters -- tiivad's `Results` is a
class-level singleton, so in-process runs would leak state between scenarios.

Usage:

    python test/test_all.py               # everything
    python test/test_all.py -k calls      # only ids containing "calls"
    python test/test_all.py -j 1          # serial, easier to read
    pytest test/test_all.py               # same scenarios, one item each

Exit code is 0 when everything matches, 1 otherwise.
"""

from __future__ import annotations

import argparse
import copy
import json
import os
import shutil
import subprocess
import sys
import tempfile
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Optional

FIXTURES_ROOT = Path(__file__).resolve().parent / "fixtures"
PY = sys.executable
TIMEOUT_S = 20


# --------------------------------------------------------------------------
# Discovery
# --------------------------------------------------------------------------


def scenario_id(scenario_dir: Path) -> str:
    """`calls_consolidated/class_calls_class/fail` -- stable across platforms."""
    return scenario_dir.relative_to(FIXTURES_ROOT).as_posix()


def scenario_dirs(pattern: Optional[str] = None) -> list[Path]:
    """Every directory holding a `compiled.py`, optionally substring-filtered."""
    if not FIXTURES_ROOT.exists():
        return []
    found = sorted(p.parent for p in FIXTURES_ROOT.rglob("compiled.py"))
    if pattern:
        found = [d for d in found if pattern.lower() in scenario_id(d).lower()]
    return found


# --------------------------------------------------------------------------
# Normalisation
# --------------------------------------------------------------------------
# Fields that change on every run are replaced with placeholders, so that a
# plain equality check stays meaningful. Everything else -- status, points,
# checks, title, feedback, ordering -- is compared verbatim.


def normalise(payload: dict, tmp_path: Path) -> dict:
    """Return a deep copy with run-specific values scrubbed out."""
    out = copy.deepcopy(payload)

    # Pinned to the installed tiivad version; changes on every release.
    if "producer" in out:
        out["producer"] = "<producer>"
    # Wall-clock UTC.
    if "finished_at" in out:
        out["finished_at"] = "<finished_at>"

    for test in out.get("tests") or []:
        message = test.get("exception_message")
        if message:
            # Paths and line numbers churn every run; keep the last salient line.
            test["exception_message"] = _scrub_paths(_last_line(message), tmp_path)
        for check in test.get("checks") or []:
            for key in ("title", "feedback"):
                if key in check:
                    check[key] = _scrub_paths(check[key], tmp_path)

    return out


def _last_line(s: str) -> str:
    if not isinstance(s, str) or "\n" not in s:
        return s
    lines = [ln for ln in s.splitlines() if ln.strip()]
    return lines[-1] if lines else s


def _scrub_paths(s: str, tmp_path: Path) -> str:
    """The per-scenario temp dir leaks into feedback strings; mask it."""
    if not isinstance(s, str):
        return s
    tmp = str(tmp_path)
    return s.replace(tmp, "<tmp>").replace(tmp.replace("\\", "/"), "<tmp>")


# --------------------------------------------------------------------------
# Execution
# --------------------------------------------------------------------------


def run_compiled(scenario_dir: Path, work_dir: Path) -> dict:
    """Copy the scenario into `work_dir`, run `compiled.py`, return its JSON."""
    for name in ("student.py", "compiled.py"):
        source = scenario_dir / name
        if not source.exists():
            raise AssertionError(f"scenario is missing {name}")
        shutil.copy2(source, work_dir / name)

    # Pin the child's stdout encoding. Otherwise the feedback strings come back
    # through the ambient console codepage (cp1257 on Windows) and every
    # Estonian letter is mangled into U+FFFD, producing bogus diffs.
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"

    proc = subprocess.run(
        [PY, "compiled.py"],
        cwd=str(work_dir),
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=TIMEOUT_S,
    )
    if proc.returncode != 0:
        raise AssertionError(
            f"compiled.py exited with {proc.returncode}\n"
            f"stderr:\n{proc.stderr}\nstdout:\n{proc.stdout}"
        )
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"compiled.py did not print valid JSON ({exc})\nstdout:\n{proc.stdout}"
        ) from exc


def check_scenario(scenario_dir: Path, work_dir: Path) -> list[str]:
    """Run one scenario. Returns [] when it matches, else difference lines."""
    expected_path = scenario_dir / "expected.json"
    if not expected_path.exists():
        return ["expected.json is missing"]

    actual = normalise(run_compiled(scenario_dir, work_dir), work_dir)
    expected = normalise(
        json.loads(expected_path.read_text(encoding="utf-8")), work_dir
    )
    return diff_json(actual, expected)


def diff_json(actual: Any, expected: Any, path: str = "$") -> list[str]:
    """Recursively describe how `actual` differs from `expected`."""
    if isinstance(expected, dict) and isinstance(actual, dict):
        lines: list[str] = []
        for key in sorted(set(expected) | set(actual)):
            here = f"{path}.{key}"
            if key not in actual:
                lines.append(f"{here}: missing (expected {expected[key]!r})")
            elif key not in expected:
                lines.append(f"{here}: unexpected (actual {actual[key]!r})")
            else:
                lines.extend(diff_json(actual[key], expected[key], here))
        return lines

    if isinstance(expected, list) and isinstance(actual, list):
        lines = []
        if len(actual) != len(expected):
            lines.append(f"{path}: length {len(actual)} != expected {len(expected)}")
        for i in range(min(len(actual), len(expected))):
            lines.extend(diff_json(actual[i], expected[i], f"{path}[{i}]"))
        return lines

    if actual != expected:
        return [f"{path}:\n    expected: {expected!r}\n    actual:   {actual!r}"]
    return []


# --------------------------------------------------------------------------
# pytest entry point -- one item per scenario
# --------------------------------------------------------------------------

try:
    import pytest
except ModuleNotFoundError:  # standalone use without pytest installed
    pytest = None  # type: ignore[assignment]

if pytest is not None:

    @pytest.mark.parametrize("scenario_dir", scenario_dirs(), ids=scenario_id)
    def test_scenario(scenario_dir: Path, tmp_path: Path) -> None:
        differences = check_scenario(scenario_dir, tmp_path)
        if differences:
            pytest.fail("\n".join(differences), pytrace=False)


# --------------------------------------------------------------------------
# Standalone entry point
# --------------------------------------------------------------------------


def _run_one(scenario_dir: Path) -> tuple[Path, list[str]]:
    work_dir = Path(tempfile.mkdtemp(prefix="tiivad-fx-"))
    try:
        return scenario_dir, check_scenario(scenario_dir, work_dir)
    except Exception as exc:  # a crashed scenario is a failed scenario
        return scenario_dir, [f"{type(exc).__name__}: {exc}"]
    finally:
        shutil.rmtree(work_dir, ignore_errors=True)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "-k",
        dest="pattern",
        metavar="SUBSTRING",
        help="only run scenarios whose id contains SUBSTRING",
    )
    parser.add_argument(
        "-j",
        "--jobs",
        type=int,
        default=min(8, os.cpu_count() or 4),
        help="parallel subprocesses (default: %(default)s, 1 for serial)",
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true", help="only report failures"
    )
    args = parser.parse_args(argv)

    # Feedback strings are Estonian; don't let a cp1257 console kill the report.
    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(encoding="utf-8", errors="replace")

    scenarios = scenario_dirs(args.pattern)
    if not scenarios:
        where = f" matching {args.pattern!r}" if args.pattern else ""
        print(f"No scenarios found{where} under {FIXTURES_ROOT}", file=sys.stderr)
        return 1

    jobs = max(1, args.jobs)
    print(f"Running {len(scenarios)} scenario(s) with {jobs} job(s)\n")

    with ThreadPoolExecutor(max_workers=jobs) as pool:
        results = list(pool.map(_run_one, scenarios))

    failures = [(d, diffs) for d, diffs in results if diffs]

    if not args.quiet:
        for scenario_dir, differences in results:
            if not differences:
                print(f"  ok    {scenario_id(scenario_dir)}")

    for scenario_dir, differences in failures:
        print(f"\nFAIL  {scenario_id(scenario_dir)}")
        for line in differences:
            print(f"    {line}")

    _print_family_summary(results)

    passed = len(results) - len(failures)
    print(f"\n{passed}/{len(results)} passed, {len(failures)} failed.")
    return 1 if failures else 0


def _print_family_summary(results: list[tuple[Path, list[str]]]) -> None:
    tally: dict[str, list[int]] = {}
    for scenario_dir, differences in results:
        family = scenario_id(scenario_dir).split("/", 1)[0]
        row = tally.setdefault(family, [0, 0])
        row[1 if differences else 0] += 1

    width = max((len(f) for f in tally), default=0)
    print("\nPer family:")
    for family in sorted(tally):
        passed, failed = tally[family]
        flag = "OK  " if not failed else "FAIL"
        print(f"  {flag}  {family:<{width}}  {passed} passed, {failed} failed")


if __name__ == "__main__":
    sys.exit(main())
