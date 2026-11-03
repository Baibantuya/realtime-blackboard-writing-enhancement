# AI Session: 2026-09-29-006-board-folder-deployment

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Replace the prior release-manager approach with a visible, flat board folder containing the design files and a top-level run script, plus a local remote deployment script and README.
- Status: Flat-folder scripts implemented and deployed; live PL switch remains unverified
- Report candidate: no
- Related commits: None
- Related files: `kv260-whiteboard-enhance/scripts/`, `kv260-whiteboard-enhance/docs/`, current candidate deployment package

## Context Read

Read `AGENTS.md`, AI development policy, project state, decisions, index, prior deployment session 004, and inspected current candidate manifest, scripts, package paths, and board preflight behavior.

## Task and Constraints

The board package must be easy to inspect under a predictable path. Place the design `.bit`, `.hwh`, `.dtbo`, Python files, manifest, and top-level `run.sh` directly in one directory. Local deployment should show the exact remote target and support upload without run as well as upload-and-deploy. Do not store credentials.

## Contributions

- Replaced the previous versioned release-manager UX with a local `deploy_to_kv260.py` that prints the exact board path, flattens design firmware and PS scripts into one ZIP, uploads it, and supports upload-only, check, deploy, status, and stop commands.
- Added board installer `kv260_install_folder.py`, which validates a flat archive, installs it under `/home/ubuntu/kv260_apps/whiteboard_candidate/`, and preserves the replaced folder as `.previous`.
- Added the visible top-level `run.sh` and `kv260_board_run.py` for manifest matching, PS/PYNQ preflight, full FPGA load, software-only restart when hardware hashes match, smoke, live process, status, stop and previous-folder rollback.
- Rewrote the manual with the exact remote tree and commands; updated the formal README and local deployment config. No password is stored in project files.

## Decisions and Adoption

The owner rejected the previous release-manager presentation and clarified the desired board-folder workflow. Adopted D-057: visible flat package directory, explicit manifest mapping, top-level runner, and a local remote upload/deploy script. D-055 is marked superseded.

## Commands and Tools

- `py -3 kv260-whiteboard-enhance/scripts/deploy_to_kv260.py check` (executed after final runner update).
- Available host actions: `upload`, `deploy`, `check`, `status`, and `stop`.

## Validation and Evidence

- Host packaged 19 files and uploaded them to the board. Installer reported `BOARD_FOLDER=/home/ubuntu/kv260_apps/whiteboard_candidate`.
- Board check exited 0 with `PS_WIDTH_HWH_CHECK_PASS`, `PYNQ_OVERLAY_METADATA_READY`, and `CHECK_PASS`. Existing CSI PYNQ driver version warning was informational.
- The final check packaged 20 files including a board-folder README, and did not program the PL or stop/restart the running candidate. New runner `deploy`, live process and rollback: 未执行.

## Errors and Corrections

The previous session produced a versioned release manager under `/home/ubuntu/kv260-deploy`, which did not match the owner's requested flat, visible working directory. It was superseded by the flat package path and `run.sh`. Package paths from the nested candidate are flattened by basename; packaging fails on basename collisions instead of silently overwriting files.

## Files Changed

- Added `kv260-whiteboard-enhance/scripts/deploy_to_kv260.py`, `kv260_install_folder.py`, `kv260_board_run.py`, `kv260_run.sh`, and `deployment.example.json`.
- Removed superseded `scripts/deploy_kv260.py`, `scripts/kv260_deploy_board.py`, and old deployment example.
- Updated `docs/kv260_manual_deployment.md`, `README.md`, and `project_workspace/kv260_deploy.local.json`.
- Updated D-055/D-057, project state, index, and this record.

## Remaining Work

When ready to switch the active design, run `py -3 kv260-whiteboard-enhance/scripts/deploy_to_kv260.py deploy`, review the smoke/live log and inspect the DP screen. This session only installed and preflighted the folder; no PL programming occurred. Candidate timing violation and physical color confirmation remain open.

## Handoff Notes

Board package is installed at `/home/ubuntu/kv260_apps/whiteboard_candidate/`; inspect it directly or run `sudo bash run.sh status` from that directory. The existing candidate process was not stopped by the read-only check. Passwords must not be added to the package, local config, or records.
