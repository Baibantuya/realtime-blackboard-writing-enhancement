# Session Record: 2026-10-18-005 v19 Live Pipeline Start & End-to-End Execution

- **Date**: 2026-10-18
- **Participants**: AI (Antigravity), User
- **Task Objective**: 启动 KV260 板端正式白板增强全链路（Live Pipeline），执行真实端到端视频流采集、透视校正、遮挡恢复、量化输出及实机运行监控。
- **Hardware & Environment**:
  - Target Board: KV260 (`ubuntu@[private_ip]`)
  - Bitstream: `imx219-quality-ila.bit` (v19 200MHz fixed, Hardware Hash: `25fed13321efe203c81f19c54fa414ba04e5c3d77db6baa0c1b03fac1c1ccb1c`)
  - Runtime App: `/home/ubuntu/kv260_apps/whiteboard_candidate`
  - Live Process PID: `47366` (background daemon logging to `live.log`)

---

## 1. Startup & Deployment Execution
- **Deployment Invocation**: `sudo python3 /home/ubuntu/kv260_apps/whiteboard_candidate/kv260_board_run.py deploy`
- **Preflight & Manifest Verification**:
  - `verify_manifest.py`: `PASS` (51 files verified, SHA256 integrity check PASS)
  - `kv260_overlay.py --check-only`: `CHECK_PASS`
- **FPGA Overlay Reload**:
  - Unloaded old app via `xmutil unloadapp`
  - Loaded bitstream through FPGA manager in `1094 ms`: `BIN FILE loaded through FPGA manager successfully`
  - PYNQ metadata registered, CMA allocated (`0x34e9000`).
- **Media Setup & Sensor Photometry**:
  - `configure_restore_capture.py` configured IMX219 sensor flip (`hflip=1, vflip=1`), SBGGR8 raw format, fixed exposure (2724) and gain (205).
- **Smoke Suite Verification**:
  1. `board_pipeline_acceptance.py`:
     - Test patterns (black, white, red, green, blue) all returned `median_rgb` exact matching, `result: PASS`.
     - 1000-frame continuous streaming test: `captured=1000, sampled=942, bad_frames=0, sequence_gaps=0, camera_fps=29.917 FPS, RESULT=PASS`.
  2. `board_stage_acceptance.py`:
     - 3-frame full-pipeline test (Rectify -> Restore -> Quantize) with 100% pixel parity against reference models:
       - Frame 0: `PASS`
       - Frame 1: `PASS`
       - Frame 2: `PASS`
     - Feature check: `result: V15_PL_FEATURES_PASS` (quantizer semantic cases: 4, clear_scene_epochs: 2, static_person_protected: true, white_shirt_protected: true).

---

## 2. Live Steady-State Runtime Monitoring
- **Steady-State Statistics (at elapsed_s = 67.8s)**:
  - **Camera Ingress**: 1948 frames captured (~29.9 FPS raw ingress).
  - **Processed & Displayed Frames**: 827 frames.
  - **Output Frame Rate**: **12.2 FPS** (持续稳定输出至 DisplayPort).
  - **Bad Frames**: **0** (零坏帧).
  - **Per-Stage Hardware Latency**:
    - Rectify (透视变换): **21.9 ms**
    - Restore (遮挡恢复): **58.8 ms**
    - Quantize (调色量化): **10.9 ms**
  - **Memory & Scanout**:
    - `scanout_cpu_copies: 0` (Zero-copy DRM/KMS Direct Scanout).
    - CMA DMA-BUF imported cleanly into DisplayPort and Scaler buffers.
  - **Whiteboard Geometry**:
    - Whiteboard corners detected and locked: `[[533.9, 208.1], [1919.0, 211.7], [1919.0, 691.6], [526.1, 684.4]]`.
    - `geometry_restore_safe: true`.
- **Kernel Health**:
  - `dmesg`: 0 buffer full alerts, 0 errors.
