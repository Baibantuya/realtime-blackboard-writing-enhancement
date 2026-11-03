# AI Session: 2026-09-21-013-kv260-pl-binarize-no-display-feasibility

- Date: 2026-09-21
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 在无 HDMI 条件下，评估并尽可能验证 KV260 的 PS→PL→PS 最小 GRAY8 二值化数据通路；从 UVC 采集抽帧，回传二值化结果供目视检查。
- Status: Completed
- Report candidate: No
- Related commits: None

## Context and Constraints

- 已读取项目规范、状态、D-027/D-028 和最近会话。1080p30 UVC MJPEG 可采集，PS 应只做解码/缓冲调度；此前尚无 KV260 PS→DMA→PL→显示闭环实测，也没有 HDMI。
- 软件二值化只能作为像素语义与输出参考，不能冒充 PL 验证；不加载未知 bitstream，不复用旧 ZCU104 工程。

## Contributions

- 在真实 KV260 上盘点 PL 运行时：XRT/ZOCL 设备 Ready，FPGA manager 为 operating；系统有 CMA DMA heap、`/dev/dmaproxy`、4 个 AXI performance monitor UIO 和 `a0000000.fabric` UIO。
- 默认固件包只有 `k26_starter_kits.bit.bin` 与 DTBO，shell 为单槽 `XRT_FLAT`；可见固件路径没有二值化 xclbin/bitstream。
- 运行中 device tree 的 PL 区仅公开 `a0000000.fabric`（`generic-uio`），没有 AXI DMA/VDMA 或二值化 IP 节点。继续核对后确认 `dmaproxy` 是 VCU staging client driver，不是当前 fabric 的自定义视频 DMA 通道；普通用户也不能访问 DMA heap/dmaproxy。
- 从 `/dev/video0` 实际采集 1920×1080 MJPEG 一帧，用板端 OpenCV 灰度阈值 128 生成参考二值图，再取回 960×540 预览原图和结果图。该处理没有加载 PL 加速器。

## Decision and Adoption

- 采用 D-029：当前镜像没有可用的 PS→PL→PS 二值化硬件接口，不能将软件参考图标记为 PL 数据通路验证。下一步需要受控的 AXI DMA + GRAY8 AXIS 二值化核 + 匹配 DT overlay；无 HDMI 时，结果回写 PS 并抽帧比较。

## Validation and Evidence

- XRT 2.13/ZOCL 设备 Ready，FPGA manager `operating`；但 PL device tree 仅有 `a0000000.fabric: generic-uio`，无 AXI DMA/VDMA/二值化节点。因此现有镜像上的真实 PL 回环为**未具备接口、未执行**，不是算法失败。
- 参考帧为 1920×1080，阈值 128，白像素占比 50.07%。板端源图 SHA-256：`2de40fceab039390404a489d31dd44d01f5f630a9460415cc8dcae8a52334e2c`；二值图：`6da3d60880290399febea6fdca6648c6f723827798ee79f7285ae6ff5b0e19f7`。
- 取回的 960×540 预览哈希与板端一致：原图 `ECCC77546746ECBFDF73B8647815DC60FF91BF8591AF1FC2ECA54C975CD70F90`，二值图 `9E3507DC851CEAE0A8475BE4F73F52D707FAC2A86FD5401E9F90E332648F5D0C`。证据为 `project_workspace/evidence/kv260_uvc/kv260_1080p_reference_preview.jpg`、`project_workspace/evidence/kv260_uvc/kv260_1080p_binary_reference_preview.jpg`。
- 目视结果中，桌面物体轮廓在二值图中连贯，阈值语义/输出格式正常；但这不是白板场景，不能据此评估笔迹可读性、曝光或自适应阈值。
- 静态 1920×1080 Gray8 的 OpenCV 阈值为 1.775 ms/帧（1000 次）；150 帧 MJPEG→Gray8 原始输出为 5.63 s、CPU 94%。PL 阈值可回收该逐像素 CPU 时间与约 124.4 MB/s Gray8 读写流量，但不能消除软件 MJPEG 解码这个主要瓶颈。

## Errors and Corrections

- 最初看到 `/dev/dmaproxy`/DMA heap 时不能据此推断已有通用 PL 视频 DMA；检查 device tree 后纠正为“当前未连接到自定义二值化 IP”。
- `xmutil listapps` 因 dfx-mgrd socket 权限被拒；没有使用 sudo、没有加载默认或未知 bitstream，也没有改变板端持久配置。
- 板端四个 `/tmp/kv260_bin_*` 临时文件已在取证后删除。

## Files Changed

- `project_workspace/ai/sessions/2026-09-21-013-kv260-pl-binarize-no-display-feasibility.md`
- `project_workspace/evidence/kv260_uvc/kv260_1080p_reference_preview.jpg`
- `project_workspace/evidence/kv260_uvc/kv260_1080p_binary_reference_preview.jpg`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/DECISIONS.md`
- `project_workspace/ai/INDEX.md`

## Remaining Work

1. 从 KV260 的受控基础工程新建 `AXI DMA MM2S → GRAY8 threshold AXIS → S2MM` 与匹配 DT overlay，不复用默认 starter-kit bitstream 的未知接口。
2. 用 DMA-safe buffer 做每帧 Y plane 输入、cache 同步和回写校验；先和软件参考逐字节比较，再测 1080p30 连续帧率、延迟、CPU 和错误计数。
3. 实际加载新 bitstream 前，保留当前桌面/PL 状态可恢复记录并获得管理员操作授权。

## Handoff

已完成无显示条件下的输入、参考输出和现有 PL 平台可行性检查。PL 核适合二值化，但当前启动镜像没有它所需的 DMA/IP/DT overlay，真实 PS→PL→PS 上板回环尚未执行；两张结果图只证明相机与参考阈值效果。
