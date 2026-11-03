# AI Session: 2026-09-29-004-repeatable-kv260-deployment

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Turn the candidate KV260 deployment history into a repeatable manual workflow with a small fixed command set for later bit/HWH and PS Python updates.
- Status: Implementation complete; first managed live switch and rollback remain unverified
- Report candidate: Yes
- Related commits: None
- Related files: `kv260-whiteboard-enhance/scripts/`, `kv260-whiteboard-enhance/docs/`, current candidate deployment package

## Context Read

Read root AGENTS.md, AI development policy, project state, decisions, index, recent deployment/color sessions, current Git status and candidate package. Prior live candidate PID 20368 was active at the last check; the owner has not yet confirmed physical DP color after the latest pixel-format change.

## Task and Constraints

The deploy command should remain unchanged when artifact contents change. A changed hardware design still requires a matching bit/HWH/DTBO and software contract; the workflow cannot infer arbitrary new IP addresses or media graphs. The script must preflight before stopping the current app, preserve a rollback path, avoid storing credentials, and keep generated staging materials outside the formal project root.

## Contributions

- Implemented a Windows host entry with fixed `package`, `check`, `deploy`, `status`, and `rollback` subcommands. It reads a local no-password config, collects only declared firmware and package software, hashes every file and transfers a versioned ZIP by PuTTY.
- Implemented a board-side release manager that validates ZIP paths and hashes, parses HWH, runs optional design-specific preflight hooks and PYNQ metadata validation before stopping the old process. It selects a software-only restart when hardware hashes are identical and the managed process is alive, otherwise installs bit/HWH/DTBO and invokes `fpgautil` followed by PYNQ metadata registration. It retains previous releases and logs and attempts restoration after a failed managed switch.
- Added a generic overlay helper and candidate `deployment.json`. Added `--check-only` to the candidate PS width script so its HWH contract is checked before a live switch, without writing `/dev/mem`.
- Wrote a concise formal manual and linked it from the formal README. Added a formal manifest template. No password is present in any new file.

## Decisions and Adoption

Adopted the fixed command and package-local manifest contract. Current candidate package paths live in `project_workspace/kv260_deploy.local.json`; a different package only requires updating this local path and its own manifest. D-055 records the deployment contract. Design-specific PS widths, media setup and runtime commands remain explicit hooks because arbitrary HWH/DTBO changes cannot be inferred safely.

## Commands and Tools

- `py -3 kv260-whiteboard-enhance/scripts/deploy_kv260.py package`
- `py -3 kv260-whiteboard-enhance/scripts/deploy_kv260.py check`
- Existing candidate `load_pynq_overlay.py`, `set_ps_widths.py` and legacy deployment script were inspected to preserve the verified PYNQ/fpgautil environment and sequencing.

## Validation and Evidence

- Host package succeeded: release ID `f0c2a30b3bc18547c1f3`, 15 files, archive under `test_workspace/kv260_manual_deploy_staging/`.
- Board `check` succeeded after upload: `PS_WIDTH_HWH_CHECK_PASS`, `PYNQ_OVERLAY_METADATA_READY`, `PREFLIGHT_PASS`; the command exited 0. An existing PYNQ CSI IP driver version warning was printed but did not fail metadata parsing.
- The new manager's `deploy`, live process start, software-only update, FPGA reload and `rollback`: 未执行. Current video process was not intentionally stopped or replaced by this session. Physical display observation after the earlier DP pixel-order switch is still pending.

## Errors and Corrections

- PuTTY's first interactive remote command paused at `Access granted. Press Return to begin session.`; added `-no-antispoof` to the host plink call for future runs. This particular option was not retested on the board after editing.
- Release extraction was made atomic by validating a temporary directory before renaming it into the releases directory. Added release-ID recomputation and a managed-PID identity guard to avoid overwriting an existing release or stopping a recycled PID.

## Files Changed

- `kv260-whiteboard-enhance/scripts/deploy_kv260.py`, `kv260_deploy_board.py`, `kv260_overlay.py`, `deployment.example.json`
- `kv260-whiteboard-enhance/docs/kv260_manual_deployment.md`, `README.md`
- `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/deployment.json`, `software/set_ps_widths.py`
- `project_workspace/kv260_deploy.local.json`, `DECISIONS.md`, `PROJECT_STATE.md`, `ai/INDEX.md`, this session record

## Remaining Work

- On user-directed first managed deployment, run `deploy`, inspect the resulting live log and screen, then run `status`. There is no prior managed release to roll back to before this first success.
- On a later update, exercise software-only switching and `rollback` against actual board hardware. Confirm the monitor's physical colors after the earlier DP pixel-order change.
- Resolve the candidate bitstream's known timing violation in the hardware design; deployment packaging does not repair it.

## Handoff Notes

The board has a staged release and helper scripts in `/home/ubuntu/`; `check` did not switch firmware or the live app. Use the formal manual for the exact operator commands. Do not record passwords or private keys.
