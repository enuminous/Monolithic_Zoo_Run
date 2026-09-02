from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hummingbird import HummingbirdMonitor, Observation, freeze_protocol
from hummingbird.hashing import GENESIS_HASH, chain_digest, sha256_json


ROSTER = [
    (1, "Tortoise"), (2, "Owl"), (3, "Octopus"), (4, "Gecko"),
    (5, "Hive"), (6, "Eagle"), (7, "Crab"), (8, "Shepherd"),
    (9, "Pulse"), (10, "Cat"), (11, "Fox"), (12, "Spider"),
    (13, "Raven"), (14, "Dolphin"), (15, "Ant"), (16, "Moth"),
    (17, "Shark"), (18, "Penguin"), (19, "Bat"), (20, "Hedgehog"),
    (21, "Crocodile"), (22, "Dragon"), (23, "Turtle"), (24, "Magpie"),
    (25, "Wolf"), (26, "Elephant"), (27, "Chameleon"), (28, "Jellyfish"),
    (29, "Beaver"), (30, "Mantis"), (31, "Bison"), (32, "Weasel"),
    (33, "Salmon"), (34, "Orca"), (35, "Mole"), (36, "Lynx"),
    (37, "Horse"), (38, "Termite"), (39, "Phoenix"), (40, "Cobra"),
    (41, "Whale"), (42, "Falcon"), (43, "Rhino"), (44, "Bonobo"),
    (45, "Axolotl"), (46, "Butterfly"),
]

REQUIRED = ("README", "LICENSE", "CITATION", "IMPLEMENTATION", "TEST", "TESTS_PASS")
OPTIONAL = ("LIMITATIONS_OR_FALSIFICATION", "BENCHMARK", "ABLATION", "FREEZE_OR_MANIFEST", "CI")
AUDIT_PROTOCOL = {
    "audit_id": "ZOOWIDE-001",
    "designation": "HUMMINGBIRD-ZOO-FLIGHT",
    "zoo_boundary": "Core Zoo v1.0: Animals #1-46; #47+ prospective",
    "owner": "enuminous",
    "roster": [{"number": number, "repository": name} for number, name in ROSTER],
    "required_evidence": list(REQUIRED),
    "optional_reproducibility_evidence": list(OPTIONAL),
    "classification": {
        "GREEN": "all frozen checks present and tests pass",
        "AMBER": "core passes; one or more optional reproducibility surfaces absent",
        "RED": "one or more frozen core checks absent or tests do not pass",
        "BLACK": "repository unavailable or evidence uninterpretable",
    },
    "first_flight_boundary": (
        "This run initializes exact commit baselines. It cannot establish whether historical "
        "states predating the run were unchanged."
    ),
}
AUDIT_PROTOCOL_HASH = sha256_json(AUDIT_PROTOCOL)


def run(command: list[str], cwd: Path | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        timeout=timeout,
        check=False,
        env={
            **os.environ,
            "PATH": str(Path(sys.executable).parent) + ":/usr/local/bin:/usr/bin:/bin",
        },
    )


def has_named(files: list[str], names: set[str]) -> bool:
    return any(Path(path).name.lower() in names for path in files)


def has_fragment(files: list[str], fragments: tuple[str, ...]) -> bool:
    return any(any(fragment in path.lower() for fragment in fragments) for path in files)


