from __future__ import annotations

from statistics import median
from typing import Iterable

from .events import (
    Channel,
    Deviation,
    FrozenSpec,
    InferenceStatus,
    IntegrityState,
    Observation,
    ReasonCode,
)


_STATE_RANK = {
    IntegrityState.GREEN: 0,
    IntegrityState.AMBER: 1,
    IntegrityState.RED: 2,
    IntegrityState.BLACK: 3,
}


def inference_status(state: IntegrityState) -> InferenceStatus:
    return {
        IntegrityState.GREEN: InferenceStatus.VALID,
        IntegrityState.AMBER: InferenceStatus.VALID_WITH_QUALIFICATION,
        IntegrityState.RED: InferenceStatus.INVALID,
        IntegrityState.BLACK: InferenceStatus.UNINTERPRETABLE,
    }[state]


def classify(deviations: Iterable[Deviation]) -> IntegrityState:
    states = [item.state for item in deviations]
    return max(states, key=_STATE_RANK.get) if states else IntegrityState.GREEN


def evaluate(
    spec: FrozenSpec,
    obs: Observation,
    enabled_channels: Iterable[Channel] | None = None,
) -> tuple[tuple[Deviation, ...], IntegrityState]:
    enabled = set(enabled_channels) if enabled_channels is not None else set(Channel)
    deviations: list[Deviation] = []

    def add(channel, code, state, message, expected=None, observed=None):
        if channel in enabled:
            deviations.append(Deviation(channel, code, state, message, expected, observed))

    if Channel.PROTOCOL in enabled:
        if obs.run_id != spec.run_id or obs.protocol_hash != spec.protocol_hash:
            add(
                Channel.PROTOCOL, ReasonCode.PROTOCOL_MUTATION, IntegrityState.RED,
                "Run identity or protocol hash differs from the frozen specification.",
                {"run_id": spec.run_id, "protocol_hash": spec.protocol_hash},
                {"run_id": obs.run_id, "protocol_hash": obs.protocol_hash},
            )
        if (
            obs.candidate_version != spec.candidate_version
            or dict(obs.baseline_versions) != dict(spec.baseline_versions)
        ):
            add(
                Channel.PROTOCOL, ReasonCode.VERSION_DRIFT, IntegrityState.RED,
                "Candidate or baseline version changed.",
                {"candidate": spec.candidate_version, "baselines": dict(spec.baseline_versions)},
                {"candidate": obs.candidate_version, "baselines": dict(obs.baseline_versions)},
            )
        if obs.dataset_version != spec.dataset_version:
            add(
                Channel.PROTOCOL, ReasonCode.DATA_CORRUPTION, IntegrityState.RED,
                "Dataset identity differs from the frozen specification.",
                spec.dataset_version, obs.dataset_version,
            )

    if Channel.DATA in enabled:
        if not 0 <= obs.missingness <= 1:
            add(
                Channel.DATA, ReasonCode.INSTRUMENT_FAILURE, IntegrityState.BLACK,
                "Missingness is outside the measurable range [0, 1].",
                "[0, 1]", obs.missingness,
            )
        elif obs.missingness >= spec.black_missingness:
            add(
                Channel.DATA, ReasonCode.INSTRUMENT_FAILURE, IntegrityState.BLACK,
                "Telemetry loss exceeds the uninterpretable threshold.",
                f"< {spec.black_missingness}", obs.missingness,
            )
        elif obs.missingness > spec.max_missingness:
            add(
                Channel.DATA, ReasonCode.DATA_CORRUPTION, IntegrityState.RED,
                "Missingness exceeds the frozen tolerance.",
                f"<= {spec.max_missingness}", obs.missingness,
            )

        if obs.distribution_shift >= spec.drift_amber_threshold:
            severe = obs.distribution_shift >= spec.drift_red_threshold
            state = (
                IntegrityState.RED
                if severe and spec.red_on_distribution_shift
                else IntegrityState.AMBER
            )
            add(
                Channel.DATA, ReasonCode.DISTRIBUTION_SHIFT, state,
                "Input regime differs materially from the reference distribution.",
                f"< {spec.drift_amber_threshold}", obs.distribution_shift,
            )

    if Channel.INFORMATION in enabled:
        expected = set(spec.information_features)
        candidate = set(obs.candidate_information)
        if candidate != expected:
            add(
                Channel.INFORMATION, ReasonCode.INFORMATION_LEAKAGE, IntegrityState.RED,
                "Candidate information differs from the frozen feature set.",
                sorted(expected), sorted(candidate),
            )
        for name in spec.baseline_versions:
            received = set(obs.baseline_information.get(name, ()))
            if received != expected:
                add(
                    Channel.INFORMATION, ReasonCode.BASELINE_ASYMMETRY, IntegrityState.RED,
                    f"Baseline {name!r} did not receive the frozen feature set.",
                    sorted(expected), sorted(received),
                )

    if Channel.COMPUTE in enabled:
        values = [
            float(obs.baseline_compute[name])
            for name in spec.baseline_versions
            if name in obs.baseline_compute
        ]
        if len(values) != len(spec.baseline_versions) or any(value <= 0 for value in values):
            add(
                Channel.COMPUTE, ReasonCode.INSTRUMENT_FAILURE, IntegrityState.BLACK,
                "Baseline compute telemetry is missing or non-positive.",
                sorted(spec.baseline_versions), dict(obs.baseline_compute),
            )
        elif obs.candidate_compute < 0:
            add(
                Channel.COMPUTE, ReasonCode.INSTRUMENT_FAILURE, IntegrityState.BLACK,
                "Candidate compute telemetry is negative.",
                ">= 0", obs.candidate_compute,
            )
        else:
            ratio = float(obs.candidate_compute) / median(values)
            lower, upper = spec.compute_ratio_bounds
            if ratio < lower or ratio > upper:
                add(
                    Channel.COMPUTE, ReasonCode.BASELINE_ASYMMETRY, IntegrityState.RED,
                    "Candidate/baseline compute ratio left the frozen bounds.",
                    [lower, upper], ratio,
                )

    if Channel.INTERVENTION in enabled and obs.intervention is not None:
        if obs.intervention in set(spec.allowed_interventions):
            add(
                Channel.INTERVENTION, ReasonCode.INTERVENTION_RECORDED, IntegrityState.AMBER,
                "Registered intervention occurred and was preserved.",
                sorted(spec.allowed_interventions), obs.intervention,
            )
        else:
            add(
                Channel.INTERVENTION, ReasonCode.UNRECORDED_INTERVENTION, IntegrityState.RED,
                "Intervention was not permitted by the frozen specification.",
                sorted(spec.allowed_interventions), obs.intervention,
            )

    # OUTCOME is intentionally record-only. No outcome value may affect classification.
    return tuple(deviations), classify(deviations)
