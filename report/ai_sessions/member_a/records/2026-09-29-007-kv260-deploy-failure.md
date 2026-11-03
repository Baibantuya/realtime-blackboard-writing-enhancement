# AI Session: 2026-09-29-007-kv260-deploy-failure

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Diagnose the failed manual `run.sh deploy` from the owner's captured output and restore a safe, working deployment path.
- Status: Completed; corrected package deployed and live pipeline verified
- Report candidate: no
- Related commits: None
- Related files: `kv260-whiteboard-enhance/scripts/deploy_to_kv260.py`, `kv260_board_run.py`, `kv260_overlay.py`, deployment docs/example; `project_workspace/DECISIONS.md`, `PROJECT_STATE.md`

## Context Read

Read project instructions and development policy in the current task, D-057 and the flat-folder deployment session. Owner's captured log shows PS-width preflight passed; the FPGA manager reported a failed overlay load; the subsequent RAW8 setup could not find `/dev/media0`; fallback repeated the same failure.

## Task and Constraints

Inspect the board before retrying; repair the flat-package load path; recover the intended candidate and verify board state. Preserve logs. Do not record credentials.

## Contributions

- Diagnosed the initial run: preflight passed, but FPGA-manager firmware request failed; subsequent camera setup had no `/dev/media0`. Board inspection confirmed FPGA manager state `firmware request error: 0xfffffffe`, no media/video nodes, and kernel message that the requested firmware could not be loaded.
- First combined remote installer+sudo invocation closed its SSH session before installation. Verified the archive and installer remained on the board and the flat folder still had the old manifest. Split installation and deploy into two commands.
- Installed the updated package and deployed it. `fpgautil` reported `BIN FILE loaded through FPGA manager successfully`; PYNQ metadata registered; camera setup enumerated 1920x1080 RGB3; five-frame smoke passed; managed live PID 4352 started.
- Follow-up status confirmed PID 4352 alive, FPGA manager `operating`, `/dev/media0` and `/dev/video0` present. `live.log` progressed past frame 1240 with status 0, detected board corners, AE target/luma near 80/82, and no runtime failure.

## Decisions and Adoption

- Adopted D-058: exact DTBO firmware-name and staged firmware naming must agree. `fpgautil` or manager-state failure must stop the flow before PYNQ metadata/media setup. Do not retry the previous folder automatically; rollback is explicit.
- Updated deployment documentation and the generic manifest example to include firmware naming and explain failure/rollback behavior.
- Changed the host deploy helper to issue package installation and privileged board execution as separate SSH commands. This host-side refactor was not rerun after the successful manual split-phase board deployment to avoid a duplicate PL reload.
- Refreshed the board-folder `README.md` directly over SSH after updating the manual, without replacing the active package folder or interrupting the running pipeline.

## Commands and Tools

- Read-only board probes through PuTTY `plink`; board folder inspection; remote installer command; `sudo bash /home/ubuntu/kv260_apps/whiteboard_candidate/run.sh deploy`; follow-up status, FPGA state, device-node and live-log inspection.

## Validation and Evidence

- Before repair: `run.sh deploy` failed; logs showed `Failed to apply Overlay`, `BIN FILE loading through FPGA manager failed`, and `Failed to enumerate /dev/media0 (-2)`; `.previous` fallback repeated the failure.
- After repair: deploy exited 0. FPGA manager `operating`; `/dev/media0` and `/dev/video0` exist; format `1920x1080 RGB3`; smoke completed and command printed `DEPLOY_RUNNING ... pid=4352 FPGA_reloaded=True`.
- Follow-up: `run.sh status` reported `alive: true`; live log advanced through frame 1240 with `status: 0`, detected corners, and no Python exception. Physical monitor output was not visually checked.
- The new two-phase host helper itself was not executed after editing.

## Errors and Corrections

- The old runner accepted PYNQ metadata/CMA setup after `fpgautil` had already reported failure, then attempted media setup and automatic full-load retry from `.previous`; that repeated a known-failed operation. Updated overlay helper validates return code/error text and FPGA-manager state before metadata registration, and runner reports automatic retry disabled.
- The first combined plink command disconnected, but SSH remained available. Read-only inspection proved installation had not occurred. Splitting install and root deploy phases resolved the interruption.

## Files Changed

- `kv260-whiteboard-enhance/scripts/kv260_board_run.py` and `kv260_overlay.py` (corrected and verified by the successful board run).
- `kv260-whiteboard-enhance/scripts/deploy_to_kv260.py` (split install/run SSH phases; not re-executed).
- `kv260-whiteboard-enhance/scripts/deployment.example.json` and `docs/kv260_manual_deployment.md`.
- Board copy `/home/ubuntu/kv260_apps/whiteboard_candidate/README.md` was refreshed; no PL operation was triggered by the documentation copy.
- `project_workspace/DECISIONS.md`, `PROJECT_STATE.md`, `ai/INDEX.md`, and this session record.

## Remaining Work

Candidate is active at PID 4352. Candidate timing violation and physical color/display confirmation remain open.

## Handoff Notes

Board package is installed at `/home/ubuntu/kv260_apps/whiteboard_candidate/`; inspect it or run `sudo bash run.sh status` from that directory. Current handoff state: PID 4352 active, FPGA manager `operating`, RAW8 camera capture configured at 1920x1080 RGB3. Physical screen confirmation remains with the owner. Passwords must not be added to package, local config, or records.
