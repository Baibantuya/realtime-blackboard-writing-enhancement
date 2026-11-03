---
name: pynq-overlay-preflight
description: Check PYNQ overlay artifact pairs, release identity and explicit HWH interface contracts offline before preparing a board-specific load. Use for reviewing a release or comparing new hardware packages; the checker does not load hardware or prove board functionality.
---

# PYNQ Overlay Preflight

Read [README.md](readme.md) for validated scope and [workflow.md](workflow.md) for operation order. The reusable executable is [scripts/preflight.py](scripts/preflight.py); its JSON contract is documented in [references/configuration.md](references/configuration.md).

Use a reviewed, versioned contract and immutable input copy. Obtain expected hashes/IP fields from an accepted release or independent interface specification; label observed-baseline snapshots as such. Do not derive a new expectation from the very input being challenged merely to make it pass.

Run `python scripts/preflight.py --root INPUT_ROOT --config PROFILE.json`. Read the JSON `checks`, including every `not_checked`; exit 0/`PASS_OFFLINE` means only the configured comparisons passed. Exit 1/`FAIL` is a mismatch or invalid input. Standard argparse usage errors may return 2. The script reads files and writes JSON to stdout only; it imports no PYNQ and executes no backend.

Keep target-board environment, physical device, build provenance, DTBO semantics, driver ABI, installed PYNQ parsing, and hardware functionality separate from byte/XML checks. A backend name in the profile is descriptive, never an executable command. Use the appropriate documented board loading workflow only within the user's execution scope; preparing materials does not authorize a reload.

For the V22 example, preserve these observed distinctions: `run.sh` defaults to deploy; `kv260_overlay.py --check-only` may write files and clear stale state; loading uses fpgautil followed by PYNQ metadata registration. The supplied original preflight still expects the legacy PS entry and must be reconciled before claiming cold-start reproducibility. See [project findings](../evidence/board_reproduction/entrypoint_conflict.md).

When reporting, distinguish reviewed source, this-run offline results, historical delivery evidence, operator feedback, plans and unverified work. Do not describe constructed test failures as historical incidents. AI_Sessions is maintained in the user's separate conversation; this workspace only links case identifiers and engineering evidence. Do not request raw conversations again or block engineering work on that archive.

For a new board/project, supply its own bitstream, HWH, device/interface/environment expectations and backend procedure. The V22 bitstream is not transferable to another device. Real cross-board use has not been validated in this draft.
