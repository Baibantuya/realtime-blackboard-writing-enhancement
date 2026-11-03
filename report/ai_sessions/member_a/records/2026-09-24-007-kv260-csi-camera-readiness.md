# AI Session: 2026-09-24-007-kv260-csi-camera-readiness

- Date: 2026-09-24
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 检查已接入 KV260 的 CSI-2 摄像头当前是否可采集；若链路就绪，将板框校正→可选二值化→HDMI 流程切换为 CSI 输入。
- Status: Inspection completed; CSI path not ready; existing input flow intentionally unchanged
- Report candidate: No
- Related commits: None
- Related files: `kv260-whiteboard-enhance/scripts/create_board_rectify_overlay.tcl`; `test_workspace/board_rectify_2026-09-24/board_rectify_kv260.ipynb`; D-042.

## Context Read

按顺序阅读根 `AGENTS.md`、AI 开发策略、项目状态、决策流水、索引和近期板框校正 HDMI/deploy 会话。检查当前 overlay Tcl、板端文件部署状态和既有 CSI-2 项目记录。工作区根无 Git 元数据。

## Task and Constraints

用户要求先检查 CSI 摄像头；只有检查无问题后，才将刚完成的摄像头→PL 校正→可选二值化→HDMI notebook 流程切换为 CSI 输入。此前用户要求不要在其浏览器中调试，本次遵循，不启动/编辑/执行 Jupyter 页面。用户明确提供 ubuntu SSH 账号，本次只用于板端只读探测，不记录凭据、不写板端系统配置。

## Contributions

- SSH 登录 KV260（Linux `kria`, kernel `5.15.0-1027-xilinx-zynqmp`）并检查 `/dev/video*`、`/dev/media*`、`/dev/v4l-subdev*`、V4L2 设备、media topology、格式、内核模块目录和设备树。
- 初始普通用户可见结果：无 video/media/subdev 节点；`v4l2-ctl` 无法打开 `/dev/video0`；CSI/MIPI/IMX219 视频模块目录搜索无结果；`/sys/class/video4linux` 为空。
- 使用用户提供的 sudo 凭据运行只读 `xmutil listapps`：清单只有 `k26-starter-kits`，类型 XRT_FLAT、base 同名、active slot 0、(PL+AIE) slot `(0+0)`。`/etc/dfx-mgrd/default_firmware` 为 `k26-starter-kits`，FPGA manager `operating`。
- `/proc/device-tree` 下未发现 camera/CSI/IMX 节点；`/lib/firmware/xilinx/` 仅存在 `k26-starter-kits` 的 shell manifest、bitstream；无可见 CSI media pipeline。
- 检查正式校正 overlay Tcl：只实例化 ZynqMP PS、板框校正、二值化和 DDR SmartConnect，没有 CSI-2 RX、I2C camera control、Bayer/ISP 或 V4L2 frame-buffer IP。
- 因 CSI 输入栈尚未存在且当前校正 bitstream 不含 CSI 硬件，本轮不改采集入口为猜测的 `/dev/videoN`，也不覆盖现有可运行 notebook；记录为前置集成工作。

## Decisions and Adoption

- D-042 记录：CSI 摄像头“物理接入”不等于 Linux 已可采集；在 CSI media/video 节点与格式/帧抓取通过前，不能把当前输入流程宣称切换到 CSI。
- 要支持摄像头到校正再到 HDMI 的单一 live flow，需要识别 sensor 型号及已安装驱动/初始化支持，并让 CSI-2 RX/所需图像前处理与校正 IP 在同一可运行 PL/软件方案里共存。当前流程保持原样；没有宣称 CSI 功能已完成。
- AMD/Xilinx 官方 Kria-PYNQ 项目说明其 KV260 Base Overlay 才提供 Raspberry Pi camera/PMOD 支持；该 base overlay 在本板当前 app list 中没有独立 CSI video node 可见。资料参考：[Xilinx/Kria-PYNQ](https://github.com/Xilinx/Kria-PYNQ)。

## Commands and Tools

- SSH 只读 shell：查询 `uname -a`、V4L2 设备、media topology、video formats、`/sys/class/video4linux`、内核模块路径、设备树 camera/CSI 节点。
- 管理员只读：`xmutil listapps`、读取 `/etc/dfx-mgrd/default_firmware`、`/sys/class/fpga_manager/fpga0/state`。
- 本地读取 `kv260-whiteboard-enhance/scripts/create_board_rectify_overlay.tcl`，确认当前校正 overlay 实例化内容及无 CSI/MIPI IP。
- web 官方来源核实：Xilinx/Kria-PYNQ README 对 KV260 Base Overlay camera support 的说明。

## Validation and Evidence

- 实际板端检查结果：无 `/dev/video*`、`/dev/media*`、`/dev/v4l-subdev*`；无 V4L2 video4linux class 实例；设备树搜索无 camera/CSI/IMX 实例。
- `xmutil listapps` 返回唯一 `k26-starter-kits`，active slot 0；FPGA manager 为 `operating`。
- 当前正式 rectifier Tcl 无 CSI RX 或摄像头控制/前处理接口。
- 没有改写/加载 bitstream，没有改板端配置，没有修改已部署 HDMI notebook。CSI sensor 具体型号、I2C ACK、lane/format、真实帧采集和 HDMI 串接均未验证。

## Errors and Corrections

- 普通用户读取 `dmesg` 被内核权限策略拒绝；没有尝试放宽权限。结论依赖设备节点、sysfs、设备树只读信息及 sudo 授权的 app list，不依赖 dmesg。
- `xmutil listapps` 普通用户访问本地 socket 得到权限拒绝；经用户提供的 sudo 密码以只读方式重试后成功。

## Files Changed

- `project_workspace/ai/sessions/2026-09-24-007-kv260-csi-camera-readiness.md` (新增)
- `project_workspace/ai/INDEX.md` (更新)
- `project_workspace/PROJECT_STATE.md` (更新)
- `project_workspace/DECISIONS.md` (D-042 新增)

## Remaining Work

- 在安装或加载 CSI camera-capable overlay 后，确认准确摄像头 sensor/module 型号，获取 `/dev/media*` topology 和 `/dev/video*` pixel formats，并验证至少一帧。
- 之后构建/选定含 CSI 输入和板框校正的共存实现，再把 CSI 捕获格式转成校正核需要的 1920×1080 GRAY8，接二值化 demo 与 HDMI；若使用预构建 base overlay，需解决其与 rectifier overlay 同一 PL 配置的共存/整合。
- 当前 HDMI 显示和校正上板本身仍待用户运行验证。

## Handoff Notes

本轮仅完成 CSI readiness 检查。板端“相机插着”但当前系统/PL 无可采集接口；用户要求的条件分支不满足，故没有更改已部署的 UVC/输入入口，也没有在 Jupyter 浏览器中运行 notebook。
