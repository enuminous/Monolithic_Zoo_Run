from pathlib import Path

from hummingbird import HummingbirdMonitor, Observation, freeze_protocol, render_markdown


document = {
    "run_id": "HB-EXAMPLE-001",
    "candidate_version": "candidate@1",
    "baseline_versions": {"baseline_a": "baseline_a@1"},
    "dataset_version": "dataset@1",
    "information_features": ["x", "y"],
    "compute_ratio_bounds": [0.8, 1.2],
    "drift_amber_threshold": 0.1,
    "drift_red_threshold": 0.3,
    "max_missingness": 0.05,
    "black_missingness": 0.5,
    "allowed_interventions": ["scheduled_pause"],
    "stop_reason_codes": [
        "STOP_PROTOCOL_MUTATION",
        "STOP_INFORMATION_LEAKAGE",
        "STOP_BASELINE_ASYMMETRY",
        "STOP_DATA_CORRUPTION",
        "STOP_INSTRUMENT_FAILURE",
        "STOP_UNRECORDED_INTERVENTION",
        "STOP_VERSION_DRIFT",
    ],
}
spec = freeze_protocol(document)
base = Observation(
    timestamp="2026-09-02T12:00:00Z",
    run_id=spec.run_id,
    protocol_hash=spec.protocol_hash,
    candidate_version=spec.candidate_version,
    baseline_versions=spec.baseline_versions,
    dataset_version=spec.dataset_version,
    candidate_information=spec.information_features,
    baseline_information={"baseline_a": spec.information_features},
    candidate_compute=1.0,
    baseline_compute={"baseline_a": 1.0},
)

log = Path("example-flight.jsonl")
if log.exists():
    log.unlink()

monitor = HummingbirdMonitor(spec, log_path=log)
records = [
    monitor.observe(base),
    monitor.observe(Observation(
        **{
            **base.to_mapping(),
            "timestamp": "2026-09-02T12:00:01Z",
            "distribution_shift": 0.15,
        }
    )),
]
print(render_markdown(records))
