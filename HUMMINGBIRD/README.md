# HUMMINGBIRD — EFMW Zoo #47

**Prospective Pilot Integrity Monitor**

HUMMINGBIRD is a small, read-only monitor that asks one question while an experiment is running:

> Are we still running the same test we preregistered?

It compares each observed experiment state with a frozen specification, classifies deviations, and writes an append-only hash-chained flight log. It does not tune the candidate, move thresholds, relabel data, remove runs, or use favorable outcomes to soften integrity findings.

## Scientific position

HUMMINGBIRD is the first prospective animal after the frozen historical Zoo (#1–46). It is therefore Zoo II / ZOOS-OOS-1 and must not be counted retroactively as evidence for the original Zoo.

HUMMINGBIRD is useful only if prospective testing shows that it detects consequential integrity faults better than ordinary logging, manual post-hoc audit, or conventional telemetry monitoring at matched information, compute, latency, and false-alarm budgets.

## Six channels

| Channel | Watches |
|---|---|
| Protocol | frozen procedure, versions, dataset identity |
| Data | distribution shift, missingness, telemetry loss |
| Information | feature/input parity across candidate and baselines |
| Compute | matched resource budgets |
| Intervention | human or automated changes during the run |
| Outcome | immutable recording only; never optimization |

States are GREEN (locked), AMBER (qualified deviation), RED (validity breach), and BLACK (result uninterpretable).

## Quick start

    python -m hummingbird.protocol protocol.example.json frozen_protocol.json
    python example.py
    python -m unittest discover -s tests -v
    python benchmark/fault_injection.py
    python ablations/channel_ablation.py

## Minimal use

    from hummingbird import HummingbirdMonitor, Observation
    from hummingbird.protocol import load_frozen_protocol

    spec = load_frozen_protocol("frozen_protocol.json")
    monitor = HummingbirdMonitor(spec, log_path="flight.jsonl")

    record = monitor.observe(Observation(
        timestamp="2026-09-02T12:00:00Z",
        run_id=spec.run_id,
        protocol_hash=spec.protocol_hash,
        candidate_version=spec.candidate_version,
        baseline_versions=spec.baseline_versions,
        dataset_version=spec.dataset_version,
        candidate_information=spec.information_features,
        baseline_information={
            name: spec.information_features for name in spec.baseline_versions
        },
        candidate_compute=1.0,
        baseline_compute={name: 1.0 for name in spec.baseline_versions},
    ))

    print(record.state.value, record.inference_status.value)

## Evidence boundary

A BLACK state does not mean the candidate failed. It means the experiment can no longer determine whether the candidate succeeded. Likewise, a GREEN report establishes procedural conformance to the encoded specification—not the truth of the candidate's scientific claims.

**Hover. Observe. Never secretly steer.**

Status: prospective research software; not validated for medical, financial, safety-critical, or autonomous deployment.
