import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from hummingbird import (
    HummingbirdMonitor,
    IntegrityState,
    Observation,
    freeze_protocol,
    load_frozen_protocol,
    save_frozen_protocol,
    verify_log,
)


def make_spec():
    return freeze_protocol({
        "run_id": "HB-TEST",
        "candidate_version": "candidate@1",
        "baseline_versions": {"a": "a@1", "b": "b@1"},
        "dataset_version": "data@1",
        "information_features": ["y", "x"],
        "compute_ratio_bounds": [0.8, 1.2],
        "drift_amber_threshold": 0.1,
        "drift_red_threshold": 0.3,
        "max_missingness": 0.05,
        "black_missingness": 0.5,
        "red_on_distribution_shift": False,
        "allowed_interventions": ["scheduled_pause"],
        "stop_reason_codes": [
            "STOP_VERSION_DRIFT",
            "STOP_PROTOCOL_MUTATION",
            "STOP_INFORMATION_LEAKAGE",
            "STOP_BASELINE_ASYMMETRY",
            "STOP_DATA_CORRUPTION",
            "STOP_INSTRUMENT_FAILURE",
            "STOP_UNRECORDED_INTERVENTION",
        ],
    })


def make_observation(spec, **changes):
    base = Observation(
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
    )
    return replace(base, **changes)


class HummingbirdFaultTests(unittest.TestCase):
    def setUp(self):
        self.spec = make_spec()
        self.monitor = HummingbirdMonitor(self.spec)

    def test_hb001_protocol_mutation(self):
        record = self.monitor.observe(
            make_observation(self.spec, protocol_hash="tampered")
        )
        self.assertEqual(record.state, IntegrityState.RED)
        self.assertTrue(record.stop_recommended)

    def test_hb002_candidate_only_information(self):
        record = self.monitor.observe(
            make_observation(self.spec, candidate_information=("x", "y", "secret"))
        )
        self.assertEqual(record.state, IntegrityState.RED)

    def test_hb003_baseline_degradation(self):
        record = self.monitor.observe(
            make_observation(self.spec, baseline_compute={"a": 4.0, "b": 4.0})
        )
        self.assertEqual(record.state, IntegrityState.RED)

    def test_hb004_distribution_shift_is_amber_by_default(self):
        record = self.monitor.observe(
            make_observation(self.spec, distribution_shift=0.35)
        )
        self.assertEqual(record.state, IntegrityState.AMBER)
        self.assertFalse(record.stop_recommended)

    def test_hb005_unregistered_intervention(self):
        record = self.monitor.observe(
            make_observation(self.spec, intervention="manual_threshold_change")
        )
        self.assertEqual(record.state, IntegrityState.RED)

    def test_hb006_benign_perturbation_stays_green(self):
        for index in range(100):
            record = self.monitor.observe(make_observation(
                self.spec,
                timestamp=f"t-{index}",
                distribution_shift=0.099,
                missingness=0.05,
            ))
            self.assertEqual(record.state, IntegrityState.GREEN)

    def test_hb007_instrument_failure_is_black(self):
        record = self.monitor.observe(
            make_observation(self.spec, missingness=0.5)
        )
        self.assertEqual(record.state, IntegrityState.BLACK)

    def test_hb008_outcome_does_not_change_state(self):
        good = self.monitor.observe(make_observation(self.spec, outcome={"score": 1.0}))
        bad = self.monitor.observe(make_observation(self.spec, outcome={"score": -1.0}))
        self.assertEqual(good.state, IntegrityState.GREEN)
        self.assertEqual(good.state, bad.state)

    def test_frozen_protocol_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "protocol.json"
            save_frozen_protocol(self.spec, path)
            loaded = load_frozen_protocol(path)
            self.assertEqual(loaded.protocol_hash, self.spec.protocol_hash)
            self.assertEqual(loaded.to_mapping(), self.spec.to_mapping())

    def test_hash_chain_detects_tampering(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "flight.jsonl"
            monitor = HummingbirdMonitor(self.spec, path)
            monitor.observe(make_observation(self.spec))
            monitor.observe(make_observation(self.spec, timestamp="t2"))
            self.assertTrue(verify_log(path))
            rows = path.read_text(encoding="utf-8").splitlines()
            item = json.loads(rows[0])
            item["state"] = "RED"
            rows[0] = json.dumps(item)
            path.write_text("\n".join(rows) + "\n", encoding="utf-8")
            self.assertFalse(verify_log(path))


if __name__ == "__main__":
    unittest.main()
