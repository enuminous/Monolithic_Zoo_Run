from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any, Mapping


class IntegrityState(str, Enum):
    GREEN = "GREEN"
    AMBER = "AMBER"
    RED = "RED"
    BLACK = "BLACK"


class InferenceStatus(str, Enum):
    VALID = "VALID"
    VALID_WITH_QUALIFICATION = "VALID WITH QUALIFICATION"
    INVALID = "INVALID"
    UNINTERPRETABLE = "UNINTERPRETABLE"


class Channel(str, Enum):
    PROTOCOL = "protocol"
    DATA = "data"
    INFORMATION = "information"
    COMPUTE = "compute"
    INTERVENTION = "intervention"
    OUTCOME = "outcome"


class ReasonCode(str, Enum):
    PROTOCOL_MUTATION = "STOP_PROTOCOL_MUTATION"
    INFORMATION_LEAKAGE = "STOP_INFORMATION_LEAKAGE"
    BASELINE_ASYMMETRY = "STOP_BASELINE_ASYMMETRY"
    DATA_CORRUPTION = "STOP_DATA_CORRUPTION"
    INSTRUMENT_FAILURE = "STOP_INSTRUMENT_FAILURE"
    UNRECORDED_INTERVENTION = "STOP_UNRECORDED_INTERVENTION"
    VERSION_DRIFT = "STOP_VERSION_DRIFT"
    DISTRIBUTION_SHIFT = "DISTRIBUTION_SHIFT"
    INTERVENTION_RECORDED = "INTERVENTION_RECORDED"


@dataclass(frozen=True)
class FrozenSpec:
    run_id: str
    protocol_hash: str
    candidate_version: str
    baseline_versions: Mapping[str, str]
    dataset_version: str
    information_features: tuple[str, ...]
    compute_ratio_bounds: tuple[float, float] = (0.8, 1.2)
    drift_amber_threshold: float = 0.1
    drift_red_threshold: float = 0.3
    max_missingness: float = 0.05
    black_missingness: float = 0.5
    red_on_distribution_shift: bool = False
    allowed_interventions: tuple[str, ...] = ()
    stop_reason_codes: tuple[str, ...] = ()
    extra: Mapping[str, Any] = field(default_factory=dict)

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any]) -> "FrozenSpec":
        known = {
            "run_id", "protocol_hash", "candidate_version", "baseline_versions",
            "dataset_version", "information_features", "compute_ratio_bounds",
            "drift_amber_threshold", "drift_red_threshold", "max_missingness",
            "black_missingness", "red_on_distribution_shift",
            "allowed_interventions", "stop_reason_codes",
        }
        missing = [
            key for key in (
                "run_id", "protocol_hash", "candidate_version",
                "baseline_versions", "dataset_version", "information_features",
            )
            if key not in value
        ]
        if missing:
            raise ValueError(f"Missing frozen protocol fields: {', '.join(missing)}")
        bounds = tuple(float(x) for x in value.get("compute_ratio_bounds", (0.8, 1.2)))
        if len(bounds) != 2 or bounds[0] <= 0 or bounds[0] > bounds[1]:
            raise ValueError("compute_ratio_bounds must be two positive ordered values")
        amber = float(value.get("drift_amber_threshold", 0.1))
        red = float(value.get("drift_red_threshold", 0.3))
        if not 0 <= amber <= red:
            raise ValueError("drift thresholds must satisfy 0 <= amber <= red")
        max_missing = float(value.get("max_missingness", 0.05))
        black_missing = float(value.get("black_missingness", 0.5))
        if not 0 <= max_missing <= black_missing <= 1:
            raise ValueError("missingness must satisfy 0 <= max <= black <= 1")
        return cls(
            run_id=str(value["run_id"]),
            protocol_hash=str(value["protocol_hash"]),
            candidate_version=str(value["candidate_version"]),
            baseline_versions=dict(value["baseline_versions"]),
            dataset_version=str(value["dataset_version"]),
            information_features=tuple(sorted(map(str, value["information_features"]))),
            compute_ratio_bounds=(bounds[0], bounds[1]),
            drift_amber_threshold=amber,
            drift_red_threshold=red,
            max_missingness=max_missing,
            black_missingness=black_missing,
            red_on_distribution_shift=bool(value.get("red_on_distribution_shift", False)),
            allowed_interventions=tuple(sorted(map(str, value.get("allowed_interventions", ())))),
            stop_reason_codes=tuple(sorted(map(str, value.get("stop_reason_codes", ())))),
            extra={key: value[key] for key in value if key not in known},
        )

    def to_mapping(self) -> dict[str, Any]:
        result = {
            "run_id": self.run_id,
            "protocol_hash": self.protocol_hash,
            "candidate_version": self.candidate_version,
            "baseline_versions": dict(self.baseline_versions),
            "dataset_version": self.dataset_version,
            "information_features": list(self.information_features),
            "compute_ratio_bounds": list(self.compute_ratio_bounds),
            "drift_amber_threshold": self.drift_amber_threshold,
            "drift_red_threshold": self.drift_red_threshold,
            "max_missingness": self.max_missingness,
            "black_missingness": self.black_missingness,
            "red_on_distribution_shift": self.red_on_distribution_shift,
            "allowed_interventions": list(self.allowed_interventions),
            "stop_reason_codes": list(self.stop_reason_codes),
        }
        result.update(self.extra)
        return result


@dataclass(frozen=True)
class Observation:
    timestamp: str
    run_id: str
    protocol_hash: str
    candidate_version: str
    baseline_versions: Mapping[str, str]
    dataset_version: str
    candidate_information: tuple[str, ...]
    baseline_information: Mapping[str, tuple[str, ...]]
    candidate_compute: float
    baseline_compute: Mapping[str, float]
    intervention: str | None = None
    distribution_shift: float = 0.0
    missingness: float = 0.0
    outcome: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_mapping(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Deviation:
    channel: Channel
    reason_code: ReasonCode
    state: IntegrityState
    message: str
    expected: Any = None
    observed: Any = None

    def to_mapping(self) -> dict[str, Any]:
        value = asdict(self)
        value["channel"] = self.channel.value
        value["reason_code"] = self.reason_code.value
        value["state"] = self.state.value
        return value


@dataclass(frozen=True)
class FlightRecord:
    sequence: int
    observation: Observation
    deviations: tuple[Deviation, ...]
    state: IntegrityState
    inference_status: InferenceStatus
    stop_recommended: bool
    previous_hash: str
    chain_hash: str

    def to_mapping(self) -> dict[str, Any]:
        return {
            "sequence": self.sequence,
            "observation": self.observation.to_mapping(),
            "deviations": [d.to_mapping() for d in self.deviations],
            "state": self.state.value,
            "inference_status": self.inference_status.value,
            "stop_recommended": self.stop_recommended,
            "previous_hash": self.previous_hash,
            "chain_hash": self.chain_hash,
        }