def inspect_repository(number: int, name: str, clone_root: Path, test_timeout: int) -> dict:
    started = time.perf_counter()
    target = clone_root / f"{number:02d}-{name}"
    url = f"https://github.com/enuminous/{name}.git"
    result = {
        "number": number,
        "animal": name.upper(),
        "repository": f"enuminous/{name}",
        "url": url[:-4],
    }
    try:
        clone = run(
            ["git", "clone", "--depth", "1", "--no-tags", "--single-branch", url, str(target)],
            timeout=test_timeout,
        )
        if clone.returncode != 0:
            result.update({
                "retrieval": "FAILED",
                "state": "BLACK",
                "error": clone.stdout[-2000:],
                "elapsed_seconds": time.perf_counter() - started,
            })
            return result

        head = run(["git", "rev-parse", "HEAD"], target).stdout.strip()
        tree = run(["git", "rev-parse", "HEAD^{tree}"], target).stdout.strip()
        branch = run(["git", "branch", "--show-current"], target).stdout.strip()
        commit_date = run(["git", "show", "-s", "--format=%cI", "HEAD"], target).stdout.strip()
        files = sorted(
            str(path.relative_to(target)).replace("\\", "/")
            for path in target.rglob("*")
            if path.is_file() and ".git" not in path.parts
        )
        lower = [path.lower() for path in files]
        test_files = [
            path for path in files
            if Path(path).suffix == ".py" and (
                Path(path).name.lower().startswith("test_")
                or Path(path).name.lower().endswith("_test.py")
            )
        ]
        implementation_files = [
            path for path in files
            if Path(path).suffix == ".py"
            and path not in test_files
            and Path(path).name not in {"setup.py", "freeze.py", "benchmark.py", "ablations.py"}
        ]

        checks = {
            "README": has_named(files, {"readme.md", "readme.rst", "readme.txt"}),
            "LICENSE": has_named(files, {"license", "license.md", "license.txt", "copying"}),
            "CITATION": has_named(files, {"citation.cff"}),
            "IMPLEMENTATION": bool(implementation_files),
            "TEST": bool(test_files),
            "LIMITATIONS_OR_FALSIFICATION": has_fragment(
                files, ("limitation", "falsification")
            ),
            "BENCHMARK": has_fragment(files, ("benchmark",)),
            "ABLATION": has_fragment(files, ("ablation",)),
            "FREEZE_OR_MANIFEST": has_named(files, {"freeze.py", "manifest.sha256"}),
            "CI": any(path.startswith(".github/workflows/") and path.endswith((".yml", ".yaml")) for path in lower),
        }

        test_started = time.perf_counter()
        if test_files:
            try:
                test = run(
                    [sys.executable, "-m", "pytest", "-q"],
                    target,
                    timeout=test_timeout,
                )
                test_status = "PASS" if test.returncode == 0 else "FAIL"
                test_output = test.stdout[-4000:]
                test_returncode = test.returncode
            except subprocess.TimeoutExpired as exc:
                test_status = "TIMEOUT"
                test_output = str(exc)[-4000:]
                test_returncode = None
        else:
            test_status = "MISSING"
            test_output = "No Python test file matched the frozen test-file rule."
            test_returncode = None
        test_seconds = time.perf_counter() - test_started
        checks["TESTS_PASS"] = test_status == "PASS"

        actual_required = tuple(key for key in REQUIRED if checks.get(key, False))
        missing_required = [key for key in REQUIRED if not checks.get(key, False)]
        missing_optional = [key for key in OPTIONAL if not checks.get(key, False)]

        spec = freeze_protocol({
            "run_id": f"ZOOWIDE-001-{number:02d}",
            "candidate_version": head,
            "baseline_versions": {"core-zoo-registry": AUDIT_PROTOCOL_HASH},
            "dataset_version": "github-snapshot@2026-09-02",
            "information_features": list(REQUIRED),
            "compute_ratio_bounds": [0.5, 2.0],
            "drift_amber_threshold": 0.001,
            "drift_red_threshold": 1.0,
            "max_missingness": 0.0,
            "black_missingness": 1.0,
            "red_on_distribution_shift": False,
            "allowed_interventions": [],
            "stop_reason_codes": [
                "STOP_PROTOCOL_MUTATION", "STOP_INFORMATION_LEAKAGE",
                "STOP_BASELINE_ASYMMETRY", "STOP_DATA_CORRUPTION",
                "STOP_INSTRUMENT_FAILURE", "STOP_UNRECORDED_INTERVENTION",
                "STOP_VERSION_DRIFT",
            ],
            "animal_number": number,
            "repository": f"enuminous/{name}",
            "audit_protocol_hash": AUDIT_PROTOCOL_HASH,
        })
        observation = Observation(
            timestamp=datetime.now(timezone.utc).isoformat(),
            run_id=spec.run_id,
            protocol_hash=spec.protocol_hash,
            candidate_version=head,
            baseline_versions=spec.baseline_versions,
            dataset_version=spec.dataset_version,
            candidate_information=actual_required,
            baseline_information={"core-zoo-registry": tuple(REQUIRED)},
            candidate_compute=max(test_seconds, 1e-9),
            baseline_compute={"core-zoo-registry": max(test_seconds, 1e-9)},
            distribution_shift=len(missing_optional) / len(OPTIONAL),
            missingness=0.0,
            outcome={
                "test_status": test_status,
                "test_returncode": test_returncode,
                "test_output_tail": test_output,
            },
            metadata={
                "repository": f"enuminous/{name}",
                "branch": branch,
                "tree_sha": tree,
                "commit_date": commit_date,
                "checks": checks,
                "missing_required": missing_required,
                "missing_optional": missing_optional,
            },
        )
        record = HummingbirdMonitor(spec).observe(observation)
        result.update({
            "retrieval": "PASS",
            "default_branch": branch,
            "head_sha": head,
            "tree_sha": tree,
            "commit_date": commit_date,
            "file_count": len(files),
            "checks": checks,
            "missing_required": missing_required,
            "missing_optional": missing_optional,
            "test_status": test_status,
            "test_seconds": test_seconds,
            "snapshot_protocol_hash": spec.protocol_hash,
            "state": record.state.value,
            "inference_status": record.inference_status.value,
            "stop_recommended": record.stop_recommended,
            "deviations": [item.to_mapping() for item in record.deviations],
            "flight_record": record.to_mapping(),
            "elapsed_seconds": time.perf_counter() - started,
        })
        return result
    except Exception as exc:
        result.update({
            "retrieval": "FAILED",
            "state": "BLACK",
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_seconds": time.perf_counter() - started,
        })
        return result


