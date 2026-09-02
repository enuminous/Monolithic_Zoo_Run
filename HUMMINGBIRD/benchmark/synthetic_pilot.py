from __future__ import annotations

import random
import sys
import time
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from fault_injection import setup
from hummingbird import HummingbirdMonitor


def main(seed: int = 47, observations: int = 10000):
    rng = random.Random(seed)
    spec, base = setup()
    monitor = HummingbirdMonitor(spec)
    counts = {"GREEN": 0, "AMBER": 0, "RED": 0, "BLACK": 0}
    started = time.perf_counter_ns()
    for index in range(observations):
        shift = max(0.0, rng.gauss(0.03, 0.015))
        missing = max(0.0, min(1.0, rng.gauss(0.01, 0.005)))
        obs = replace(
            base,
            timestamp=str(index),
            distribution_shift=shift,
            missingness=missing,
        )
        counts[monitor.observe(obs).state.value] += 1
    elapsed = time.perf_counter_ns() - started
    print({"seed": seed, "observations": observations, "counts": counts})
    print({"total_ns": elapsed, "mean_ns_per_observation": elapsed / observations})


if __name__ == "__main__":
    main()
