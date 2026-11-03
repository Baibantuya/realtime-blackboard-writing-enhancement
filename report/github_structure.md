# GitHub repository layout

仓库：<https://github.com/Baibantuya/realtime-blackboard-writing-enhancement>。

当前采用私有仓库整理，主分支为 `main`。项目原创代码采用 MIT；第三方条款见根目录 `third_party_notices.md`。正式提交前公开仓库并创建与实际工程身份一致的版本标签。

```text
src/       2025.2 RTL、HLS、PS、UI 与驱动源码
sim/       测试平台、输入生成、比较程序与补充验证
build/     Tcl、约束、构建入口、实现报告及来源清单
board/     C5 运行包、硬件导出、环境说明与按版本分组的板测
data/      必要测试数据及参考输出
skill/     可复用工具、用法、测试和来源
report/    仓库技术报告、团队 AI Sessions、证据索引及附件
readme.md  项目入口、版本状态、构建和运行方法
license.txt
third_party_notices.md
manifest.json
```

当前结构与赛事建议的七目录一致。展开路径统一小写英文、数字、下划线和连字符。厂商IP归档内部保持原名。将编译缓存和临时输出排除在版本控制外；必要的冻结IP、硬件产物与原始报告作为可追溯输入保留。后续大视频和完整发行压缩包适合通过 Release 资产分发，README提供关联。

版本建议：源码与硬件用 `v24-2025.2-c5-r5-review` 标明本轮审查基线；当前先提交主分支，不发布“已完成板测”的正式标签。补现场结果后再创建相应发行版。
