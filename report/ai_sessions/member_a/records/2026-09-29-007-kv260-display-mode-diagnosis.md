# AI Session: 2026-09-29-007-kv260-display-mode-diagnosis

- Date: 2026-09-29
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: Diagnose why the KV260 Linux desktop currently uses a 768-line mode while the same monitor supports 1080p on a PC.
- Status: Cold-boot and deploy regressions reproduced. The EDID can be absent, GNOME can restore 1024x768 after startup, and the PYNQ app itself previously selected its largest exposed mode (1024x768). Added a resident GDM mode monitor and updated the actual deployment package's `run_pipeline.py` to install a validated CTA 1080p EDID fallback when the kernel EDID is empty and explicitly require 1920x1080. One-click deploy completed successfully; live log, PYNQ mode list, RandR, DRM state, and process status all confirmed 1920x1080, with PID 6330 alive. Final full cold boot and external visual/capture measurement remain unverified.
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/DECISIONS.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/ai/INDEX.md`

## Context Read

- Read `AGENTS.md`, `project_workspace/ai/AI_DEVELOPMENT_POLICY.md`, `project_workspace/PROJECT_STATE.md`, `project_workspace/DECISIONS.md`, `project_workspace/ai/INDEX.md`, and the recent display-mode/rollback session in order.
- Read the candidate runner and board handoff docs. Candidate uses PYNQ `DisplayPort()`; prior board readback showed `DP-1`, EDID 0 bytes, and maximum 1024x768.
- Checked Git status; the workspace is the initial uncommitted repository and no tracked changes were present.

## Task and Constraints

- Owner reports the KV260 is recovered and the Linux desktop appears at 768-line resolution; same monitor produces 1080p when connected to a PC.
- Inspect current board display state without changing its configuration.
- Do not infer monitor capability from only the board's mode list; do not claim a hardware failure without isolating the output connector and EDID route.

## Contributions

- Verified the direct-link board SSH host key against the cached ED25519 key, then performed read-only board inspection.
- Current `/proc/cmdline` contains no `video=DP-1:1920x1080...` force argument, confirming the rollback is active.
- Current `/sys/class/drm` exposes one connector, `/sys/class/drm/card0-DP-1`; status is `connected`, its EDID file is 0 bytes, and its advertised modes are `1024x768`, `800x600` (twice), `848x480`, and `640x480`.
- `/sys/class/graphics/fb0/virtual_size` reads `1024,1536` (virtual framebuffer height is double the 768-line scanout). GDM has an X11 local seat session.
- The immediate software-level blocker is the board's DRM mode set: it has no 1920x1080 mode for the desktop to choose. Missing EDID or a source/bridge that does not supply one explains why the driver's available list remains conservative. The same mode limitation was observed before rollback and is now reconfirmed after recovery.
- Official AMD UG1089 identifies two distinct carrier-card video connectors, J5 HDMI and J6 DisplayPort. Official Xilinx KV260 BIST documentation states that that test's EDID read comes from the KV carrier's DP splitter rather than directly from the monitor; this is evidence that a board-side splitter/EDID path is in the display chain, but does not by itself identify the exact Linux DRM cause.
- Owner clarified that the display is connected to the KV260 HDMI output (AMD UG1089 identifies carrier-card J5 as HDMI; J6 is DisplayPort). This rules out the possibility that the owner simply selected the DP connector physically, but the Linux DRM name remains `DP-1`.
- AMD's KV260 product details list one HDMI 1.4 interface and one DisplayPort 1.2a interface. UG1089 also describes Vitis platforms with display to DisplayPort and/or HDMI and 1080p30 video support. This establishes platform-level 1080p capability in supported designs, not a guarantee that the currently booted desktop setup enables it.
- With physical HDMI confirmed and EDID still empty, the likely fault domain is the KV260 HDMI/DP-splitter EDID path or its Linux DRM mode discovery/configuration. The exact block/component is not isolated; the documented BIST EDID source is not the monitor itself.
- Follow-up driver inspection: kernel `5.15.0-1027-xilinx-zynqmp` has `CONFIG_DRM_ZYNQMP_DPSUB=m`, and the `zynqmp_dpsub` module is bound to live DT node `xlnx,zynqmp-dpsub-1.7` (`status=okay`). Its `i2c-2` adapter is named `ZynqMP DP AUX`. The DRM connector remains `DP-1 connected`, EDID is 0 bytes, and the kernel exposes only 1024x768/800x600/848x480/640x480. This shows the display driver is loaded and detects hot-plug, but its current mode-discovery path has not obtained the sink EDID.
- Kernel journal for the current boot has no useful `dpsub`/AUX/EDID failure message. Xorg log records Pixman scanout and DRI2 flip errors, but no evidence ties them to the 1024x768 mode. The serial boot output from the earlier recovery contains `zynqmp_clk_divider_set_rate() set divider failed for dpdma_ref_div1, ret = -13`; its relationship to this mode limit is unproven.
- The owner supplied the `kv260_vcuDecode_vmixDP` platform capability. AMD UG1089 confirms this is a Vitis platform with VMIX to DisplayPort and/or HDMI and 1080p30 per stream. The official `aibox-reid` overlay DTSI for that platform adds a `v_mix` node and bridges it into `zynqmp_dpsub` through VTC; these nodes are absent from the currently live device tree. Thus that platform description establishes capability of that specific loaded PL design, not the current stock desktop's mode list. Current FPGA manager state is `operating`, but `xmutil listapps` could not identify the loaded application because its socket returned permission denied.
- `CONFIG_DRM_XLNX_HDMITX` is not set in this kernel, but the cited VMIX platform uses the ZynqMP DisplayPort subsystem as its display bridge; this config symbol is for a separate Xilinx HDMI-TX IP driver and its absence alone does not explain the HDMI/J5 desktop's missing EDID.
- Root run-time discriminator: `sudo i2ctransfer -y 2 w1@0x50 0x00 r128` and offset `0x80` each returned a full 128-byte EDID block over the live `ZynqMP DP AUX` adapter. Both EDID checksums are valid (sum modulo 256 = 0); base block advertises one CTA extension, and its detailed timing/CTA VIC include 1920x1080 at 60 Hz. The one-byte DDC probe also returned `0x00`; debugfs connector force was `unspecified`, and EDID override was empty.
- Before the desktop refresh, `/sys/class/drm/card0-DP-1/edid` was 0 bytes and kernel modes were fallback 1024x768 and below. Xorg uses the `armsoc` DDX; startup log at uptime 41.334s says it probed only fallback modes and selected 1024x768. Later, after a read-only `xrandr --query` in the GDM session, Xorg logged `EDID vendor "RTK", prod id 9557` and DDC modelines including 1920x1080; kernel EDID became 256 bytes, kernel KMS state became 1920x1080@60, and a subsequent xrandr query reported current 1920x1080@60. This demonstrates that the physical EDID/AUX route and the 1080p output path work, while the initial probe state was stale/incomplete.
- After the owner explicitly requested persistence, installed `/usr/local/sbin/kv260-display-1080p.sh` and `/etc/systemd/system/kv260-display-1080p.service`, then enabled it under `graphical.target`. The service runs as GDM after `gdm.service`, retries EDID/mode discovery for up to 120 seconds, leaves an already-active 1080p mode alone, and selects `DP-1` 1920x1080@60 when the mode becomes available. No U-Boot script, kernel command line, driver, or EDID data was changed.
- Validated the activation path without reboot: temporarily changed the live desktop from 1920x1080 to 1024x768, manually started the enabled service, and confirmed it restored 1920x1080@60. `systemd-analyze verify` passed; `systemctl status` reported enabled and exit status 0/SUCCESS. Actual boot ordering after a restart remains untested.
- Performed one real reboot after installing the service. The board returned on SSH; `systemctl status` showed the service enabled, started at boot 05:41:48, completed at 05:41:56 with exit 0/SUCCESS, and logged `1080p is already active`. A post-boot GDM `xrandr --query` confirmed current 1920x1080@60. The board's original U-Boot script and kernel command line remained unmodified.

## Decisions and Adoption

- Confirm D-056's immediate diagnosis: in the current Linux system, missing EDID plus a DRM mode list capped at 1024x768 is the direct reason the desktop cannot select 1920x1080.
- Do not repeat the unverified boot-script `video=` experiment. The owner has confirmed J5 HDMI; compare EDID/modes on J5 and J6 DP and inspect the board/BIST EDID route while preserving the restored boot script.
- The original GDM service only waited for EDID; the owner later performed a full cold boot and reproduced the failure. A one-shot CTA modeset fixed the missing EDID mode, but the GDM greeter's GNOME Shell then restored 1024x768. Replace the one-shot with a resident GDM service that adds the already-read-from-monitor CTA 1080p60 timing and reasserts it whenever another desktop component changes the mode. Do not change U-Boot or kernel arguments.
- The PC success establishes that the monitor can display 1080p on the PC's path, but does not validate the KV260's source, board splitter, connector route, EDID, or Linux driver path.
- Revised diagnosis after the owner's cold boot: this boot did not recover the EDID; `/sys/class/drm/card0-DP-1/edid` stayed at 0 bytes and `i2ctransfer -y 2 w1@0x50 0x00 r128` failed with `Remote I/O error`. This session cannot prove which physical or driver element prevents DDC discovery. The original wait-only service could never create a 1080p mode in that state.
- The monitor EDID read successfully on an earlier boot advertised CTA 1920x1080@60. Registering its standard timing (`148.50 MHz`, totals `2200x1125`) through RandR was accepted by Xorg/KMS while EDID remained empty; DRM atomic state then showed active 1920x1080 at a 148.5 MHz pixel clock. This validates software modeset acceptance, not an external measurement of the HDMI waveform.
- The owner later reported that running the installed one-click `run.sh` returned the display to 768p. Inspection of its `run_pipeline.py` showed `mode = max(display.modes, ...)`; PYNQ's live modes were 1024x768/800x600/848x480/640x480 when kernel EDID was unavailable, so `DisplayPort.configure()` explicitly programmed 1024x768. The XrandR desktop helper and PYNQ's direct DRM output are separate paths; xrandr could report 1920 while DRM atomic state and PYNQ output were 1024x768.
- Linux v5.15 DRM `edid_override` accepts a raw EDID blob and updates the connector EDID property. A locally generated 128-byte EDID with the previously validated 1920x1080@60 detailed timing was written to `/sys/kernel/debug/dri/0/DP-1/edid_override`; checksum was 0 and PYNQ then enumerated only `[(1920, 1080, 60)]`. This successful runtime check is why the deployment code uses a debugfs override when the physical EDID file is empty.
- Modified the exact package source selected by `project_workspace/kv260_deploy.local.json`: `test_workspace/design_1_full_deployment_20260928/design_1_full_deployment_20260928/software/run_pipeline.py`. It installs the synthetic EDID only when the connector is connected and kernel EDID is empty, selects exactly 1920x1080, and fails clearly rather than silently selecting a lower mode. Package deployed using `python kv260-whiteboard-enhance/scripts/deploy_to_kv260.py deploy`; board installer accepted the checksums, smoke run completed, FPGA manager loaded successfully, and live pipeline started at PID 6330.
- Answer to owner: yes, the KV260 hardware/platform can output 1080p under a supported design; the current Linux desktop's active KMS path is not exposing 1080p.

## Commands and Tools

- Read-only SSH checks: `/proc/cmdline`, `/sys/class/drm`, each connector `status`, EDID byte count and `modes`, `/sys/class/graphics/fb0/virtual_size`, `loginctl show-session`.
- Read-only driver checks: kernel and module version/config, platform-device binding, live device-tree nodes, DP AUX adapter name, kernel journal, Xorg log, and FPGA-manager state. `xmutil listapps` was attempted but returned socket permission denied; app identity remains unknown.
- Read-only local TCP check found the direct Ethernet board path at `[private_ip]` active; SSH host key matched the cached known-host entry.
- Cold-boot follow-up checks: `journalctl -b -u kv260-display-1080p.service`, `i2cdetect -y 2`, `i2ctransfer -y 2 w1@0x50 0x00 r128`, RandR queries as GDM, connector sysfs, and `/sys/kernel/debug/dri/0/state`.
- Reversible live recovery used `xrandr --newmode`/`--addmode` with the CTA 1080p60 timing, then `xrandr --output DP-1 --mode 1920x1080_60`; persistence test switched to 1024x768 and started the enabled systemd service.
- Web lookup of AMD UG1089 (interfaces/Vitis platforms), Xilinx KV260 BIST display docs, and Linux DRM/EDID documentation.
- Persistent config deployment: `/usr/local/sbin/kv260-display-1080p.sh`; `/etc/systemd/system/kv260-display-1080p.service`; enabled symlink `/etc/systemd/system/graphical.target.wants/kv260-display-1080p.service`.
- Deployment package rebuilt and installed from `project_workspace/kv260_deploy.local.json`'s `package_dir`; one-click command `python kv260-whiteboard-enhance/scripts/deploy_to_kv260.py deploy` ran the board's `/home/ubuntu/kv260_apps/whiteboard_candidate/run.sh deploy`.

## Validation and Evidence

- Live board readback after recovery first showed `DP-1 connected`, EDID length 0, and only fallback modes; after the successful DDC refresh it showed EDID length 256, mode list including 1920x1080, and current 1920x1080@60 in both Xorg RandR and DRM atomic state. Kernel command line remains free of a forced mode.
- Persistent service validation: `systemd-analyze verify /etc/systemd/system/kv260-display-1080p.service` returned no diagnostics; systemd reports the service enabled. After intentionally switching the current desktop to 1024x768, `systemctl start kv260-display-1080p.service` completed 0/SUCCESS, logged `selected 1920x1080 at 60 Hz`, and RandR reported current 1920x1080@60. After one full reboot, the enabled service ran at boot, logged `1080p is already active`, and exited successfully; post-boot RandR again reported 1920x1080@60.
- Owner then performed a full cold boot and reported 1080p was lost. This is a genuine regression of the original persistence strategy. On that boot, service attempts exhausted 120 seconds and restarted; live DRM EDID remained 0 bytes, AUX I2C address 0x50 did not ACK, and RandR exposed only fallback modes.
- Toggled the RandR output off/on; EDID remained unavailable and `--auto` selected 848x480. Restored the desktop to 1024x768 before testing a custom timing.
- Registered RandR mode `1920x1080_60` with CTA 1080p60 timing (148.50 MHz; 1920 2008 2052 2200; 1080 1084 1089 1125; +HSync +VSync) and activated it successfully. RandR reported current 1920x1080; DRM atomic state reported active 1920x1080 at 148500 kHz.
- A system restart exposed a second issue: service logged a successful 1080p modeset at 05:41:59, GNOME Shell started at 05:42:00, and later RandR/DRM state was back at 1024x768. No `monitors.xml` setting was found. This places the revert after the one-shot service and during GDM greeter initialization.
- Updated `/usr/local/sbin/kv260-display-1080p.sh` to remain running, add/select the known timing when needed, and check every 5 seconds. Updated the unit to `Type=simple`, enabled `PartOf=gdm.service`, retained `After=gdm.service` and `WantedBy=graphical.target`, and verified it remains enabled. `bash -n` and `systemd-analyze verify` passed. After forcing 1024x768, the resident service restored RandR to 1920x1080 within 7 seconds. Restarting GDM stopped and restarted the helper; after GNOME Shell initialization, the helper reasserted 1080p and RandR remained 1920x1080. Cold boot with this final service version and physical HDMI capture: 未执行。
- After running the original one-click deployment, PYNQ mode enumeration and DRM atomic state showed 1024x768 even while RandR had reported 1920x1080. After packaging the updated source and rerunning one-click deploy with the kernel EDID first reset to absent, live log reported `DisplayPort active at 1920x1080@60; EDID=CTA 1080p60 fallback EDID; modes=[(1920, 1080, 60)]`. `/sys/class/drm/card0-DP-1/edid` became 128 bytes, DRM atomic mode became 1920x1080 at 148500 kHz, RandR current mode was 1920x1080, and `run.sh status` reported live PID 6330. `FPGA_reloaded=True`; bitstream load and deployment smoke proceeded successfully. A visual capture device was not used.
- The kernel's DRM documentation defines the connector EDID property as sink capability data used to expose display information/modes. Link: https://www.kernel.org/doc/html/v6.13/gpu/drm-kms.html
- AMD UG1089 lists separate carrier-card J5 HDMI and J6 DisplayPort connectors. Link: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Interfaces
- AMD KV260 data sheet lists HDMI 1.4 x1 and DisplayPort 1.2a x1. Link: https://docs.amd.com/r/en-US/ds986-kv260-starter-kit/Product-Details
- AMD UG1089 Vitis platform table lists DisplayPort and/or HDMI output and 1080p30 support in NV12 for specified platforms. Link: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vitis-Platforms
- Xilinx KV260 BIST docs state that its display-connectivity test reads EDID from the KV carrier DP splitter, not directly from the monitor. Link: https://xilinx.github.io/kria-apps-docs/kv260/2022.1/bist/1_3/build/html/docs/modules/display.html
- AMD UG1089 lists `kv260_vcuDecode_vmixDP` as supporting VMIX output to DisplayPort and/or HDMI with 1080p30 per stream. Link: https://docs.amd.com/r/en-US/ug1089-kv260-starter-kit/Vitis-Platforms
- Official KV260 `aibox-reid` overlay DTSI for that VMIX platform connects `v_mix` through VTC to `zynqmp_dpsub`; this confirms the platform-level display path design but is not the current stock desktop device tree. Link: https://github.com/Xilinx/kria-apps-firmware/blob/main/boards/kv260/aibox-reid/kv260-aibox-reid.dtsi
- Live driver readback: bound module `zynqmp_dpsub` on `xlnx,zynqmp-dpsub-1.7`, kernel `5.15.0-1027-xilinx-zynqmp`, `i2c-2` named `ZynqMP DP AUX`; kernel EDID file 0 bytes; connector mode list tops at 1024x768. Current live DT has no `v_mix`/VTC nodes. `xmutil listapps` returned permission denied, so current FPGA app identity was not verified.
- Physical measurement with an external meter/capture device and recheck after reboot: 未执行. Current software state confirms a 1920x1080@60 modeset, but does not establish boot-to-boot persistence.
- Root-only DRM debugfs state, EDID/AUX transaction trace, BIST EDID comparison, and exact loaded FPGA application: 未执行.

## Errors and Corrections

- A local SSH shim rejected the first direct SSH invocation; switched to PuTTY Plink and verified its host key against the cached key before logging in.
- The first stage was read-only. Persistent systemd script/service files were installed only after the owner's explicit request; no U-Boot or kernel boot arguments were touched.
- `xmutil listapps` failed with permission denied on `/tmp/dfx-mgrd.socket`; this is an access limitation, not proof that no application is loaded. No privilege escalation or configuration change was attempted.
- Previous 1080p force attempt had lost remote services after reboot, but the available evidence does not establish that the mode parameter caused that loss. Preserve that uncertainty.
- The earlier statement that one successful ordinary reboot proved persistence was overconfident; a later restart showed the one-shot service ran before GNOME Shell and the greeter reverted to fallback afterward. The resident service now reasserts the known CTA timing every 5 seconds, and GDM restart plus deliberate fallback tests passed. A full power-cycle test after this final correction remains unverified.
- The resident RandR service alone cannot govern the PYNQ application's direct DRM scanout. The application itself chose 1024x768 from PYNQ's mode list and changed the hardware scanout. Corrected the deployment source to supply the validated EDID fallback before constructing PYNQ `DisplayPort()` and to require 1920x1080; the actual one-click package deployment now selects 1920x1080. Physical output measurement remains outside this software verification.

## Files Changed

- `project_workspace/ai/sessions/2026-09-29-007-kv260-display-mode-diagnosis.md`
- `project_workspace/ai/INDEX.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/PROJECT_STATE.md`
- KV260 `/usr/local/sbin/kv260-display-1080p.sh`
- KV260 `/etc/systemd/system/kv260-display-1080p.service` and graphical.target enablement symlink

## Remaining Work

- Record the cable/monitor input path and carrier-board revision if exact hardware isolation is needed. The owner has confirmed HDMI output is in use.
- Verify the resident service after a future cold boot; journal should report `enforced CTA 1920x1080 at 60 Hz` if GNOME changes the mode, and RandR should remain at 1920x1080 after the greeter starts. EDID may remain absent; it no longer blocks the software modeset. Physical HDMI waveform/capture remains unverified.

## Handoff Notes

The current runtime desktop and PYNQ direct DRM scanout are 1920x1080@60. GDM's enabled resident service reasserts RandR mode; deployed `run_pipeline.py` supplies a 128-byte CTA 1080p EDID override if physical EDID is missing and explicitly selects 1920x1080. One-click deployment passed and PID 6330 is alive. Final full cold boot and external HDMI capture remain unverified. The earlier boot-script force-mode experiment remains rolled back and untouched.
