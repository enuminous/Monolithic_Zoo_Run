from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from benchmark.fault_injection import setup
from hummingbird import Channel, HummingbirdMonitor


def main():
    spec, base = setup()
    faults = {
        Channel.PROTOCOL: replace(base, protocol_hash="changed"),
        Channel.DATA: replace(base, missingness=0.5),
        Channel.INFORMATION: replace(base, candidate_information=("x", "y", "secret")),
        Channel.COMPUTE: replace(base, baseline_compute={"baseline": 4.0}),
        Channel.INTERVENTION: replace(base, intervention="manual_change"),
    }
    print("removed_channel,fault_channel,state")
    for removed in Channel:
        enabled = [channel for channel in Channel if channel != removed]
        for fault_channel, observation in faults.items():
            state = HummingbirdMonitor(
                spec, enabled_channels=enabled
            ).observe(observation).state.value
            print(f"{removed.value},{fault_channel.value},{state}")


if __name__ == "__main__":
    main()
