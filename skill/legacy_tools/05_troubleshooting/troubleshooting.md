# PYNQ 软硬件协同踩坑清单与故障排查指南 (TROUBLESHOOTING)

本清单严格对应《全国大学生嵌入式芯片与系统设计竞赛（AMD 赛题）》第 **3.3.5.2 节（踩坑清单）** 规范要求。汇总了基于 AMD Zynq-7000 / Zynq UltraScale+ (KV260 / ZCU104 / PYNQ-Z2) 进行 PYNQ 软硬件协同开发中最具杀伤力、最易被误判为“硬件时序坏了”或“芯片损坏”的 **7 大典型故障**。

每一项故障均包含：**现象描述、触发机理、现场诊断命令、已验证的根治方案，以及工程事实来源**。

---

## 故障 1: 视频流首帧超时 / 内核报 `Stream Line Buffer Full!`

### 1. 现象描述
启动摄像头采集或视频加速流时，程序在首帧或连续运行十几次后突然卡死，`dmesg` 抛出：
```text
[  124.582103] xilinx-csi2rxss a0000000.mipi_csi2_rx_subsystem: Stream Line Buffer Full!
```
用户态 `v4l2-ctl` 或 OpenCV 抛出 `VIDIOC_DQBUF: Resource temporarily unavailable`。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-18-004 (D-114)*。
- **机理剖析**：IP（如 Gamma / CSC / Scaler）的控制时钟来自 200MHz 视频时钟，而复位引脚 `ap_rst_n` 来自 PS EMIO GPIO（跨时钟域异步复位）。Linux 驱动在启动视频流时释放复位极其迅速，并紧接着背靠背全速向 AXI-Lite 写入几百个寄存器（如 LUT 表、宽高）。当异步复位释放与首轮总线写突发相撞时，AXI-Lite 状态机地址解码器发生亚稳态错位，将 Height 错写到 Width 寄存器，Height 寄存器变为 0。下游模块拒绝接收像素流，反压前级 FIFO，导致 CSI-2 接收端在 13 行后缓存满溢爆死。

### 3. 现场排查诊断步骤
1. 查看内核报错：`sudo dmesg | grep -E "csi2|buffer full"`；
2. 抓取流水线各 IP 的 AXI-Lite 寄存器：
   ```bash
   devmem2 0xa0010000 # 检查 Demosaic 宽高
   devmem2 0xa0030010 # 检查 Gamma Width (是否变成 1080)
   devmem2 0xa0030018 # 检查 Gamma Height (是否变成 0)
   ```

### 4. 彻底根治方案
- **硬件级（推荐）**：在 Vivado Block Design 中增加专用的硬件级复位同步器（`isp_rst_sync.v`），采用双触发器打拍消除亚稳态，并展宽复位脉冲至少 32 个时钟周期；
- **软件规避级**：在 PS 释放 GPIO 复位后强制插入 `time.sleep(0.01)`，确认 IP 处于 IDLE 后再开始突发写入寄存器。

---

## 故障 2: 画面偶发条纹、噪点或读到过时历史数据 (Cache Incoherency)

### 1. 现象描述
PL 硬件加速运算逻辑在 C 仿真（C-Sim）与波形仿真（RTL Sim）中结果 100% 正确，但上板后画面偶尔出现水平细横线、随机彩条，或者 CPU 读出的结果竟然是上一秒的旧画面。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-20-004 (D-137)*。
- **机理剖析**：现代 ARM Cortex-A53 / A72 具有两级高速缓存（L1/L2 Cache）。当 CPU 准备好数据后，数据实际上还驻留在 CPU Cache 中，尚未完全写穿到底层物理 DDR；PL 的 AXI Master DMA 直接从物理 DDR 读取，读到了未被刷写的脏数据。反之，当 PL 运算完毕将结果写入物理 DDR 后，CPU 试图读取该内存块时，由于 Cache 命中机制，CPU 直接读取了本地 Cache 中过时的数据。

### 3. 现场排查诊断步骤
在读取数据前后打印内存前 16 字节，对比物理 DDR 回读值与 CPU 数组值：
```python
print("CPU view:", buffer[:16])
buffer.invalidate() # 强制失效
print("DDR view after invalidate:", buffer[:16]) # 若两者不一致，证实发生了缓存不一致
```

### 4. 彻底根治方案
使用技能包中的 [`02_dma_buffer_guard`](../02_dma_buffer_guard/) 上下文管理器：
- **CPU -> PL (写输入)**：必须在启动 PL 前调用 `input_buf.flush()`；
- **PL -> CPU (读输出)**：必须在 PL 运行完成（`ap_done`）之后、CPU 读取之前调用 `output_buf.invalidate()`。

