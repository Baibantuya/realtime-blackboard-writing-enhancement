# DMA 与加载边界

`DmaBufferPool` 必须传入真实分配器或显式 mock 分配器。无 PYNQ 时不会悄悄生成假物理地址。接口面向单个所有者线程，跨线程访问会失败；不负责多进程 DMA 所有权仲裁。

`with pool.acquire() as lease` 返回 Lease；CPU 数组通过 `lease.buffer` 访问。启动前应按已审阅寄存器契约配置地址，并把 PL 会访问的所有缓冲作为 leases 传给 guard。调用者仍能绕过 API，因此不能将此 Python 状态机当作硬件隔离机制。

状态：free → leased → in_flight → leased → free。任何启动写、轮询、完成确认或缓存失效异常都转为 quarantined；退出上下文不会使其 free。输入和输出在启动前 flush；确认完成后对输出 invalidate。guard 限定 ap_ctrl_hs 单次启动，拒绝 auto_restart；不是 AXI DMA SG、自动重启或通用流式引擎驱动。

`completion_confirmed(ip, status)` 必须来自特定 IP 的完成/总线排空约定。本候选不会因为通用 DONE 位就自行认定一切 DMA 已结束。轮询预算只约束能够返回的 MMIO 调用，不能打断阻塞于总线访问的内核调用。

发生超时后，池保留强引用并拒绝复用和 close；Python GC 不会在此进程内回收这些隔离对象。需要由板级流程先阻止继续提交、停止相关 master、确认 outstanding 访问归零，必要时依授权复位，再以 `pool.recover(verify_quiescent=..., reason=...)` 提交证据。返回 False 或抛异常都保留隔离。mock 恢复回调只用于测试，不能复制成真实 `lambda: True`。

<span style="color:#C00000">【待核验】强引用只在当前进程有效，不能保证进程死亡或 fd 关闭后 CMA 仍保留；异常退出、停止、复位与内核驱动的协作必须板测。当前代码不提供进程退出保护，也不承诺防止 D 状态。</span>

Overlay 的 `inspect_overlay()` 只读文件并比较显式哈希；KV260 计划要求独立元数据目录和显式 DTBO。`execute_overlay()` 明确未实现。未来加载后端需独占进程/设备、DMA 停稳检查、受控卸载目标、子进程超时与失败后状态确认。进程超时不能自动触发再次加载。不能以 `/sys/class/fpga_manager/fpga0/state` 存在判断平台或后端可用。

V24 原加载器的 `--check-only` 仍会复制文件/处理状态，不能作为本地只读测试；详见 [运行说明](../../evidence/board_reproduction/readme.md)。
