# AI Session: 2026-09-29-008-kv260-camera-timeout

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Diagnose and recover the one-click deployment failure where RAW8 camera smoke times out waiting for its first frame.
- Status: Diagnosed capture hardware path failure; live application remains stopped
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/scripts/kv260_board_run.py`, `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/software/run_pipeline.py`

## Context Read

Read `AGENTS.md`, AI development policy, project state, decisions, index, recent flat deployment and display diagnosis sessions, then current Git status and relevant code.

## Task and Constraints

Owner supplied a failed `run.sh deploy` transcript. Preflight, FPGA manager load, PYNQ metadata registration, CMA allocation, and 1920x1080 RGB3 media setup succeeded. Five-frame no-display smoke timed out before the first frame; automatic full-load retry is disabled. Locate the camera or capture failure and restore the deploy path without mislabeling display mode as the direct cause. Do not record credentials.

## Contributions

- Connected to the board after verifying its SSH ED25519 fingerprint against the existing local known-host entry. No credential was recorded.
- Confirmed the deployed media graph is connected end to end: IMX219 RAW8 1920x1080 -> CSI RX -> demosaic -> gamma -> CSC -> scaler -> `/dev/video0` RGB3 1920x1080. No managed `run_pipeline.py` process is active.
- Independent `v4l2-ctl` captures also timed out. This excludes the Python `V4l2RgbStream` reader and the 1080p display configuration as the direct causes of the smoke failure.
- Kernel repeatedly reported `xilinx-csi2rxss ... Stream Line Buffer Full!`. The CSI RX register after failure showed VC0 RAW8 data type `0x2a`, line byte count 1920, and line count 13. The sensor is delivering data, but the downstream video stream stalls before a complete frame reaches the framebuffer writer. The framebuffer interrupt count was initially zero.
- Read the active framebuffer-writer registers during capture: 1920 width, 1080 height, stride 5760, RGB format register `0x14`, and control `0x81`; the stage was configured and started but did not complete a frame. All media links were enabled. The precise blocking IP in the chain remains unisolated.
- Reprogrammed the same FPGA design once and reduced IMX219 vertical blanking from 1648 to 20000 for an isolated capture attempt. Five-frame `v4l2-ctl` capture still timed out and the CSI line-buffer-full alert recurred. Restored vertical blanking to 1648 afterward.
- Manual PYNQ metadata registration initially failed because the diagnostic shell omitted the runner's PYNQ `PATH`; reran registration with the normal environment and it succeeded. The FPGA manager reports `operating`; `run.sh status` reports the last managed PID 6330 is no longer alive.
- The current bitstream SHA-256 matches the `.previous` package's bitstream, so package rollback would not substitute different camera hardware logic. The build's previously recorded WNS is -5.589 ns. The worst path ends in the AE status meter side branch, so that number alone does not identify the direct video-stream blockage. The physical video chain also contains an AXI subset converter that is not represented as a V4L2 media entity; exact stage isolation needs hardware trace.

## Decisions and Adoption

- Adopt D-061: keep five-frame camera smoke as a required deployment gate. Do not bypass it, increase the Python read timeout as a purported fix, or blindly repeat FPGA loads after this hardware-stream failure. The next design revision should close timing and provide a verified CSI/downstream reset strategy, then repeat independent capture before the full live application.

## Commands and Tools

- Board: `media-ctl -d /dev/media0 -p`, `v4l2-ctl --all`, independent `v4l2-ctl --stream-mmap=3 --stream-count=3/5`, `journalctl -k -b`, `/proc/interrupts`, read-only `/dev/mem` register probes, one controlled FPGA reload, sensor blanking trial, PYNQ metadata registration, and `run.sh status`.
- Read Xilinx `xilinx-csi2rxss.c`, `xilinx-gamma.c`, and `xilinx_frmbuf.c` register/interrupt behavior plus AMD PG232. The CSI driver identifies stream line-buffer-full as downstream backpressure and disables the CSI core on that interrupt.

## Validation and Evidence

Owner's transcript: `TimeoutError: Camera produced no frame` at `run_pipeline.py:132`, after `Format Video Capture Multiplanar: 1920/1080 RGB3` and `vertical_blanking: 1648`.

- Independent capture with `--stream-poll` reported `select timeout`; 30-second non-poll capture also exited by timeout, with no complete frame.
- CSI register `0x60=0x000d0780` encodes 13 lines and 1920-byte line count; `0x64=0x2a` is RAW8 data type. Register `0x00=0` after overflow reflects the disabled CSI core. Framebuffer writer programmed width `0x780`, height `0x438`, stride `0x1680`, and control `0x81` during capture.
- 20000-line vertical blanking and one same-bitstream FPGA reload did not restore capture. FPGA manager remained `operating`, and PYNQ metadata registration was restored. Physical screen and full cold reboot after this incident: 未执行.

## Errors and Corrections

- An initial manual metadata registration omitted the PYNQ virtual environment from `PATH`, so PYNQ could not generate its temporary xclbin. Repeated only metadata registration with the runner's environment; it succeeded. This error happened after successful FPGA programming and did not explain the camera timeout.
- Overlapping background capture probes briefly produced `Device or resource busy`; subsequent isolated capture still timed out. The diagnostic probes were stopped before final status checks.
- The trial sensor blanking was restored to the package default 1648. No application process was restored because independent capture remained blocked.

## Files Changed

- `project_workspace/ai/sessions/2026-09-29-008-kv260-camera-timeout.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`

## Remaining Work

Isolate the exact downstream IP/clock/reset fault using a timing-closed build or hardware trace; verify raw capture before redeploying. Current board app is stopped. A full power-cycle after this failure was not performed.

## Handoff Notes

The current blocker is the PL camera-processing stream: CSI receives RAW8 lines but reports downstream backpressure after about 13 lines, and `/dev/video0` never receives a complete frame. The 1080p EDID/mode fix remains in the package but is not reached by failed smoke. `run.sh status` is `alive: false`; FPGA manager is `operating`; sensor blanking is restored to 1648. Do not report the deployment as successful.