---

## 故障 3: 运行一段时间后报 `pynq.allocate` 失败 (CMA 内存耗尽)

### 1. 现象描述
程序启动初期完全正常，运行数分钟至数小时后，Python 突然崩溃并抛出：
```text
RuntimeError: Memory allocation failed.
```
同时系统 `dmesg` 打印：`cma: cma_alloc: alloc failed, req-size: ...`。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-24-001*。
- **机理剖析**：开发者在每一帧的主循环内部调用 `pynq.allocate((1080, 1920, 3), 'uint8')`。由于 Python 垃圾回收机制（GC）具有滞后性，且底层 Linux 内核管理 CMA 时连续物理页面的频繁释放与申请极易产生大量外部碎片，即使物理空闲内存足够，内核也无法凑出一段连续的 6MB 内存供 DMA 使用。

### 3. 现场排查诊断步骤
```bash
cat /proc/meminfo | grep -i cma
# 观察 CmaTotal 与 CmaFree。若 CmaFree 极小或频繁跳变，说明存在内存泄漏或碎片化
```

### 4. 彻底根治方案
使用技能包中的 [`02_dma_buffer_guard/dma_buffer_pool.py`](../02_dma_buffer_guard/dma_buffer_pool.py)：
- **预先分配原则**：严禁在每帧循环内动态 `allocate`；
- **环形乒乓池**：在系统初始化时一次性申请 3~4 块物理缓冲，通过 `with pool.acquire():` 借还复用；
- **安全析构**：在主程序捕获 `KeyboardInterrupt` 或异常退出时，统一致电释放（`pool.close()`）。

---

## 故障 4: PYNQ 加载 Overlay 报 `cannot readback configfs` 或系统挂起

### 1. 现象描述
在 KV260 / KR260 板卡上执行 `Overlay("my_design.bit")` 时，系统抛出：
```text
OSError: [Errno 2] No such file or directory: '/sys/kernel/config/device-tree/overlays/...'
```
或者连续加载 2 次后系统出现软死锁。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-18-005, 2026-10-26-002*。
- **机理剖析**：PYNQ 会自动探测比特流同目录下的 `.dtbo` 设备树文件。如果检测到同名 `.dtbo`，PYNQ 默认走 Linux configfs 动态设备树通道。然而在 Ubuntu 20.04/22.04 的定制内核中，configfs 针对特定 Xilinx FPGA Manager 节点的读回支持不完善，导致 PYNQ 判定加载状态失败；此外，若上一次运行异常终止，`/tmp/pynq/global_pl_state.json` 残留了指向已失效临时文件的路径，直接导致再次启动时抛出空指针异常。

### 3. 现场排查诊断步骤
```bash
ls -l /tmp/pynq/ # 检查是否有残留的全局状态
cat /sys/class/fpga_manager/fpga0/state # 检查硬件管理器是否为 operating
```

### 4. 彻底根治方案
使用技能包中的 [`01_overlay_manager/overlay_loader.py`](../01_overlay_manager/overlay_loader.py)：
1. 加载前自动调用 `clear_stale_pynq_state()`；
2. 针对 ZynqMP 平台，解耦底层烧录与元数据：通过官方 `fpgautil -b bit.bin -o dtbo` 载入硬件与时钟；随后使用 `Overlay(..., download=False, gen_cache=True)` 仅解析寄存器字典，彻底规避 configfs 缺陷。

---

## 故障 5: 异常退出时进程卡死在后台，无法使用 `kill -9` 终止

### 1. 现象描述
用户按下 `Ctrl+C` 试图终止脚本，终端打印退出提示后光标卡住；在另一个终端执行 `kill -9 <PID>` 依然毫无反应，进程变成 `D` 状态（不可中断睡眠状态 Uninterruptible Sleep），只能断电重启。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-26-002 (D-162)*。
- **机理剖析**：很多传统脚本的 `finally` 或 `close()` 块中写有类似逻辑：
  ```python
  finally:
      while not (ip.read(0x00) & 0x04): # 等待硬件 IDLE
          time.sleep(0.01)
      buffer.freebuffer()
  ```
  如果硬件是因为时钟丢失、AXI 流反压卡死等致命原因挂起，硬件将**永远无法进入 IDLE 状态**。此时进程在系统调用中陷入无超时的死循环；或者更严重的是：若在 AXI DMA 传输未完成时强行释放（`freebuffer`）物理连续内存，内核内存管理子系统会触发致命总线错误，进程被内核挂起在 `D` 状态。

