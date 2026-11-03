# AI Session: 2026-09-28-002-git-repository-setup

- Date: 2026-09-28
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Configure Git backups for the formal KV260 project and reproducible tests, retaining necessary Vivado project sources while excluding synthesized outputs.
- Status: Completed; empty workspace-level repository configured, no commit created
- Report candidate: No
- Related commits: None
- Related files: `.gitignore`, `.gitattributes`, `kv260-whiteboard-enhance/.gitignore`, `kv260-whiteboard-enhance/.gitattributes`, `test_workspace/imx219_team_package_20260928/imx219_rgb_rectify_20260928/.gitignore`, `.git/`

## Context Read
Read root `AGENTS.md`, `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`, and latest session `2026-09-28-001-ssh-host-setup.md`. The workspace root and formal project directory were not Git repositories. Found a separate nested Git repository under `test_workspace/imx219_reference_2026-09-24/.git` and another under the excluded `zcu104_legacy_demos/` tree.

## Task and Constraints
Back up the formal submission, runnable tests, and necessary Vivado source projects. Exclude tutorials and legacy demos. Include project definitions (`.xpr`), source block designs (`.bd`), IP configs (`.xci`), RTL, constraints and authored Tcl. Exclude Vivado/Vitis synthesis, implementation, simulation and HLS generated outputs. Keep `project_workspace/` internal. No hardware or synthesis validation is in scope for Git setup.

## Contributions
Moved the empty `.git` directory from `kv260-whiteboard-enhance/` to the workspace root, preserving branch `main`. Root allowlist includes `kv260-whiteboard-enhance/` and selected test paths: `imx219_ps_core/`, `imx219_ps_core_ae_tests/`, `kv260_fps_optimization_2026-09-22/`, `board_rectify_2026-09-24/`, `imx219_gamma_ae/`, `imx219_team_package_20260928/`, `query_kv260_hdmi_ip/`, `root-vivado-artifacts/`, and `test_workspace/query_kv260_hdmi_ip.tcl`. Updated the team-package `.gitignore` to stop excluding its whole `build/`, allowing the `.xpr` and source `.bd` through.

Root ignore rules exclude `.Xil`, `.runs`, `.gen`, `.cache`, `.sim`, HLS `solution*`, synthesis/implementation result directories, logs, reports, DCP, bitstream/HWH/XSA/BIN and other generated outputs in `test_workspace`. Official deployable `.bit/.hwh` in `kv260-whiteboard-enhance/pynq/` remain available as project deliverables. Tutorials, `zcu104_legacy_demos/`, `project_workspace/`, unselected test folders, and the existing nested `imx219_reference` repository remain outside the parent repository.

## Decisions and Adoption
Use one workspace-level Git repository. Track reproducible source and project definitions, not tool-generated synthesis/implementation data. The current candidate set is 309 files / 12.98 MB. This changes only version-control scope, not hardware architecture or evaluation method.

## Commands and Tools
PowerShell inventory by project and extension; `git status --short`, `git ls-files --others --exclude-standard`, and `git check-ignore` checks for source project files and generated products.

## Validation and Evidence
`git rev-parse --show-toplevel` resolves to `E:/code/fpga-competition`; branch is `main`; no commit or remote exists. Candidate inventory confirms 81 `.xpr/.bd/.xci/.xdc` files along with source and scripts. Ignore checks confirm `.xpr` and source `.bd` files are visible while `.runs`/DCP, `.Xil`, `.bit`, `.bin`, DLL and log outputs in test projects are excluded. Tutorials, legacy demos and unselected test folders are excluded. No tests, synthesis or board runs were executed.

## Errors and Corrections
An initial `Add-Content` invocation for ignore exceptions used invalid PowerShell argument syntax and made no change; corrected it using a here-string. The broad root ignore initially exposed unselected test folders after expanding Vivado projects; restored a `test_workspace/*` deny rule with explicit project-directory allowlist. A broad file inventory regex produced PowerShell regex errors and excessive output; replaced it with targeted extension and path queries.

## Files Changed
- `.gitignore`
- `.gitattributes`
- `kv260-whiteboard-enhance/.gitignore`
- `kv260-whiteboard-enhance/.gitattributes`
- `test_workspace/imx219_team_package_20260928/imx219_rgb_rectify_20260928/.gitignore`
- moved repository metadata from `kv260-whiteboard-enhance/.git/` to workspace root `.git/`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- this session record

## Remaining Work
Review the initial candidate list before the first commit. Configure author identity and remote URL when provided. The nested `imx219_reference_2026-09-24` repo can be backed up separately or added as a submodule once its remote is known.

## Handoff Notes
Current candidate files total about 13 MB; Git status has not staged or committed them. Additional test projects can be allowlisted after checking source and generated-output boundaries.
