# HUMMINGBIRD specification v0.1.0

## Invariant

HUMMINGBIRD observes and records. It never mutates the candidate, baselines, labels, thresholds, exclusions, or experimental environment.

OBSERVE is not INTERVENE.

## Frozen inputs

Before a confirmatory run, freeze:

- run identity and protocol document;
- candidate and baseline versions;
- dataset/version and information features;
- compute-ratio bounds;
- drift and missingness tolerances;
- allowed interventions;
- stop reason codes;
- source commit, metrics, exclusions, and stopping rules in the protocol document.

The canonical SHA-256 of the frozen JSON is the protocol hash.

## Atomic observation

Each observation contains a timestamp, run ID, protocol hash, versions, information received, compute observations, intervention, distribution shift, missingness, optional outcome, and metadata.

## Classification precedence

BLACK > RED > AMBER > GREEN.

- GREEN: no registered deviation.
- AMBER: measurable but presently non-invalidating deviation.
- RED: registered validity breach.
- BLACK: evidence chain is too degraded to answer the registered question.

Severe distribution shift is AMBER by default because regime change is not automatically misconduct or invalidity. A protocol may explicitly set red_on_distribution_shift to make it a breach.

## Evidence log

Every record stores the preceding record hash and its own SHA-256 chain hash. Verification detects mutation, deletion within the observed chain, or reordering. Operational deployments should additionally anchor log heads in an independent timestamping or storage system; a local hash chain alone cannot prove that an entire file was replaced.

## Outcome separation

Outcome values may be recorded, but the classifier is not permitted to branch on them. Test HB-008 enforces this invariant.
