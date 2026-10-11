from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping

from .events import FrozenSpec
from .hashing import sha256_json


def freeze_protocol(document: Mapping[str, Any]) -> FrozenSpec:
    """Normalize a protocol and return it with a canonical content hash."""
    body = dict(document)
    supplied_hash = body.pop("protocol_hash", None)
    body["protocol_hash"] = ""
    normalized = FrozenSpec.from_mapping(body).to_mapping()
    normalized.pop("protocol_hash")
    calculated = sha256_json(normalized)
    if supplied_hash is not None and supplied_hash != calculated:
        raise ValueError("Supplied protocol_hash does not match protocol content")
    normalized["protocol_hash"] = calculated
    return FrozenSpec.from_mapping(normalized)


def save_frozen_protocol(spec: FrozenSpec, path: str | Path) -> None:
    target = Path(path)
    target.write_text(
        json.dumps(spec.to_mapping(), indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def load_frozen_protocol(path: str | Path) -> FrozenSpec:
    document = json.loads(Path(path).read_text(encoding="utf-8"))
    return freeze_protocol(document)


def main() -> None:
    parser = argparse.ArgumentParser(description="Freeze a HUMMINGBIRD protocol")
    parser.add_argument("source", help="Unfrozen protocol JSON")
    parser.add_argument("destination", help="Destination frozen JSON")
    args = parser.parse_args()
    source = json.loads(Path(args.source).read_text(encoding="utf-8"))
    spec = freeze_protocol(source)
    save_frozen_protocol(spec, args.destination)
    print(spec.protocol_hash)


if __name__ == "__main__":
    main()
