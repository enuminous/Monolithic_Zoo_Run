"""HUMMINGBIRD: prospective, read-only experiment-integrity monitoring."""

from .events import (
    Channel,
    Deviation,
    FlightRecord,
    FrozenSpec,
    InferenceStatus,
    IntegrityState,
    Observation,
    ReasonCode,
)
from .monitor import HummingbirdMonitor, verify_log
from .protocol import freeze_protocol, load_frozen_protocol, save_frozen_protocol
from .report import render_markdown, summarize

__all__ = [
    "Channel",
    "Deviation",
    "FlightRecord",
    "FrozenSpec",
    "HummingbirdMonitor",
    "InferenceStatus",
    "IntegrityState",
    "Observation",
    "ReasonCode",
    "freeze_protocol",
    "load_frozen_protocol",
    "render_markdown",
    "save_frozen_protocol",
    "summarize",
    "verify_log",
]

__version__ = "0.1.0"
