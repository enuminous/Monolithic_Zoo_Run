from __future__ import annotations

from collections import Counter
from typing import Iterable

from .events import FlightRecord, InferenceStatus, IntegrityState


_RANK = {
    IntegrityState.GREEN: 0,
    IntegrityState.AMBER: 1,
    IntegrityState.RED: 2,
    IntegrityState.BLACK: 3,
}


def summarize(records: Iterable[FlightRecord]) -> dict:
    rows = list(records)
    if not rows:
        raise ValueError("At least one flight record is required")
    worst = max((row.state for row in rows), key=_RANK.get)
    reasons = Counter(
        deviation.reason_code.value
        for row in rows
        for deviation in row.deviations
    )
    inference = {
        IntegrityState.GREEN: InferenceStatus.VALID,
        IntegrityState.AMBER: InferenceStatus.VALID_WITH_QUALIFICATION,
        IntegrityState.RED: InferenceStatus.INVALID,
        IntegrityState.BLACK: InferenceStatus.UNINTERPRETABLE,
    }[worst]
    return {
        "experiment": rows[0].observation.run_id,
        "protocol_hash": rows[0].observation.protocol_hash,
        "observation_count": len(rows),
        "final_sequence": rows[-1].sequence,
        "log_head": rows[-1].chain_hash,
        "state_counts": dict(Counter(row.state.value for row in rows)),
        "reason_counts": dict(sorted(reasons.items())),
        "final_state": worst.value,
        "inference_status": inference.value,
        "stop_recommended": any(row.stop_recommended for row in rows),
    }


def render_markdown(records: Iterable[FlightRecord]) -> str:
    report = summarize(records)
    reasons = report["reason_counts"]
    reason_lines = (
        "\n".join(f"- {name}: {count}" for name, count in reasons.items())
        if reasons else "- None"
    )
    return f"""# HUMMINGBIRD FLIGHT REPORT

- Experiment: {report['experiment']}
- Frozen protocol: {report['protocol_hash']}
- Observations: {report['observation_count']}
- Final state: **{report['final_state']}**
- Inference status: **{report['inference_status']}**
- Stop recommended: **{report['stop_recommended']}**
- Log head: {report['log_head']}

## Deviations

{reason_lines}

This certificate reports conformance to the encoded frozen protocol. It does not
establish that the candidate's scientific claims are true.
"""
