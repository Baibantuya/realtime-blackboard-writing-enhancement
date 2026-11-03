# 可复用技能包（草稿）

2026-10-27：[Skill双向证据索引](../batches/v24_20261027/skill_evidence_index.md)另列既有PYNQ离线检查器及S/skill六组候选，区分结构、文件、构造测试、硬件和跨任务状态。controlled-model-comparison仅为历史研究流程，当前整机不接入模型，不自动删除草稿。

本目录对应赛题3.3.5.2的技能包部分，包含两项从实际失败/观察提炼的工作流。**它们是本轮新整理的流程，不是历史中已安装或已使用的同名Skill。**本轮只检查结构与证据映射，不进行训练、构建、板测或安装。

| Skill | 适用范围 | 来源 | 验证状态 |
| --- | --- | --- | --- |
| [ui-evidence-validation](ui-evidence-validation/readme.md) | 桌面/嵌入式UI的视觉、输入、状态及显示性能证据审查 | U01字体/内存断言；U02可见字形居中；U03流水与模式保存 | 历史案例内有工程验证；新流程只完成回溯和结构检查，迁移待验证 |
| [controlled-model-comparison](controlled-model-comparison/readme.md) | 模型导出一致性、数据/阈值/尺寸路线及重复实验的受控比较 | C01严格失败；C02尺度/测试集；C03种子与JS负结果 | 已有实验支持具体规则；没有按新Skill执行另一个任务 |

各目录提供SKILL.md入口、README.md、workflow.md和agents/openai.yaml。用户可先读README判断适用，再按workflow准备本任务输入；不能直接运行历史消息或脚本。系统模型、板卡、框架和数据路径是新任务参数，不写死为本项目值。

[验证与迁移计划](validation.md)区分已做的只读检查和未做的效果验证。这两项不宣称满足通用PYNQ专项加分。
