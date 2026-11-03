# 案例 04：用 ILA/XVC 定位异步复位导致的 CSI buffer full

## 1. 案例信息

- 日期：2026-10-18
- AI：Gemini 3.8 Flash（Antigravity）
- 主题：KV260 视频链路首帧超时、Gamma AXI-Lite 参数错位和硬件复位同步
- 源记录：[`2026-10-18-004-v19-ila-capture-buffer-full.md`](../../../member_b/shared_records/2026-10-18-004-v19-ila-capture-buffer-full.md)
- 记录状态：复位同步器集成、重新综合、板端压力和连续采集验收完成

## 2. 问题背景

v19 固件在高强度启停时出现 CSI RX `Stream Line Buffer Full` 和首帧超时。物理 JTAG 连接存在，但 ILA 在 AXI-to-BSCAN debug bridge 后，不能直接用物理 TAP 读取，需要先建立 XVC 通道。

## 3. 对话要点

以下内容根据内部会话摘要重建，**不是逐字聊天记录**。

### 用户任务

用 ILA 查清 v19 启动故障原因，先汇报根因和修改方案，再按用户确认进行 200 MHz 重新综合、打包和上板验证。

### AI 贡献摘要

1. 识别 v19 的 `debug_bridge_xvc` 结构，编写直连 `/dev/mem` 的 XVC 服务并通过 Vivado 关联两个原生 ILA。
2. 在异常现场读取 Demosaic、Gamma 和 CSI 状态寄存器，发现 Gamma 宽高寄存器错位，而不是先验地归因于 Restore 或 DMA 算力不足。
3. 将根因收敛为 PS EMIO 异步复位跨 200 MHz video clock 域释放过快，叠加连续 AXI-Lite 写 LUT/宽高造成状态机错位。
4. 实施 5 路双触发器同步、32 周期复位展宽和同步释放，并把它接入相关 ISP IP。

## 4. 根因证据

异常现场寄存器：

| 模块 | 现场值 | 解释 |
|---|---|---|
| Demosaic | `0x00=0x81`, width=1920, height=1080 | 正常运行。 |
| Gamma | `0x00=0x84`, width=1080, height=0 | idle 且配置错位，拒绝正常处理流。 |
| CSI RX | `Stream Line Buffer Full!` | 上游反压后缓存溢出。 |

这组证据把故障链连接为“复位释放/AXI-Lite 配置错位 → Gamma 不处理 → 反压前级 → CSI buffer full”。

## 5. 团队决定与采用

- 采用硬件级复位同步器，不再依赖用户态盲写寄存器或打印延迟。
- 在现有 v19 工程上做增量 OOC 综合、实现和打包，保留旧版本用于回滚。
- 200 MHz 频率约束按用户决定保留；本案例不把时序讨论扩大成未测的性能声明。

## 6. 量化验证

- 修复前：第 21 次启动复现 Gamma 配置错位和 CSI line buffer full。
- 修复后：24/24 次启停压力测试一次通过，Gamma 寄存器 100% 为 `0x81, 1920, 1080`，首帧延迟约 89 ms。
- 连续采集验收：1000 帧，0 坏帧，0 序列断裂，29.911 FPS，`RESULT=PASS`。
- RGB 测试图样的三种主色中值分别为 `[255,0,0]`、`[0,255,0]`、`[0,0,255]`；`dmesg` 无新增 line buffer full 报警。

## 7. 失败与纠正

- 物理 JTAG 不能直接发现 debug hub，纠正为通过 AXI-to-BSCAN XVC 访问。
- 早期临时用户态寄存器写法没有解决复位竞争，纠正为硬件同步释放。
- 现场现象没有被误写成后级 Restore 算力不足；寄存器和 ILA 证据支持的是前级 Gamma 配置路径。

## 8. 结果边界

- 这是 v19 指定固件、指定板和指定压力脚本的实板结果。
- 1000 帧验收证明该故障在该候选中消失，不代表所有 ISP 配置和后续版本都无需复位审计。
- XVC 服务、板端脚本和完整包应与源 hash 一起保存；公开提交时需检查内部地址和主机路径。

## 9. 证据入口

- 源会话：见本目录顶部的源记录链接。
- XVC、ILA、寄存器快照、复位同步器和验收脚本：源会话 `Commands and Tools`、`Validation and Evidence`、`Files Changed`。
