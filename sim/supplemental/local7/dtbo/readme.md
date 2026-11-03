# Local7 设备树能力声明修正候选

基线为 C5 设备树及 C5 HWH，另对照 R5 的 MIPI CSI-2 RX XCI。原始文件未覆盖。

已移除硬件配置为 false 的三个布尔声明：

| 设备树声明 | 对应硬件参数 |
|---|---|
| `xlnx,en-active-lanes` | `C_CSI_EN_ACTIVELANES=false` |
| `xlnx,en-csi-v2-0` | `C_EN_CSI_V2_0=false` |
| `xlnx,en-vcx` | `C_EN_VCX=false` |

WSL 的 dtc 1.6.1 编译退出码为 0。解析二进制 DTBO 后确认只有以上三个属性删除，其余 374 项属性、节点集合、内存预留和启动 CPU 不变。编译仍有原设备树结构相关警告，详见 `compile.log`；本结果不是零警告认证。

候选文件：`imx219-v24-2025-2-c5-local7.dtbo`。SHA-256：`1619520ce90928f122125682fddc5a9e9b171903dbc0ff50f1af25d0b68d62c5`。

固件引用仍为 `imx219-v24-2025-2-c5.bit.bin`。未改变 RTL、时钟、约束或位流；未增加 CDC 豁免。此修正改善软硬件能力声明一致性，不能消除 CDC 告警或证明运行时驱动兼容。

**未上板验证，未替换既有提交包。** 后续板级核查必须确认实际 Linux 驱动版本、overlay 加载、摄像头启停及持续采集；当前用户明确暂不做实机验收。

生成与审查脚本位于上级目录 `prepare_dtbo.py`、`audit_dtbo.py`；原始输入哈希和属性差异分别见 `origin.json`、`validation.json`。
