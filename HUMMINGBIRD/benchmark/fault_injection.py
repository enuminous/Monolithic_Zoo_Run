from __future__ import annotations

import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from hummingbird import HummingbirdMonitor, Observation, freeze_protocol


def setup():
    spec = freeze_protocol({
        "run_id": "HB-BENCH",
        "candidate_version": "candidate@1",
        "baseline_versions": {"baseline": "baseline@1"},
        "dataset_version": "data@1",
        "information_features": ["x", "y"],
        "compute_ratio_bounds": [0.8, 1.2],
        "drift_amber_threshold": 0.1,
        "drift_red_threshold": 0.3,
        "max_missingness": 0.05,
        "black_missingness": 0.5,
        "allowed_interventions": [],
        "stop_reason_codes": [
            "STOP_PROTOCOL_MUTATION",
            "STOP_INFORMATION_LEAKAGE",
            "STOP_BASELINE_ASYMMETRY",
            "STOP_DATA_CORRUPTION",
            "STOP_INSTRUMENT_FAILURE",
            "STOP_UNRECORDED_INTERVENTION",
            "STOP_VERSION_DRIFT",
        ],
    })
    obs = Observation(
        timestamp="0",
        run_id=spec.run_id,
        protocol_hash=spec.protocol_hash,
        candidate_version=spec.candidate_version,
        baseline_versions=spec.baseline_versions,
        dataset_version=spec.dataset_version,
        candidate_information=spec.information_features,
        baseline_information={"baseline": spec.information_features},
        candidate_compute=1.0,
        baseline_compute={"baseline": 1.0},
    )
    return spec, obs


def main():
    spec, base = setup()
    injections = {
        "HB-001 protocol": replace(base, protocol_hash="changed"),
        "HB-002 information": replace(base, candidate_information=("x", "y", "secret")),
        "HB-003 compute": replace(base, baseline_compute={"baseline": 4.0}),
        "HB-004 shift": replace(base, distribution_shift=0.35),
        "HB-005 intervention": replace(base, intervention="manual_change"),
        "HB-006 benign": replace(base, distribution_shift=0.09, missingness=0.01),
        "HB-007 instrument": replace(base, missingness=0.5),
        "HB-008 outcome": replace(base, outcome={"candidate_wins": True}),
    }
    expected = {
        "HB-001 protocol": "RED",
        "HB-002 information": "RED",
        "HB-003 compute": "RED",
        "HB-004 shift": "AMBER",
        "HB-005 intervention": "RED",
        "HB-006 benign": "GREEN",
        "HB-007 instrument": "BLACK",
        "HB-008 outcome": "GREEN",
    }
    monitor = HummingbirdMonitor(spec)
    started = time.perf_counter_ns()
    results = {
        name: monitor.observe(obs).state.value for name, obs in injections.items()
    }
    elapsed = time.perf_counter_ns() - started
    passed = sum(results[name] == expected[name] for name in results)
    for name, state in results.items():
        print(f"{name}: {state} (expected {expected[name]})")
    print(f"detection fixtures passed: {passed}/{len(results)}")
    print(f"total classifier time ns: {elapsed}")
    raise SystemExit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
