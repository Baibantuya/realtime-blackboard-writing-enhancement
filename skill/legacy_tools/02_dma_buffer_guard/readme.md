# 模块 02: 可复用 DMA 缓冲池与缓存一致性安全守卫 (02_dma_buffer_guard)

## 1. 适用范围与功能职责

### 适用场景
- 任何通过 AXI DMA、AXI Master 或 VDMA 在 PS (ARM) 与 PL (FPGA) 之间交换高带宽数据的 PYNQ 项目；
- 音视频流、高频特征向量、大矩阵或批量传感器数据的连续传输；
- 对吞吐率（FPS）、延迟稳定性有严格要求，绝不允许由于内存碎片化导致程序中途崩溃的生产场景。

### 核心功能
1. **连续物理内存池（Zero-Copy Buffer Pool）**：在系统启动阶段一次性完成 CMA 连续物理内存申请，运行时通过环形队列借还（Acquire/Release），彻底杜绝由于动态调用 `pynq.allocate` 引发的内存碎片化与操作系统 OOM；
2. **物理地址碰撞拦截**：硬件加速中输入输出内存重叠是致命的总线错误。缓冲池在借出前自动校验 `in_buf.physical_address` 与 `out_buf.physical_address`，物理边界重叠时直接阻断；
3. **缓存一致性安全上下文管理器（Cache Coherency Guard）**：
   - 启动前强制调用 `input_buf.flush()`：将 CPU L1/L2 Cache 中的脏数据推入 DDR，保证 PL 读到最新内容；
   - 硬件计算中配备**看门狗超时监控**：绝不使用无超时无退出的死循环轮询，超时自动报警并保全总线；
   - 计算完成后强制调用 `output_buf.invalidate()`：使 CPU L1/L2 Cache 失效，强制 CPU 从物理 DDR 重新拉取 PL 写入的最新运算结果。

### 失效条件
- 系统预留的 Linux CMA 内存池过小（可通过 `dmesg | grep cma` 查看，若不足需在 bootargs 调整 `cma=512M`）；
- 硬件在超时后依然死锁并独占总线，此时禁止直接调用 `freebuffer()`，必须先行对 PL 实施复位或断开 AXI 事务。

---

## 2. 核心 API 与使用范式

### 2.1 预分配连续内存池
```python
from skill.dma_buffer_guard.dma_buffer_pool import DmaBufferPool

# 初始化 3 级乒乓环形缓冲池（1080p RGB565 帧尺寸）
pool = DmaBufferPool(
    buffer_shape=(1080, 1920),
    dtype="uint16",
    pool_size=3
)

# 借出缓冲区
with pool.acquire() as in_buf, pool.acquire() as out_buf:
    # 填充输入数据
    in_buf[:] = camera_frame
```

### 2.2 缓存一致性与看门狗执行
```python
from skill.dma_buffer_guard.cache_coherent_guard import CacheCoherentGuard

guard = CacheCoherentGuard(ip_handle=my_ip, timeout_seconds=1.5)

# 使用上下文管理器安全运行
with pool.acquire() as in_buf, pool.acquire() as out_buf:
    in_buf[:] = camera_frame
    
    with guard.run_hardware(in_buf, out_buf):
        # 退出上下文时硬件已完成 ap_done，且 out_buf 已完成 invalidate
        pass
    
    # CPU 安全使用计算结果
    result_array = out_buf.copy()
```

---

## 3. 经验来源与失败复盘

本模块直接源自项目中的以下排查实证：
1. **缓存未失效导致的偶发性像素脏读**：早期处理流程在读取 PL 输出时偶尔出现横向白噪点与重影。排查确认 CPU L2 缓存命中机制导致未从 DDR 读取最新帧。封装 `invalidate()` 上下文后彻底解决。
2. **硬件挂死导致的僵尸进程与内核死锁**：启动测试在等待硬件空闲时使用无超时的无限循环，在摄像头断流时进程永久死锁，`SIGTERM` 无法响应。引入看门狗硬超时机制，超时主动抛出 `HardwareTimeoutError`。
