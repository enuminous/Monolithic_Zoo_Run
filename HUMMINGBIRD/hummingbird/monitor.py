from __future__ import annotations

import json
import os
from dataclasses import replace
from pathlib import Path
from threading import Lock
from typing import Iterable

from .events import Channel, FlightRecord, FrozenSpec, Observation
from .hashing import GENESIS_HASH, chain_digest, stable_json
from .integrity import evaluate, inference_status


class HummingbirdMonitor:
    """Read-only classifier with an optional append-only hash-chained log."""

    def __init__(
        self,
        spec: FrozenSpec,
        log_path: str | Path | None = None,
        enabled_channels: Iterable[Channel] | None = None,
    ) -> None:
        self.spec = spec
        self.log_path = Path(log_path) if log_path is not None else None
        self.enabled_channels = (
            tuple(enabled_channels) if enabled_channels is not None else tuple(Channel)
        )
        self._lock = Lock()
        self._sequence, self._previous_hash = self._resume_state()

    def _resume_state(self) -> tuple[int, str]:
        if self.log_path is None or not self.log_path.exists():
            return 0, GENESIS_HASH
        lines = [
            line for line in self.log_path.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        if not lines:
            return 0, GENESIS_HASH
        if not verify_log(self.log_path):
            raise ValueError("Existing flight log failed hash-chain verification")
        last = json.loads(lines[-1])
        return int(last["sequence"]) + 1, str(last["chain_hash"])

    def observe(self, observation: Observation) -> FlightRecord:
        with self._lock:
            deviations, state = evaluate(
                self.spec, observation, self.enabled_channels
            )
            stop_codes = set(self.spec.stop_reason_codes)
            stop_recommended = any(
                deviation.reason_code.value in stop_codes for deviation in deviations
            )
            draft = FlightRecord(
                sequence=self._sequence,
                observation=observation,
                deviations=deviations,
                state=state,
                inference_status=inference_status(state),
                stop_recommended=stop_recommended,
                previous_hash=self._previous_hash,
                chain_hash="",
            )
            payload = draft.to_mapping()
            payload.pop("chain_hash")
            digest = chain_digest(self._previous_hash, payload)
            record = replace(draft, chain_hash=digest)
            if self.log_path is not None:
                self.log_path.parent.mkdir(parents=True, exist_ok=True)
                with self.log_path.open("a", encoding="utf-8") as handle:
                    handle.write(stable_json(record.to_mapping()) + "\n")
                    handle.flush()
                    os.fsync(handle.fileno())
            self._sequence += 1
            self._previous_hash = digest
            return record


def verify_log(path: str | Path) -> bool:
    previous = GENESIS_HASH
    expected_sequence = 0
    try:
        with Path(path).open("r", encoding="utf-8") as handle:
            for line in handle:
                if not line.strip():
                    continue
                record = json.loads(line)
                digest = record.pop("chain_hash")
                if record.get("sequence") != expected_sequence:
                    return False
                if record.get("previous_hash") != previous:
                    return False
                if chain_digest(previous, record) != digest:
                    return False
                previous = digest
                expected_sequence += 1
    except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
        return False
    return True
