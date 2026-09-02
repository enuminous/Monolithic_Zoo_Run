# HUMMINGBIRD ZOO-WIDE FLIGHT REPORT

**Run:** ZOOWIDE-001  
**Observed:** 2026-09-02T20:22:39.223973+00:00  
**Audit protocol:** `3c8ed81d800d83f4d4ef7fe063c0ff3aeb9fab65b7d7701118c2e9077061e700`  
**Zoo evidence-chain head:** `cb1d06aa2793097a0c595a5e219f4b95339a392c87317d2d1122d80077f05ff9`

## Verdict

- GREEN: 0
- AMBER: 46
- RED: 0
- BLACK: 0
- Test suites passing: 46/46
- Tests collected and passed: 118
- Repositories resolved: 46/46
- Runner SHA-256: `6e79959d1a7235f50ab7ab7a6892f2e72bc5687a3770649485061c9ebcd04efc`

This first flight establishes exact prospective commit baselines. It does not prove that
historical states preceding the flight were unchanged, nor does a passing unit test validate
an animal's scientific claim.

## Aggregate integrity findings

- Missing LIMITATIONS_OR_FALSIFICATION: 23/46
- Missing BENCHMARK: 23/46
- Missing ABLATION: 21/46
- Missing FREEZE_OR_MANIFEST: 23/46
- Missing CI: 46/46

## Animal matrix

| # | Animal | State | Tests | Missing core | Missing reproducibility | HEAD |
|---:|---|---|---|---|---|---|
| 1 | TORTOISE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, CI | `6658128fd2df` |
| 2 | OWL | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `afe43985e76e` |
| 3 | OCTOPUS | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `e590a6d9d757` |
| 4 | GECKO | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `0345f2ed1d98` |
| 5 | HIVE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `e66e03d67c19` |
| 6 | EAGLE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `d4f6fb029312` |
| 7 | CRAB | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `f49f430353c9` |
| 8 | SHEPHERD | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `c875bad6c518` |
| 9 | PULSE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `78b7bd4a4fa1` |
| 10 | CAT | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, CI | `9bf56f891b3a` |
| 11 | FOX | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `b4c317d45b7f` |
| 12 | SPIDER | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `fd8f546d528f` |
| 13 | RAVEN | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `d18b4a8e0581` |
| 14 | DOLPHIN | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `718b09ca4966` |
| 15 | ANT | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `e7432f132a47` |
| 16 | MOTH | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `08e5ce7cf219` |
| 17 | SHARK | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `13ef3943eb38` |
| 18 | PENGUIN | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `1a99e0c1eb1c` |
| 19 | BAT | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `67c2c0e3cd6f` |
| 20 | HEDGEHOG | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `2e9b46039a64` |
| 21 | CROCODILE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `2407241cc2d7` |
| 22 | DRAGON | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `9ac2ffe7a271` |
| 23 | TURTLE | **AMBER** | PASS | — | LIMITATIONS_OR_FALSIFICATION, BENCHMARK, ABLATION, CI | `ff98950fcb40` |
| 24 | MAGPIE | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `342438c17983` |
| 25 | WOLF | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `7e4fd6d2b7c8` |
| 26 | ELEPHANT | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `a30bd9ae77d7` |
| 27 | CHAMELEON | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `75095bd98349` |
| 28 | JELLYFISH | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `7119a66a7509` |
| 29 | BEAVER | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `f6255d49e71e` |
| 30 | MANTIS | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `a9fd85eb62a2` |
| 31 | BISON | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `588acafecff7` |
| 32 | WEASEL | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `fa2d91ae108f` |
| 33 | SALMON | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `b141f6ccd5b0` |
| 34 | ORCA | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `a5caecf5a81b` |
| 35 | MOLE | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `523f80178510` |
| 36 | LYNX | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `d2f705136a61` |
| 37 | HORSE | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `e55b6881a1d3` |
| 38 | TERMITE | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `76f70136ebf3` |
| 39 | PHOENIX | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `20079489fe4c` |
| 40 | COBRA | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `1af3a2016813` |
| 41 | WHALE | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `c64bbfb54fce` |
| 42 | FALCON | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `bf74635c358b` |
| 43 | RHINO | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `8718a3132ffc` |
| 44 | BONOBO | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `40a3c44a997b` |
| 45 | AXOLOTL | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `af8e011f0be6` |
| 46 | BUTTERFLY | **AMBER** | PASS | — | FREEZE_OR_MANIFEST, CI | `5952c7f260f6` |

## Interpretation

- GREEN means the repository satisfied every frozen structural, execution, and reproducibility check.
- AMBER means core integrity passed but at least one optional reproducibility surface was absent.
- RED means a frozen core check was absent or the current test suite did not pass in this runner.
- BLACK means the repository or evidence could not be interpreted.
- A changed HEAD on a later flight is a protocol/version event to investigate, not automatic scientific failure.

## Required next flight

Freeze this report and rerun without changing the protocol. The second flight can then detect
version drift against the exact SHAs established here. External empirical validation remains
separate from repository integrity.

**Hover. Observe. Never secretly steer.**
