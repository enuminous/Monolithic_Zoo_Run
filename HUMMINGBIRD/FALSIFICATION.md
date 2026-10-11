# Falsification plan

## Primary claim

Continuous frozen-protocol monitoring catches experimentally consequential deviations that would otherwise survive into final analysis.

## Baselines

1. ordinary experiment logging;
2. blinded manual post-hoc audit;
3. conventional MLOps or telemetry monitoring.

All systems must receive matched information and be evaluated under matched compute, latency, and false-alarm budgets.

## Preregistered measures

- fault detection rate;
- false-alarm rate;
- detection latency;
- monitoring overhead;
- experiment-contamination rate;
- severity calibration;
- per-fault-class sensitivity.

## Required fault suite

| ID | Injection | Expected state |
|---|---|---|
| HB-001 | silent protocol mutation | RED |
| HB-002 | candidate-only information | RED |
| HB-003 | degraded or slowed baseline | RED |
| HB-004 | distribution shift only | AMBER by default |
| HB-005 | unregistered intervention | RED |
| HB-006 | perturbation below tolerance | GREEN |
| HB-007 | severe telemetry loss | BLACK |
| HB-008 | favorable/unfavorable outcome reveal | unchanged |

## Loss condition

HUMMINGBIRD loses if conventional logging or post-hoc audit identifies integrity violations equally well or better under matched information, compute, latency, and false-alarm constraints.

Passing the included unit tests establishes implementation behavior only. It is not empirical validation of the primary claim.
