# 通用 PYNQ 软硬件协同技能包 (Universal PYNQ Skills)

## 1. 技能包背景与通用性声明

### 1.1 为什么需要本技能包？
在基于 AMD Zynq-7000 / Zynq UltraScale+ (如 KV260, ZCU104, PYNQ-Z2) 的软硬件协同开发中，PYNQ 框架极大地简化了 Linux 用户态对 FPGA 逻辑（PL）的控制。然而在真实的工程实践与高吞吐音视频/流式计算场景中，开发者频繁遭遇以下共性痛点：
1. **Linux 设备树（DTBO）与 PYNQ Configfs 冲突**：在 KV260/KR260 等 Ubuntu/Linux 系统上直接加载 `.dtbo` 经常导致内核拒绝读回或驱动竞争；
2. **64 位物理地址切片与 HWH 命名混淆**：ZynqMP 的 64 位总线指针在 Vivado HWH 中被自动拆分为高低 32 位寄存器（`*_1` 与 `*_2`），传统代码容易漏写高位导致地址总线挂死；
3. **缓存一致性穿透（Cache Incoherency）**：CPU 未刷写（`flush`）导致 PL 读到 DDR 脏数据，或 PL 运算完毕后 CPU 未失效（`invalidate`）导致 CPU 从 L1/L2 缓存读到过期旧数据；
4. **CMA 物理连续内存泄露与碎片化**：高频动态调用 `pynq.allocate` 导致 Linux 内核连续内存耗尽；
5. **硬件反压挂死时的无超时无限轮询**：在 `finally` 块中等待硬件空闲，一旦 PL 流水线因背压卡死，进程陷入死锁且无法被杀死；
6. **嵌入式 ARM Cortex-A53 算力木桶效应**：PS 端 Python/NumPy 多维数组规约单帧吃掉 50~120ms，打破流式实时吞吐。

### 1.2 通用性证明（跨题目、跨板卡复用）
本技能包中的所有模块与范式均**不与具体业务算法（如白板增强、图像滤波等）绑定**。任何使用 PYNQ 框架的参赛队伍，无论是进行音频信号处理、目标检测加速、电机运动控制，还是加密解密协处理器，均可直接引入本目录下的模块与规范。
- **支持硬件平台**：AMD Zynq-7000 (PYNQ-Z2, ZedBoard)、Zynq UltraScale+ MPSoC (KV260, KR260, ZCU104, ZCU102) 及 Versal Adaptive SoC。
- **支持软件栈**：PYNQ 2.7 / 3.0+、Python 3.8 ~ 3.12、Linux 5.4 / 5.15 内核。

---

## 2. 目录结构与模块映射

本技能包由六大独立且互补的子模块组成：

| 模块目录 | 赛题范式映射 | 核心职责与交付成果 |
|---|---|---|
| [`01_overlay_manager/`](01_overlay_manager/) | **范式 1**：Overlay 加载与寄存器映射 | 跨平台健壮加载器、DTBO 解耦、64位寄存器映射与 HWH 校验器 |
| [`02_dma_buffer_guard/`](02_dma_buffer_guard/) | **范式 2**：DMA 搬运与缓存一致性处理 | 零拷贝物理连续环形内存池、自动 Flush/Invalidate 上下文管理器、看门狗超时防挂死 |
| [`03_contract_codegen/`](03_contract_codegen/) | **范式 3**：接口契约代码与测试骨架生成 | 从 Vivado `.hwh` 或 HLS `x*_hw.h` 一键自动生成强类型 Python 驱动类与 pytest 测试骨架 |
| [`04_golden_benchmark/`](04_golden_benchmark/) | **范式 4**：黄金参考比对与性能自动化报表 | 三级自动化比对工具（算法仿真对比、3帧软硬 Smoke、1000帧稳态压测）、实时 FPS/延迟与坏帧报告生成器 |
| [`05_troubleshooting/`](05_troubleshooting/) | **踩坑清单**：常见错误与结构化定位方法 | 总结 7 大经典软硬件死锁与总线故障的触发条件、现场排查与对策 |
| [`06_prompt_workflows/`](06_prompt_workflows/) | **提示词工作流**：人机大模型协同设计范式 | 软硬件任务划分、HLS 接口收敛约束、PS 端算力瓶颈诊断三组验证提示词模板 |

---

## 3. 快速上手指南 (Quick Start)

### 3.1 极简 Overlay 加载与寄存器控制
```python
from skill.overlay_manager.overlay_loader import UniversalOverlayLoader
from skill.overlay_manager.register_map_inspector import RegisterMapInspector

# 1. 跨板卡自动兼容加载 (自动处理 KV260 的 fpgautil/dtbo 与传统 Zynq-7000)
overlay = UniversalOverlayLoader.load(
    bitfile_path="accelerator.bit",
    dtbo_path="accelerator.dtbo"
)

# 2. 自动校验 HWH 契约与 64 位拆分寄存器
inspector = RegisterMapInspector(overlay.my_ip)
inspector.verify_contracts(required_registers=["input_addr", "output_addr", "length"])
```

### 3.2 零拷贝 DMA 环形缓冲池与安全执行
```python
from skill.dma_buffer_guard.dma_buffer_pool import DmaBufferPool
from skill.dma_buffer_guard.cache_coherent_guard import CacheCoherentGuard

# 1. 初始化预分配物理连续内存池 (避免动态 allocate 碎片化)
pool = DmaBufferPool(buffer_shape=(1080, 1920), dtype="uint16", pool_size=3)

# 2. 安全执行：自动处理 CPU Cache Flush -> 硬件启动 -> 看门狗检测 -> Cache Invalidate
guard = CacheCoherentGuard(overlay.my_ip, timeout_seconds=1.0)

with pool.acquire() as in_buf, pool.acquire() as out_buf:
    in_buf[:] = source_data
    with guard.run_hardware(in_buf, out_buf):
        # 此时 PL 硬件已成功运行完毕，out_buf 已被 invalidate，CPU 可安全直接读取
        result = out_buf.copy()
```

### 3.3 自动生成 Python 驱动代码
```bash
python skill/contract_codegen/codegen_pynq_driver.py \
    --hwh path/to/design.hwh \
    --ip my_ip_instance \
    --output generated_driver.py
```