### 3. 现场排查诊断步骤
```bash
ps aux | grep python # 观察 STAT 状态是否为 D 或 D+
sudo dmesg | tail -n 30 # 检查内核是否报 AXI transaction timeout 或 page fault
```

### 4. 彻底根治方案
使用技能包中的 [`02_dma_buffer_guard/cache_coherent_guard.py`](../02_dma_buffer_guard/cache_coherent_guard.py)：
1. 严禁无超时无退出的死循环轮询，任何状态等待必须有看门狗硬超时（如 2.0s）；
2. 硬件超时未响应时，标记硬件失步，**禁止盲目调用 `freebuffer()`**，抛出明确错误并交由上层重启脚本或硬件复位。

---

## 故障 6: ZynqMP 64 位平台下 PL DMA 寻址崩溃或报 `Bus Error`

### 1. 现象描述
在 32 位 Zynq-7000 (PYNQ-Z2) 上跑得好好的代码，移植到 64 位 ZynqMP (KV260 / ZCU104) 上后，只要启动 DMA，系统直接崩溃重启，或报 `Bus error (core dumped)`。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-19-013 (D-122)*。
- **机理剖析**：ZynqMP 的物理内存地址空间为 64 位。HLS 工具在综合包含指针的接口时，会自动生成两个 32 位的 AXI-Lite 寄存器：
  - `ptr_1`: 映射物理地址的低 32 位（Bit 0 ~ 31）；
  - `ptr_2`: 映射物理地址的高 32 位（Bit 32 ~ 63）。
  如果 PS 端代码依然按照 32 位惯性只写单寄存器 `ip.write(0x10, buf.physical_address)`，那么高 32 位寄存器将残留随机乱码。PL DMA 试图从该随机 64 位高地址读取数据时，直接触发 AXI DECERR（解码错误）导致总线挂死。

### 3. 现场排查诊断步骤
```python
# 打印实际物理地址
addr = int(buffer.physical_address)
print(f"Address: 0x{addr:012X}, Low: 0x{addr & 0xFFFFFFFF:08X}, High: 0x{addr >> 32:08X}")
# 检查 IP 内部高位寄存器读回值是否等于 High
```

### 4. 彻底根治方案
使用技能包中的 [`01_overlay_manager/register_map_inspector.py`](../01_overlay_manager/register_map_inspector.py) 的 `write_pointer_64` 函数，自动拆分写入低字与高字。

---

## 故障 7: ARM Cortex-A53 软件处理耗时击穿吞吐预算 (CPU 瓶颈)

### 1. 现象描述
PL 硬件加速耗时极短（例如 1080p 单帧只需 15ms），但端到端实际吞吐依然卡在 8~10 FPS，远达不到预期的 30 FPS。

### 2. 触发机理与失败复盘
- **工程来源**：*Session 2026-10-24-006, 2026-10-24-007 (D-159, D-160)*。
- **机理剖析**：开发者忽视了嵌入式 ARM Cortex-A53 CPU 与主机 x86 CPU 算力的巨大差距。在 PS 端 Python 脚本中看似简单的操作：
  ```python
  # 跨通道差分与阈值归约
  diff = np.abs(frame_a - frame_b)
  is_shadow = np.all(diff <= 4, axis=-1) & (np.ptp(diff, axis=-1) <= 14)
  ```
  在 PC 端执行只需 1.5ms，但在 ARM Cortex-A53 单核上，由于大量临时 3D 数组对象的创建与未经 NEON 优化的多次访存，耗时高达 **50.34ms ~ 112.6ms**！直接击穿了 33.3ms (30FPS) 的调度预算，导致系统进入频繁丢帧与 deadline hold。

### 3. 现场排查诊断步骤
使用单帧耗时分段探测法定位瓶颈：
```python
t0 = time.monotonic()
# step 1 ...
t1 = time.monotonic()
# step 2 ...
t2 = time.monotonic()
print(f"step1={(t1-t0)*1000:.2f}ms, step2={(t2-t1)*1000:.2f}ms")
```

### 4. 彻底根治方案
使用技能包中的 [`06_prompt_workflows/03_arm_cpu_bottleneck_audit.md`](../06_prompt_workflows/03_arm_cpu_bottleneck_audit.md) 进行排查指导：
1. **彻底消除每帧动态对象创建**：预分配临时缓存；
2. **改用底层 C++ / NEON 优化的库**：用 OpenCV 原生 API 替代多维复杂的纯 Python NumPy 规约（耗时可从 23ms 锐降至 1.7ms，提速 13 倍以上）；
3. **将粗粒度分析下采样到低分辨率（如 1/4 尺寸）**，保证嵌入式 CPU 耗时牢牢锁定在 5ms 安全预算以内。
