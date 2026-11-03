# AI Session: 2026-09-26-001-teacher-detection-data-plan

- Date: 2026-09-26
- Operator: Project owner
- AI product/model: OpenAI Codex
- Participants: Project owner, Codex
- Objective: 估算教师遮挡识别、板面配准与 KV260 部署所需数据。
- Status: Completed; planning advice only
- Report candidate: No
- Related commits: None
- Related files: `project_workspace/PROJECT_STATE.md`; `project_workspace/ai/INDEX.md`.

## Context Read

- 已按顺序读取根 AGENTS.md、AI 开发策略、项目状态、决策、索引，以及相关最近会话、接口规范和计划。
- 工作区及正式目录均无 Git 元数据；无法取得 Git 状态。

## Task and Constraints

- 用户提出 SLAM + CNN，并计划在 PL 实现 IP；需要数据类型和数量级建议。

## Contributions

建议先用 COCO 人体检测预训练权重做课堂域微调；本项目 M0 只需教师/遮挡者矩形框。估算首版采集 8–15 个独立课堂或布置 session、约 2,000–5,000 张去重标注帧；训练/验证/测试按场景或录像分组。另保留连续录像用于帧龄、配准和历史污染评测。样本数量是工程起点估算，需学习曲线验证，不是论文保证值。

固定机位先用板面特征/单应性配准；若相机可移动且确需地图跟踪，再评估 SLAM。SLAM 主要需要标定、连续序列和可核对的位姿/配准真值，不是人体框训练集。CNN 先离线训练，量化后在 PL DPU 推理；PS 处理跟踪/坐标/调度，PL 的现有视频与历史合成核仍需集成验证。

## Decisions and Adoption

以上为建议，未获用户采纳；没有改变既有 D-039 接口或决定采用 SLAM。既有 2 fps、最多 8 框 ABI 仍是当前基线。

## Commands and Tools

读取项目规范、状态、接口及最近会话；检索 COCO 官方资料、ORB-SLAM3 项目说明和 AMD Vitis AI/KV260 文档。

## Validation and Evidence

未执行训练、综合、仿真、上板或准确率测试。

## Errors and Corrections

发现部分旧四周计划使用像素 mask 表述；以较新的 D-039/接口 v0.3 矩形框基线为准。

## Files Changed

- `project_workspace/ai/sessions/2026-09-26-001-teacher-detection-data-plan.md`

## Remaining Work

采集条件、教师身份识别是否真的需要、相机固定与否、模型支持算子/资源/延迟、样本学习曲线均待确认。

## Handoff Notes

后续先确认识别目标与摄像机安装方式，再进行真实课堂采集和离线基线评测。

## Follow-up: public-data-first clarification

- User clarified the objective is occluder localization, not identity recognition, and prefers public datasets.
- Revised advice: start with a COCO-pretrained person detector and no custom training dataset. The earlier 2,000–5,000 labeled classroom-image estimate applies only if a baseline fails and substantial domain fine-tuning is needed; it is not a prerequisite.
- A small, representative local acceptance set (suggest 100–300 sampled frames from several independent clips, with bounding boxes annotated for measurement) is still needed to claim performance on the actual camera/classroom. Keep full clips to assess 2 fps sampling, lag, expiry, and clean-board contamination. This is evaluation data, not necessarily training data.
- Public COCO person labels are suitable for a first detector. Public-source performance does not establish performance in the target classroom due to domain shift; use observed failures to decide if a small fine-tuning set is needed.
- No model was trained or deployed, and no accuracy measurement was performed. Sources checked: COCO official detection dataset, Ultralytics detector documentation, peer-reviewed domain adaptation study.

## Follow-up: SLAM and CNN responsibilities

- User asked for each component's purpose and compute location. Clarification: CNN detector outputs person/occluder boxes; training on an external computer, inference preferentially via KV260 PL DPU with PS pre/post-processing and ABI publication. SLAM, if ever needed for moving camera, estimates camera/board relative pose from temporal image features; conventional SLAM runs on PS CPU and may use a PL front-end accelerator, but a full SLAM IP is not part of the current baseline.
- For a fixed camera, existing board rectification and simple planar registration are the initial path; SLAM has no required role. The PL board rectification IP is distinct from SLAM and from CNN inference.
- No implementation or performance claim. The actual board CSI camera input remains unresolved per D-043, and DPU coexistence with the rectifier requires synthesis/board verification.

## Follow-up: project owner PL preference

- Project owner corrected the placement requirement: all feasible compute should run in PL, DPU inference is acceptable, and unnecessary PS↔PL image traffic should be avoided.
- Updated direction recorded in D-044. Video/preprocessing/detection postprocessing/history composition should be PL-first; PS should mainly configure and monitor. If motion registration is needed, evaluate PL feature/flow/homography blocks before a full SLAM implementation. Shared DDR access may remain; avoid PS software frame copies.
- Correction to prior answer: PS CPU was offered as a default for SLAM and CNN postprocessing without reflecting the owner's PL-first constraint. That placement is superseded as the preferred architecture. D-039/D-040 still define the unimplemented 2 fps PS analysis branch and need an explicit spec/ABI revision during design.
- No tests, synthesis, or board validation executed.
