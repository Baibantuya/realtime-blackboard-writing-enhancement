# AI Session: 2026-10-08-003-kv260-dpu-yolo-references

- Date: 2026-10-08
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 核实 KV260 官方 DPU 与 YOLO 部署参考，解释现成设计与当前工程集成边界。
- Status: Complete; official-reference research only
- Report candidate: No
- Related commits: None
- Related files: 本记录、PROJECT_STATE.md、ai/INDEX.md。

## Context Read
已读取 AGENTS.md、AI_DEVELOPMENT_POLICY.md；查看 PROJECT_STATE.md、DECISIONS.md 与 INDEX.md 的当前及相关条目（长历史输出部分被截断，未声称通读全部历史）；读取教师检测规划会话和最近 shared-ring 构建会话相关内容；查看 Git 状态及正式 docs/scripts 中 DPU/YOLO 相关文本。必读文件均存在。Git 显示正式目录及测试目录等未跟踪，未覆盖源码。

## Task and Constraints
用户要求官方参考。本次仅资料核实，不实施部署、训练或 PL 工程更改。

## Contributions
核实 KV260 有官方预构建 DPU overlay；DPU 是 PL 中实现的 DPUCZDX8G IP，需要硬件配置及软件运行时。DPU-PYNQ README 明确 KV260 单核 B4096 已验证，支持 PYNQ 3.0 / Vitis AI 2.5.0，并提供 bit/HWH/xclbin 与预编译模型入口。直接读取官方 YOLOv3 notebook，确认加载 dpu.bit、tf_yolov3_voc.xmodel，输入预处理及解码/NMS 在 Python 实现。官方 KV260 benchmark 列 Tiny YOLOv3 416x416，模型分 B3136/B4096；其 2021.1/dnf 安装示例为历史环境，不能直接当作当前 Ubuntu 命令。

现成 DPU 设计可用于独立验证，不能据此声称已有视频工程具备 DPU；若需同现有校正/恢复 IP 同时运行，需要共同 PL 设计、资源/时序/DDR/软件集成。模型须匹配目标 DPU 的 arch.json/配置。DPU-PYNQ 仓库已于 2025-08-12 归档，不再主动开发。未选择新工具链或新 YOLO 版本。

## Decisions and Adoption
未改变现有架构、接口或工具版本；不将参考设计可用性视为当前板端已安装 DPU。

## Commands and Tools
PowerShell、rg、Git 只读检查；将使用网页检索核对官方文档及官方仓库。

## Validation and Evidence
模型编译、量化、综合、实现、上板及性能测试：未执行。网页/官方 notebook 内容阅读已执行。

官方来源（访问日期 2026-10-08）：
- https://github.com/Xilinx/DPU-PYNQ （KV260 B4096、版本、构建文件、归档状态）
- https://github.com/Xilinx/Kria-PYNQ （官方 Ubuntu/PYNQ 及 DPU overlay 入口）
- https://raw.githubusercontent.com/Xilinx/DPU-PYNQ/master/pynq_dpu/notebooks/dpu_yolov3.ipynb （已实际读取的 YOLOv3 notebook）
- https://github.com/Xilinx/kria-kv260-ai-benchmark （Tiny YOLOv3 与 B3136/B4096 固件）
- https://docs.amd.com/r/en-US/pg338-dpu （DPUCZDX8G 产品指南，当前页 4.1）
- https://docs.amd.com/r/3.0-English/ug1414-vitis-ai/Deep-Learning-Processor-Unit （模型编译与 arch.json）
- https://docs.amd.com/r/3.0-English/ug1414-vitis-ai/Integrating-the-DPU-into-Custom-Platforms （自定义平台集成要求）

## Errors and Corrections
长历史文件一次读取输出截断，改为相关条目和最近记录阅读；GitHub 子目录页面返回 Internal Error，GitHub tree API 达到匿名限流，改为直接读取 raw 官方 notebook 成功。不从第三方搜索结果推断官方支持，无项目代码修改。

## Files Changed
本记录、project_workspace/PROJECT_STATE.md、project_workspace/ai/INDEX.md。

## Remaining Work
若后续实施，先核对实际系统/PYNQ/VART/XRT/DPU 版本及模型目标；独立官方示例验证和共同 PL 设计集成尚未执行。

## Handoff Notes
当前 shared-ring 视频工程已有自定义 PL IP；DPU 共存尚未验证。
