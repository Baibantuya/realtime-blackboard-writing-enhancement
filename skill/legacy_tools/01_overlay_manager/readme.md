# 模块 01: 通用 Overlay 加载器与寄存器映射范式 (01_overlay_manager)

## 1. 适用范围与功能职责

### 适用场景
- 任何基于 AMD Zynq-7000、Zynq UltraScale+ MPSoC (如 KV260, KR260, ZCU104) 或 Versal 的 PYNQ 平台；
- 需要在 Linux 环境下动态烧录比特流并加载配套设备树（Device Tree Overlay, DTBO）；
- 需要安全、严密地自检 PL IP 寄存器映射表，尤其是包含 64 位物理地址切片指针的高性能加速核。

### 核心功能
1. **跨板卡动态自适应加载**：自动识别底层是否为 ZynqMP FPGA Manager；在有 DTBO 时通过内核 `fpgautil` 安全烧录，避免直接调用 PYNQ Configfs 引起的驱动冲突；随后通过 PYNQ 仅注册元数据缓存，确保 Python 侧 `Overlay` 对象与硬件完全同步。
2. **残留脏状态防护**：检测并自动清理由于此前进程异常退出残留在 `/tmp` 或系统全局目录中的失效 PYNQ 状态文件（`global_pl_state.json`）。
3. **64 位寄存器智能映射检查器**：自动识别 HLS / Vivado 自动切片的高低位寄存器（`*_1` / `*_2` 后缀），防止将 64 位指针错误写入单 32 位寄存器。

### 失效条件
- 比特流文件不存在或 `.hwh` 元数据文件名与 `.bit` 不匹配；
- Linux 内核未启用 FPGA Manager 子系统（`/sys/class/fpga_manager` 缺失且不支持直接 PCAP 烧录）；
- 硬件供电或参考时钟异常导致 FPGA Manager 无法进入 `operating` 稳态。

---

## 2. 核心 API 与使用范式

### 2.1 安全加载 Overlay
```python
from skill.overlay_manager.overlay_loader import UniversalOverlayLoader

# 极简加载：自动处理 Zynq-7000 / ZynqMP 差异
overlay = UniversalOverlayLoader.load(
    bitfile_path="/path/to/my_design.bit",
    dtbo_path="/path/to/my_design.dtbo",     # 可选，若有 DTBO 则协同加载
    download=True                            # 是否执行实际烧录
)

# 获取加速 IP 句柄
my_ip = overlay.my_accelerator_0
```

### 2.2 寄存器映射校验与 64 位切片安全读写
```python
from skill.overlay_manager.register_map_inspector import RegisterMapInspector

inspector = RegisterMapInspector(my_ip)

# 1. 打印并校验硬件契约
inspector.print_register_map()
inspector.verify_registers(required_scalars=["width", "height"],
                           required_pointers=["src_addr", "dst_addr"])

# 2. 64位物理地址安全写入 (自动拆分写入 ptr_1 低字与 ptr_2 高字)
inspector.write_pointer_64("src_addr", 0x70000000)
inspector.write_pointer_64("dst_addr", 0x70400000)
```

---

## 3. 经验来源与失败复盘

本模块直接源自项目中的以下排查实证：
1. **DTBO 冲突报错**：KV260 原生 PYNQ 直接解析 DTBO 会尝试通过 configfs 读取已加载的 overlay，遭到 Linux 5.4/5.15 安全策略拒绝报错 `cannot readback configfs`。本模块采用“fpgautil 先行加载硬件与设备树 + PYNQ 仅加载元数据（`download=False, gen_cache=True`）”的解耦架构，彻底消除冲突。
2. **64位寄存器 HWH 检查误报**：早期自检脚本因严格匹配字符串，将 `src_addr_1` 与 `src_addr_2` 判定为未知非法端口，导致启动阻断。本模块引入正规化切片解析器彻底解决该问题。
