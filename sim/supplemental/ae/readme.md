# AE 被动采样接口修正

2026-10-29。修改仅位于 `rtl/axis_ae_status.v` 的接口属性和注释。AE 继续旁路观察 TDATA、TVALID、TREADY、TUSER，所有观察端口仍为输入，没有新增视频背压驱动或修改曝光算法。

原模块被工具推断成普通 AXIS Slave，因 TREADY 为输入产生 `IP_Flow 19-3480`。候选使用 AMD UG994 2025.2 支持的 `X_INTERFACE_MODE="monitor"`，并明确时钟、复位和信号映射。依据：[X_INTERFACE 属性说明](https://docs.amd.com/r/2025.2-English/ug994-vivado-ip-subsystems/List-of-Supported-X_-Attributes)。

已完成的本机验证：

- 前后接口推断探针对照：原版出现 TREADY Critical Warning，候选该告警消失。
- 完整 BD 重新构建并 validate；外部端口、标量连线、接口网和地址分配与 R5 相同。候选 AE 接口为 Monitor，四个观察信号仍全部为输入。
- 行为仿真比较原版与候选每周期的 status，并独立检查暗／中／亮图、反压、受阻 SOF 与中途复位；4 帧、791 周期通过。
- 两版独立 OOC 综合：均为 LUT 277、FF 159、BRAM 0、DSP 0。去除注释及属性后的功能网表文本相同；这不是形式等价证明。

结果见 `review.json`，复查入口为上级 `audit_ae.py`。完整 BD/OOC 日志没有实际 ERROR 或 Critical Warning；其他普通警告仍按类别保留在 JSON 中，并未宣称全工程零警告。独立接口探针没有执行 validate，其自身的“未验证 BD”提示不影响后续完整 BD 验证记录。

<span style="color:#C00000">【尚未验证】这份 AE 元数据候选没有重新运行整机布局布线或导出位流。C5/R5 的 WNS +0.011 ns 属于各自已冻结工程，不能改写成这份候选的新物理实现结果。没有执行真实摄像头曝光／画质验证。</span>
