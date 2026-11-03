# 案例 03：从 ILA 和生成 RTL 定位 RGB565 恢复核死锁

## 1. 案例信息

- 日期：2026-10-13
- AI：Antigravity / Gemini 3.8 Flash
- 主题：RGB565 位宽变更后的 AXI 读写调度死锁、行级 burst 解耦和实板修复
- 源记录：[`2026-10-13-002-restore-freeze-investigation.md`](../../../member_b/shared_records/2026-10-13-002-restore-freeze-investigation.md)
- 记录状态：死锁修复并完成板端验证

## 2. 问题背景

最新 RGB565 恢复 IP 在 `initialize=false` 时卡死，早期现象容易被误判为 FIFO 不够或上游没有数据。用户要求利用已有 ILA 和源码先找根因，遵守不盲目扩大 FIFO 或改变架构的约束。

## 3. 对话要点

以下内容根据内部会话摘要重建，**不是逐字聊天记录**。

### 用户任务

根据 ILA 交接文档和已有波形，解释恢复 IP 为什么卡死，并给出可验证的解决方案。

### AI 贡献摘要

1. 对比 RGB888 与 RGB565 版本的 HLS 代码和生成 Verilog 状态机。
2. 用 ILA 证明 `pixels`、`thin` 上游仍有数据，停滞发生在 `compose_U0` 的读取侧，排除“没有输入”和“FIFO 深度不足”的简单解释。
3. 定位同一内层循环对 `history`、`previous_frame`、`pixel_state` 原地交织读写，HLS 调度先发 AW/AR，延后 WDATA，形成未完成写事务阻塞同地址读响应的 RAW 死锁。
4. 提出并实施“行级 burst 读入 → 片上处理 → 行级 burst 写出”的读写解耦。

## 4. 团队决定与采用

- 保留 PL 纯硬件加速边界，不把恢复计算移入 PS。
- 采用行级 burst 解耦和片上 line buffer，保留原始版本以便回滚。
- 用户约束的本次工程允许综合、打包和同步，但板端验证按会话中的授权范围执行。

## 5. 根因证据

- 生成 RTL 中 State 7 发出写地址 AW，State 14 发出读地址 AR，State 21/22 等待 RVALID，State 27 后才输出 WDATA。
- ILA 解码显示 `history AWADDR=0x38500040`、`ARADDR=0x385003c0`，读写请求已失步挂起。
- `initialize=true` 之所以通过，是因为该分支跳过 `render_frame()` 和 `compose()`，不能证明运算路径正常。
- 32x16 小尺寸 `initialize=false` 也超时，说明不是大帧 FIFO 容量问题。

## 6. 量化验证

- 新的 `RESTORE_LOCAL565` 原生 C 仿真通过：`dense_static=3 weak_static=3 exits=3 thin_ink=5 frames blocks=2 groups=128`。
- HLS 综合和 IP 导出通过；1080p 最大延迟由原约 161 ms 降至约 52.39 ms。
- 板端 1080p 恢复隔离：`initialize=false` 运算帧 100.89 ms、连续运算帧 100.96 ms，原 10 s 超时消失。
- 全尺寸宽度 32、128、256、512、1024、1920 的初始化和运算矩阵全部 status=0。
- 全链候选部署：1000 帧真实连续 DMA，29.92 FPS，`bad_frames=0`、`sequence_gaps=0`；正常模式稳态 7.40 FPS。

## 7. 失败与纠正

- 最初把问题看成 FIFO 深度或上游数据不足；ILA 和小尺寸复现后纠正。
- `initialize=true` 的通过结果被重新解释为旁路证据，而不是恢复核通过。
- 未把 HLS 级延迟直接写成整机 FPS；整机 FPS 单独通过板端链路测量。

## 8. 结果边界

- 本案例验证了恢复核死锁修复和当时匹配固件的板端链路。
- 7.40 FPS 是该候选正常模式的现场结果，不代表后续版本或所有画质场景。
- 证据依赖指定板、指定固件包和指定运行模式；重新打包后仍应核对 bit/HWH/DTBO 和源 hash。

## 9. 证据入口

- 源会话：见本目录顶部的源记录链接。
- ILA、生成 RTL、HLS 报告和板端脚本：源会话 `Validation and Evidence`、`Files Changed`、`Handoff Notes`。
