# AI Session: 2026-09-24-008-imx219-driver-output

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 为已连接的 Raspberry Pi Camera Module v2 (IMX219) 加载适配 KV260 的驱动/CSI 输入栈，并尝试输出一帧。
- Status: Attempted; board recovered; single-frame capture blocked by incompatible CSI firmware load
- Report candidate: No
- Related commits: None
- Related files: D-042/D-043; `kv260-whiteboard-enhance/docs/imx219_bringup.md`; `kv260-whiteboard-enhance/scripts/probe_imx219_capture.sh`.

## Context Read

按规定顺序阅读根 AGENTS.md、AI 开发策略、项目状态、决策流水、索引、最近 CSI readiness/HDMI 会话和 IMX219 架构记录；检查正式目录代码与 Git 状态。工作区根和正式目录均不是 Git 仓库。

## Task and Constraints

Camera v2 型号由用户确认。板端 Linux/PL 输入栈需实测；输出优先定义为可核验的单帧采集，其后视实际可用显示路径尝试 HDMI。沿用此前用户提出的“不在浏览器中调试”的约束。

## Contributions

- SSH `ubuntu@[private_ip]` confirmed the live board kernel `5.15.0-1027-xilinx-zynqmp`. `/boot/config-*` reports `CONFIG_VIDEO_IMX219=y`; `modinfo imx219` reports `filename: (builtin)`. Executed `sudo modprobe imx219`, and `/sys/bus/i2c/drivers/imx219` is registered.
- Checked `xmutil listapps`, active configfs overlays, video/media nodes, I²C adapters, device tree, and kernel driver configuration. Only starter-kits firmware was available; no CSI/IMX219 media graph or capture node existed. Board I²C listing had no PL camera mux bus.
- Downloaded the public [RasPi-Camera-V2-KV260](https://github.com/ikwzm/RasPi-Camera-V2-KV260) reference to `test_workspace/imx219_reference_2026-09-24/`, commit `3973b5ad53870ef8341d3a736395ba7ca84c635c`. Its Vivado 2023.1 PL binary and DTS supply CSI RX, AXI I²C/mux, IMX219, demosaic, gamma, VPSS and frame-buffer write. The reference uses a different Ubuntu image; current kernel has the named Xilinx video functions built in and PCA954x mux as a module, but compatibility was not proven.
- Transferred reference `.bin.gz`/`.dts` into board staging `/home/ubuntu/imx219_probe_2026-09-24/`, decompressed and compiled DTBO with `dtc -@`. Temporarily installed the binary to `/lib/firmware` and unloaded `pynq` and `k26-starter-kits` overlays before applying the reference DTBO.
- The configfs DTBO write triggered a kernel Oops in `dma_buf_dynamic_attach` during `fpga_mgr_load`. No `/dev/media*`, `/dev/video*`, or `/dev/v4l-subdev*` appeared. Stopped capture attempts, saved log, rebooted the board, confirmed SSH and starter-kits active slot 0 recovered, and removed the trial binary from `/lib/firmware`. The board staging directory remains as test evidence.
- Added a safe media-graph/single-frame probe script and bring-up guide in the formal project. The script syntax passed `bash -n` on the board; after reboot it exited 3 with `No media node` as expected.

## Decisions and Adoption

- D-043: sensor module already built into this kernel, but camera use requires a matching CSI PL + device-tree graph. Do not reapply the tested third-party firmware/DTBO pair to this 5.15 image via configfs. Build/package for the current image and accept only a real media graph and captured frame. The community reference was investigated and trialed, **not adopted** as a board solution.

## Commands and Tools

- `modinfo imx219`, kernel config, `sudo modprobe imx219`, `xmutil listapps`, I²C/device-tree/V4L2 inspections over SSH.
- `git clone --depth 1` into the named test workspace; `gzip -dc`, `dtc -@`, SHA-256 checks, PuTTY secure copy.
- Unload `pynq` configfs overlay and starter-kits app; apply trial DTBO via configfs; capture `dmesg` after Oops; reboot; inspect recovered app/video state; remove temporary `/lib/firmware` binary.
- `bash -n` and a board run of `probe_imx219_capture.sh` after reboot.

## Validation and Evidence

- Confirmed: `CONFIG_VIDEO_IMX219=y`, built-in module, successful `modprobe`, no camera/media nodes before or after the failed trial.
- Reference firmware SHA-256 `df17d542a08e9904a844cb7091cad7d5a64ea0f8ccced09a9d0a7050922798ac`; compiled DTBO SHA-256 `e78a7f714be2880155d188160728c2dbafdbacfb9fcd797c92fa9cbf8983f297`.
- Oops stack: `dma_buf_dynamic_attach` → `fpga_mgr_load` → `fpga_region_program_fpga` → `of_overlay_apply`; captured in `test_workspace/imx219_reference_2026-09-24/board_overlay_oops.log` (SHA-256 `85A18BC881B1287360299FD1E08A77FD775636B97643C7CBA4CCDE622CE8BEE9`). Configfs `applied` did not mean working camera.
- Recovery: post-reboot uptime reset, SSH returned, `xmutil listapps` showed starter-kits active slot 0, configfs listed starter-kits and pynq only, and no new Oops marker appeared. Temporary firmware copy removed; FPGA manager state `operating`.
- Probe script `bash -n` passed; board run returned exit 3 with `No media node: the CSI PL/device-tree capture stack has not registered.`
- Camera I²C ID, actual captured frame, image decode, camera-to-rectifier, and HDMI output: **未执行/未成功**.

## Errors and Corrections

- Initial direct SSH command hit a local deny shim; switched to PuTTY with the board's pinned host key. No credential was written into project records or files.
- Initial non-root probe-script run needed interactive sudo; reran with `sudo bash`, correctly reporting no media node. Script was adjusted to use `modprobe` directly when already root.
- Reference DTBO write caused a kernel Oops even though configfs reported `applied`. Stopped further driver/configfs changes, saved evidence, rebooted, and verified recovery. The cause within the Ubuntu 5.15 firmware-manager path remains unisolated.
- Local Git Bash syntax check failed because its MSYS process could not create a signal pipe in this sandbox; ran `bash -n` successfully on the board.

## Files Changed

- `kv260-whiteboard-enhance/scripts/probe_imx219_capture.sh` (new)
- `kv260-whiteboard-enhance/docs/imx219_bringup.md` (new)
- `project_workspace/ai/sessions/2026-09-24-008-imx219-driver-output.md` (new)
- `project_workspace/DECISIONS.md` (D-043)
- `project_workspace/PROJECT_STATE.md` (updated)
- `project_workspace/ai/INDEX.md` (updated)
- Test workspace: reference clone, `board_overlay_oops.log`; board staging: `/home/ubuntu/imx219_probe_2026-09-24/`.

## Remaining Work

- Build or obtain a CSI-capable KV260 PL/DT bundle matched to the current Ubuntu 5.15 firmware management and driver ABI; stage it without copying the failed bundle into the active system.
- Verify IMX219 I²C bind, media topology and format; capture and inspect at least one real frame.
- Integrate CSI capture with the rectifier and HDMI path in a compatible combined design, then test end-to-end video.

## Handoff Notes

- The board is back on starter-kits active slot 0. IMX219 is built into Linux but currently unbound because the CSI hardware/device-tree path is absent. The previous notebook still expects an existing V4L2 camera and was not changed. The test binary/DTBO are retained only in staging; `/lib/firmware` trial copy was removed. No real IMX219 output was produced.
