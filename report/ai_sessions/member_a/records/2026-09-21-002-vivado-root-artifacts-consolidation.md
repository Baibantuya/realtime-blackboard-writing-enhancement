# AI Session: 2026-09-21-002-vivado-root-artifacts-consolidation

- Date: 2026-09-21
- Operator: Codex
- AI product/model: Codex
- Participants: 用户；Codex
- Objective: 识别根目录点号开头的 Vivado 生成目录，并集中放入一个子目录。
- Status: Completed
- Report candidate: no
- Related commits: none
- Related files: `.gen/`, `.srcs/`, `.Xil/`

## Context Read

- 已按顺序读取根目录 `AGENTS.md`、`project_workspace/ai/AI_DEVELOPMENT_POLICY.md`、`project_workspace/PROJECT_STATE.md`、`project_workspace/DECISIONS.md`、`project_workspace/ai/INDEX.md`。
- 已读取相关近期记录 `project_workspace/ai/sessions/2026-09-19-002-vivado-gui-full-frame.md`。
- 已检查当前状态；工作区根目录不是 Git 仓库，因此根目录 `git status` 无法执行。

## Task and Constraints

- 用户要求确认根目录点号目录来自哪个 Vivado project，并把它们集中放入一个子目录。
- 仅处理根目录的 `.gen/`、`.srcs/`、`.Xil/`，不改辅助资料和正式项目代码。
- 移动前依据 XCI、Vivado 日志和 `.Xil` Tcl 反查归属。

## Contributions

- 识别 `.gen/`、`.srcs/` 中的两个 MIPI D-PHY 4.3 IP 实例及其生成关系。
- 识别 `.Xil/` 中的 `fmc_camera_binary_hdmi_core` OOC 综合实时缓存，确认三目录不是一个普通 `.xpr` GUI 工程的完整工程目录。
- 在确认没有 Vivado 进程运行、目标路径均位于工作区根目录之后，将三个目录原样移动至 `vivado_root_artifacts/`。

## Decisions and Adoption

- 采用根目录英文子目录名 `vivado_root_artifacts/`，保留 `.gen/`、`.srcs/`、`.Xil/` 的相对并列结构。
- 用户要求针对点号目录，因此没有扩大范围移动根目录的 `vivado*.log`、`vivado*.jou` 文件。
- 本次只整理生成物位置，不影响架构、接口、器件、位宽、算法、工具版本或评测方式，故无需新增 `DECISIONS.md` 条目。

## Commands and Tools

- 使用 PowerShell 盘点目录、文件、时间和大小；使用 `rg`/`Select-String` 检索 Vivado 工程与顶层引用。
- 使用显式绝对路径校验和 `Move-Item -LiteralPath` 移动三个目录；移动前检查 Vivado 进程未运行。

## Validation and Evidence

- `.srcs` 中存在 `probe_dphy.xci` 与 `vid005_dphy_probe.xci`，均为 `xilinx.com:ip:mipi_dphy:4.3`，对应生成目录位于 `.gen`。
- `.Xil/Vivado-5892-why/realtime/fmc_camera_binary_hdmi_core.tcl` 明确记录 OOC 顶层 `fmc_camera_binary_hdmi_core` 和旧 `whiteboard/rtl/` 源文件路径。
- 移动后 `vivado_root_artifacts/` 含 8 个文件、17 个子目录、总计 2,147,917 字节。
- 根目录点号开头的目录数量为 0；目标下存在 `.gen/`、`.srcs/`、`.Xil/` 三个目录。
- 未执行仿真、综合或硬件测试；本次仅整理已有 Vivado 生成物。

## Errors and Corrections

- 首次对 PowerShell/Windows 下的 `rg vivado*.jou vivado*.log` 使用通配符，`rg` 报 Windows 路径语法错误；随后改用 `Get-ChildItem` 展开文件列表并以 `Select-String` 检索。

## Files Changed

- `.gen/` → `vivado_root_artifacts/.gen/`
- `.srcs/` → `vivado_root_artifacts/.srcs/`
- `.Xil/` → `vivado_root_artifacts/.Xil/`
- `project_workspace/PROJECT_STATE.md`
- `project_workspace/ai/INDEX.md`
- 本会话记录

## Remaining Work

- 无。

## Handoff Notes

- `.gen/.srcs` 是 2026-09-20 MIPI D-PHY 管脚/可行性探测的临时 IP 生成物，不是正式交付工程。
- `.Xil` 还保留旧 `whiteboard/rtl/` 路径引用，属于历史 OOC 缓存；如后续直接复用，需注意路径已变化且旧 `whiteboard/` 已弃用。
- 根目录的 `vivado*.log/jou` 仍保留在原处，如需进一步整理应另行确认是否一并归档。
