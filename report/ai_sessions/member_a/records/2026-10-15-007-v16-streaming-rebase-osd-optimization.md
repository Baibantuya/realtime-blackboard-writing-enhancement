# Session Record: 2026-10-15-007

- **Task**: v16 算法优化、擦除提交、粗字保护、OSD 移动方位指引、Restore-Quantize 片上 AXI-Stream 直连与部署测试轻量化
- **Date**: 2026-10-15
- **Status**: In Progress
- **Participants**: User, Antigravity AI
- **Target Platform**: KV260 (`xck26-sfvc784-2LV-c`), Vivado / Vitis HLS 2021.2
- **Key Objectives**:
  1. 修复粗字/连笔字被 `white_changed >= 5` 单块打满误杀、人走后仍不显示的问题。
  2. 修复擦除笔迹无法更新至背景缓存造成残留反复闪烁、以及 Clean Rebase 死锁问题。
  3. 抑制背景散粒噪点在白底上的闪烁。
  4. 增加初始化及运行中途黑板移出画框时的白屏与 OSD 移动方位提示。
  5. 砍掉 Restore 与 Quantize 之间的 DDR 环 B，实现片上 AXI4-Stream 直连，大幅提升帧率。
  6. 将 board package deploy 烟雾测试简化（减少测试帧数，加速上板）。

## Root Cause Analysis
1. **粗字/连笔字不显示、人走后仍不显示根因**：
   - 在 `whiteboard_restore.cpp` 中，原有逻辑：
     `if(white_changed >= 5) { o = total_o; mo = total_mo; }`
     在 16x16 单块内（共 16 个采样点，4x4 间隔），任何粗笔画、连笔字或汉字交叉笔画极易覆盖 $\ge 5$ 个点。
     单块内 `white_changed >= 5` 直接将 `o` 暴力拉满至 16/16，触发 `guarded_state` 将该块及其周围 5x5 邻域（80x80 像素）判定为人遮挡（`m_out = 1, w_out = 0`），并将置信度推至 15。
     在 `compose` 中，`displayed[k] = (mask[block] && !ink) ? b : c`，而原代码 `ink` 竟绑定了 `&& writes[block]`。由于 `writes[block] == 0`，导致 `ink` 失效，字迹被永久替换为初始化空白背景 `b`。
     人离开后，黑板上已写字迹与空白背景 `b` 的距离 `db` 依然很大，每帧继续命中 `white_changed >= 5`，死锁无法解除；唯有重启重置背景才能恢复。
2. **擦除痕迹残留反复闪烁根因**：
   - 在 `compose()` 中，背景提交通道仅包含：
     `bool trusted = writes[block] && !mask[block] && !freeze && !is_broad && q >= stable && distance(c,b) <= quiet_delta/2;`
     `committed[k] = (trusted || (ink && q >= stable && !freeze)) ? c : b;`
     当用户擦除粉笔字时，背景 `b` 为亮粉笔字，当前现实 `c` 为暗黑板底色，`distance(c, b)` 很大，且 `ink` 为 false（无笔画），导致 `trusted` 和 `ink` 均为 false。
     擦除后的暗底色物理上无法提交到背景 `b`！背景永远滞留旧粉笔字！
     随后帧中当有人靠近或遮挡抖动时，`displayed = mask ? b : c` 又将旧粉笔字调出显示，造成幽灵字迹反复闪烁。
3. **Clean Scene Rebase 被阻塞根因**：
   - 粗字使 `occ_blocks` 虚高，触发 `reasons |= 2`，导致无人场景依然被判定为人体常驻，无法自动重置。
4. **背景散粒噪点闪烁根因**：
   - Bayer 滤光阵列解马赛克时会将单像素传感器噪点扩为 2x2 斑点，在弱对比度时偶发绕过原单像素 despeckle 逻辑。

## Solutions & Implementation
1. **彻底解除单块粗字误杀**：
   - 废除单块内 `if(white_changed >= 5)` 提升 `o` 与 `mo` 的逻辑；白衣服判定移至全局多块空间连通域 `bulk_white_blocks`。
   - `compose` 中显示字迹 `ink` 解除对 `writes[block]` 的依赖：`bool ink = thin.read() && !is_broad && region[block];`。
2. **增加擦除提交通道（Erase Commit）**：
   - 增加：
     `bool is_erased = writes[block] && !mask[block] && !freeze && !is_broad && (q >= stable) && chalk(b, floor, spread) && !chalk(c, floor, spread);`
     `committed[k] = (trusted || (ink && writes[block] && q >= stable && !freeze) || is_erased) ? c : b;`
     当旧背景为粉笔字、现实已为稳定暗黑板时，强制更新背景，彻底消除擦除幽灵残留。
3. **OSD 白屏与移动方位指引**：
   - 新增 `osd_guidance.py`，全白屏底色上渲染卡片、状态和动态箭头（←、→、↑、↓），指示黑板移入视场中心。
4. **Deploy 烟雾测试压缩**：
   - 测试帧数从 1000 压至 10/3 帧，部署前置验收从 90s 缩短至 3s。

## Verification & Deployment
1. **HLS C/RTL 协同仿真与 IP 导出**：
   - `whiteboard_restore`：`SCENE_REBASE565 PASS static_person white_shirt trusted_frames one_shot epochs=2 tail_guard`，100% 通过 cosimulation，Fmax 预估 132.66MHz。
   - `board_quantize_rgb`：12 组多场景回归向量全部通过（`errors 0`）。
2. **Vivado 2021.2 顶层综合与布局布线**：
   - 配置：`-jobs 16`，多模块 OOC 并行综合。
   - 静态时序结果：`WNS = 0.512 ns`, `WHS = 0.010 ns`, `Setup Failing Endpoints = 0`（**TIMING PASS**）。
   - 资源利用率：CLB LUT 63.03%, Register 37.41%, BRAM 89.58%, URAM 20.31%, DSP 19.55%。
3. **KV260 板端交付与实机运行**：
   - 板端安装包：`whiteboard_rgb565_color_cache_clear_v16_board.zip`。
   - 部署执行：`sudo /usr/bin/python3 kv260_board_run.py deploy`。
   - 烟雾验收结果：
     - `transport_bytes: PASS`
     - `camera_fps: 23.50 FPS`
     - `frame 0..2: PASS` (4,147,200 bytes, `quantize: all_pixels_palette_reference`)
     - `V15_PL_FEATURES_PASS`: `static_person_protected: true, white_shirt_protected: true, untrusted_gate: true, new_ink_preserved: true`。
   - 运行状态：`DEPLOY_RUNNING pid=54451 FPGA_reloaded=True`，OSD 白屏与方位指引模块在校准期间实时接管 DP 屏输出。


