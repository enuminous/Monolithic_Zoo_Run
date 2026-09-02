from __future__ import annotations

import hashlib
import json
from enum import Enum
from typing import Any


GENESIS_HASH = "0" * 64


def _json_default(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if hasattr(value, "to_mapping"):
        return value.to_mapping()
    raise TypeError(f"Cannot serialize {type(value).__name__}")


def stable_json(value: Any) -> str:
    return json.dumps(
        value,
        default=_json_default,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def sha256_json(value: Any) -> str:
    return hashlib.sha256(stable_json(value).encode("utf-8")).hexdigest()


def chain_digest(previous_hash: str, payload: Any) -> str:
    body = previous_hash + "\n" + stable_json(payload)
    return hashlib.sha256(body.encode("utf-8")).hexdigest()