def render_report(payload: dict) -> str:
    summary = payload["summary"]
    lines = [
        "# HUMMINGBIRD ZOO-WIDE FLIGHT REPORT",
        "",
        "**Run:** ZOOWIDE-001  ",
        f"**Observed:** {payload['observed_at']}  ",
        f"**Audit protocol:** `{payload['audit_protocol_hash']}`  ",
        f"**Zoo evidence-chain head:** `{payload['zoo_evidence_chain_head']}`",
        "",
        "## Verdict",
        "",
        f"- GREEN: {summary.get('GREEN', 0)}",
        f"- AMBER: {summary.get('AMBER', 0)}",
        f"- RED: {summary.get('RED', 0)}",
        f"- BLACK: {summary.get('BLACK', 0)}",
        f"- Test suites passing: {payload['tests']['PASS']}/46",
        f"- Tests collected and passed: {payload['test_cases_collected']}",
        f"- Repositories resolved: {payload['repositories_resolved']}/46",
        f"- Runner SHA-256: `{payload['runner_sha256']}`",
        "",
        "This first flight establishes exact prospective commit baselines. It does not prove that",
        "historical states preceding the flight were unchanged, nor does a passing unit test validate",
        "an animal's scientific claim.",
        "",
        "## Aggregate integrity findings",
        "",
        *[
            f"- Missing {name}: {count}/46"
            for name, count in payload["missing_evidence_counts"].items()
            if count
        ],
        "",
        "## Animal matrix",
        "",
        "| # | Animal | State | Tests | Missing core | Missing reproducibility | HEAD |",
        "|---:|---|---|---|---|---|---|",
    ]
    for item in payload["animals"]:
        head = item.get("head_sha", "—")
        lines.append(
            f"| {item['number']} | {item['animal']} | **{item['state']}** | "
            f"{item.get('test_status', '—')} | "
            f"{', '.join(item.get('missing_required', [])) or '—'} | "
            f"{', '.join(item.get('missing_optional', [])) or '—'} | "
            f"`{head[:12]}` |"
        )
    lines.extend([
        "",
        "## Interpretation",
        "",
        "- GREEN means the repository satisfied every frozen structural, execution, and reproducibility check.",
        "- AMBER means core integrity passed but at least one optional reproducibility surface was absent.",
        "- RED means a frozen core check was absent or the current test suite did not pass in this runner.",
        "- BLACK means the repository or evidence could not be interpreted.",
        "- A changed HEAD on a later flight is a protocol/version event to investigate, not automatic scientific failure.",
        "",
        "## Required next flight",
        "",
        "Freeze this report and rerun without changing the protocol. The second flight can then detect",
        "version drift against the exact SHAs established here. External empirical validation remains",
        "separate from repository integrity.",
        "",
        "**Hover. Observe. Never secretly steer.**",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run HUMMINGBIRD across EFMW Zoo #1-46")
    parser.add_argument("--output-dir", default="runs", help="Report output directory")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--test-timeout", type=int, default=180)
    parser.add_argument("--keep-clones", action="store_true")
    args = parser.parse_args()

    output = Path(args.output_dir).resolve()
    output.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix="hummingbird-zoo-"))
    clone_root = temporary / "repos"
    clone_root.mkdir()
    observed_at = datetime.now(timezone.utc).isoformat()
    try:
        animals = []
        with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
            futures = {
                pool.submit(inspect_repository, number, name, clone_root, args.test_timeout): number
                for number, name in ROSTER
            }
            for future in as_completed(futures):
                animals.append(future.result())
        animals.sort(key=lambda item: item["number"])

        previous = GENESIS_HASH
        for item in animals:
            evidence = {key: value for key, value in item.items() if key != "flight_record"}
            previous = chain_digest(previous, evidence)
            item["zoo_chain_hash"] = previous

        states: dict[str, int] = {}
        tests = {"PASS": 0, "FAIL": 0, "TIMEOUT": 0, "MISSING": 0, "UNKNOWN": 0}
        missing_evidence: dict[str, int] = {name: 0 for name in REQUIRED + OPTIONAL}
        test_cases_collected = 0
        for item in animals:
            states[item["state"]] = states.get(item["state"], 0) + 1
            key = item.get("test_status", "UNKNOWN")
            tests[key] = tests.get(key, 0) + 1
            for name in item.get("missing_required", []) + item.get("missing_optional", []):
                missing_evidence[name] += 1
            if item.get("test_status") == "PASS":
                output_tail = item["flight_record"]["observation"]["outcome"]["test_output_tail"]
                matches = re.findall(r"(\d+) passed", output_tail)
                if matches:
                    test_cases_collected += int(matches[-1])

        runner_sha256 = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()

        payload = {
            "schema": "hummingbird.zoowide.v1",
            "observed_at": observed_at,
            "audit_protocol": AUDIT_PROTOCOL,
            "audit_protocol_hash": AUDIT_PROTOCOL_HASH,
            "zoo_evidence_chain_head": previous,
            "summary": states,
            "tests": tests,
            "test_cases_collected": test_cases_collected,
            "missing_evidence_counts": missing_evidence,
            "repositories_resolved": sum(item.get("retrieval") == "PASS" for item in animals),
            "runner_sha256": runner_sha256,
            "runner_environment": {
                "python": sys.version,
                "platform": platform.platform(),
                "pytest": __import__("pytest").__version__,
            },
            "animals": animals,
        }
        (output / "ZOOWIDE-001.protocol.json").write_text(
            json.dumps(AUDIT_PROTOCOL, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output / "ZOOWIDE-001.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (output / "ZOOWIDE-001.md").write_text(render_report(payload), encoding="utf-8")
        print(json.dumps({
            "audit_protocol_hash": AUDIT_PROTOCOL_HASH,
            "zoo_evidence_chain_head": previous,
            "summary": states,
            "tests": tests,
            "test_cases_collected": test_cases_collected,
            "missing_evidence_counts": missing_evidence,
            "repositories_resolved": payload["repositories_resolved"],
            "output": str(output),
        }, indent=2, sort_keys=True))
    finally:
        if args.keep_clones:
            print(f"clones retained at {temporary}")
        else:
            shutil.rmtree(temporary, ignore_errors=True)


if __name__ == "__main__":
    main()
