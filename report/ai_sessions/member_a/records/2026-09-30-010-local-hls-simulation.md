# AI Session: 2026-09-30-010-local-hls-simulation

- Date: 2026-09-30
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Run the supplied C handoff's two newer HLS kernels locally and present visible results.
- Status: Completed; both current arithmetic kernels passed C simulation, synthesis and Verilog C/RTL co-simulation
- Report candidate: No
- Related commits: None
- Related files: `test_workspace/hls_c_handoff_20260930/`; supplied C handoff snapshot.

## Context Read

Project AGENTS.md, policy, state, decisions, index and session 009 were read in this conversation. Current source, testbenches and scripts were reviewed. Local tool discovery found Vitis HLS 2022.2 at `E:/Xilinx/Vitis_HLS/2022.2/`, whereas supplied scripts target Vitis 2025.2. Git has no commits; project/test trees are untracked.

## Task and Constraints

User explicitly requests actual local simulation and visible results. Keep build products in the named ASCII test directory. Preserve delivered source. Do not claim hardware validation.

## Contributions

Prepared a 2022.2 Tcl flow and PowerShell entry point in the isolated test directory, copied unmodified algorithm/testbench source from the supplied snapshot, and ran both current kernels (`block_diff_w1` and `block_state`). Generated HTML/PNG/JSON and complete output NPZ evidence by decoding the actual RTL AXI-memory output files and comparing them with Python golden vectors. Did not substitute Python results for actual RTL output in the figures.

## Decisions and Adoption

D-062 records local reproduction with installed Vitis HLS 2022.2. Results are identified separately from supplied 2025.2 evidence. No production interface or architecture changed. The Python dependency versions differ from the delivery's suggested pins, but both generated golden-vector hashes exactly match the recorded hashes.

## Commands and Tools

Tool/path discovery and source/testbench reads. From workspace root:

```powershell
& './test_workspace/hls_c_handoff_20260930/run_hls.ps1' -Kernel block_diff_w1 -Steps full -Python 'C:\Users\why\AppData\Local\Programs\Python\Python39\python.exe'
& './test_workspace/hls_c_handoff_20260930/run_hls.ps1' -Kernel block_state -Steps full -Python 'C:\Users\why\AppData\Local\Programs\Python\Python39\python.exe'
python test_workspace/hls_c_handoff_20260930/make_report.py
```

Tool runs used normal sandbox escalation approval after MSYS signal-pipe creation was denied in the sandbox. The initial failed/interrupted run is preserved separately; only the two completed passing runs below are evidence.

## Validation and Evidence

| Kernel | Directed / Golden | C sim | HLS synth | RTL cosim | Compared golden outputs | Mismatches |
|---|---:|---|---|---|---:|---:|
| block_diff_w1 | 8 / 5 | PASS | Completed | Verilog PASS, 13 calls | 50,916 | 0 |
| block_state | 10 / 18 | PASS | Completed | Verilog PASS, 28 calls | 163,620 | 0 |

Runs: `test_workspace/hls_c_handoff_20260930/runs/block_diff_w1-20260930-195003-056/` and `runs/block_state-20260930-195031-411/`.

- All 23 golden cases, including full 120×68 grids/1080p sampling edges, match Python; all fields compared directly against RTL memory dumps. Combined 214,536 scalar outputs, 0 mismatches. Original C/RTL post-checks also PASS.
- Generated-vector hashes are unchanged: diff `8414b2e4c2872b568754c4c67f1021646708b8e97882a8a1d36017213b6f729e`; state `87cd6a27686bfb7b888518e24db372a7a0dbcce2e88a39d80f9abad398cc971c`.
- HLS estimates: diff BRAM18/DSP/FF/LUT = 0/10/6394/11986; state = 25/5/6624/10470. Estimated clock 7.3 ns for both with 10 ns target. Estimated maximum latency 587522 / 685806 cycles. These differ from supplied 2025.2 estimates; tool versions and defaults matter.
- Observed RTL latency min/avg/max: diff 78/52633/658154; state 84/48504/517068 cycles. These are current testbench/model observations, not worst-case DDR/board bounds. Diff sample loop requests II=1 and gets final II=3.
- `results/summary.json`: per-case comparison, reports and output-file hashes; `results/*_outputs.npz`: actual RTL and golden arrays; `results/report.html`: visible report; `results/rtl_comparison.png`: representative E/M/TTL maps.
- Figure visually inspected using view_image: expected and RTL maps align, zero-difference maps uniformly light green, Chinese text legible. Fixed one unsupported arrow glyph before final rendering.
- Python 3.9, NumPy 1.21.2, OpenCV 4.5.5, Pillow 9.0.1, Matplotlib 3.5.1. No dependencies installed or global environment changed.
- IP export, system integration, routed timing, hardware execution and real-video quality/1080p30 validation: 未执行. Legacy block_diff/block_ttl were not rerun; this task ran the two current superseding arithmetic kernels.

## Errors and Corrections

1. Initial sandboxed Vitis wrapper failed with MSYS `couldn't create signal pipe, Win32 error 5`; stopped it. Ctrl-C produced exit code 0 despite no valid completion. Added explicit C-sim and cosim PASS-report checks so the reproduction wrapper does not rely solely on exit code. Normal approved unsandboxed reruns succeeded. Failed run directory remains preserved, never counted as PASS.
2. Initial RTL dump parser treated the generated trailing `0x5a5aa5a50f0ff0f0` marker as another memory length and rejected it as truncation. Checked generated AESL Verilog write_binary/end-marker logic, recognized the marker, and reran parsing. Asserted full transaction counts and exact golden comparisons; all outputs match.
3. One broad text read accidentally printed binary memory payload and was truncated; later reads used bounded binary decoding. No secret environment log was inspected.

## Files Changed

- `test_workspace/hls_c_handoff_20260930/run_hls.ps1`
- `test_workspace/hls_c_handoff_20260930/run_hls.tcl`
- `test_workspace/hls_c_handoff_20260930/make_report.py`
- `test_workspace/hls_c_handoff_20260930/README.md`
- Generated `runs/` and `results/` evidence within that test directory.
- This session, `project_workspace/ai/INDEX.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`.

The supplied delivery source and formal project source were not changed.

## Remaining Work

Current requested simulations and visible results are complete. System video integration and board verification remain separate future work. If performance optimization is needed, inspect the shared AXI byte-read pattern causing final II=3; do not interpret arithmetic PASS as a throughput claim.

## Handoff Notes

Open `test_workspace/hls_c_handoff_20260930/results/report.html` for case-by-case results and the actual RTL comparison figure. Reproduction commands are in the local README. Completed run sources are unmodified and vectors match supplied manifests; 2022.2 synthesis numbers belong to this new experiment. No board programming performed.
