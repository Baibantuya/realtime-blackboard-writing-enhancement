# Session 2026-10-19-012: v20 200MHz Server Synthesis, BRAM Optimization, and Delivery Package Download

## 1. 任务背景与用户目标
- **目标**：针对 `kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v20`，在服务器上完成综合实现与打包，并下载到本地开发区，供后续连板实机测试。
- **用户明确授权与指示**：
  1. “你把这一版上服务器综合，综合完打包下载下来，明天连上板子再上板。综合时候注意隔三差两看一眼就行”
  2. “不行删掉一点ila，或者做简单一点，再不行扔uram一点”
  3. “如果有时序违能生成比特流的话就拿下来”
- **操作边界**：本轮**严禁上板**，仅限服务器综合、生成 bitstream/打包、下载到本地开发区并记录决策。

---

## 2. 关键排查、架构决策与纠正记录

### 2.1 BRAM 资源超限 (DRC UTLZ-1) 根因与优化
- **现象**：在初次 `place_design` 时发生 DRC 拦截：器件物理容量上限 288 个 RAMB18，实际请求 301 个（超限 13 个）。
- **根因分析**：为了全观测 281 位 FSM，`ila_restore_fifo` 宽度扩大至 512 位（占用 32 个 RAMB18），叠加总线监测 `ila_restore_axi`（占用 27 个 RAMB18），双 ILA 造成严重挤压。
- **决策实施 (D-121)**：
  - 在 `vivado/add_xvc_debug.tcl` 中注释移除了冗余的 `ila_restore_axi`；
  - 保留核心的 `ila_restore_fifo`（宽度 512，深度 1024，包含全部 281 位 Top FSM 状态）；
  - 全芯片 RAMB18 降至 274 个（95.14%），完美消除 DRC 报错。
- **配套修改**：更新 `scripts/check_restore_debug_wiring.py`，移除 `ila_restore_axi` 断言，验证 70 项 AXI 三端走线与 1 项原生探针 100% PASS。

### 2.2 流程与工具链问题纠正
- **服务器 IP 校正**：此前尝试连接的备用 IP 重置，依据 `PROJECT_STATE.md` 确认正确综合服务器为 `[private_ip]`。
- **脚本环境变量与 Bootgen 适配**：
  - `run_system_vivado.sh` 补充 `PY=python3` 定义；
  - `bootgen` 针对 ZynqMP BIF 文件的相对路径问题，剥离路径使用基名，成功转换 `.bit.bin`；
  - `prepare_overlay.py` 修复 Python 3.6 环境下 `subprocess.check_output(text=True)` 的兼容性（改为 `universal_newlines=True`），成功生成 `.dtbo`；
  - 补充 `wb_frame_pool.ko` 等内核驱动物料，确保整包平铺完整。

---

## 3. 验证结果与物料清单

### 3.1 时序与硬件网表签核
- **处理时钟**：200MHz 极限实验态；
- **时序签核指标**：
  - `WHS = +0.010 ns`（保持时间完全达标，零 Hold 违例，`THS = 0.000`）；
  - `WNS = -2.019 ns`（33 个 setup 违例端点，符合用户预期的实验态比特流）；
- **比特流文件**：`design_1_wrapper.bit`（7,797,812 字节，签发成功）。

### 3.2 交付物料（已下载至本地）
- **交付压缩包**：`kv260-whiteboard-enhance/rtl/dma_rgb565_quality_v20/delivery/whiteboard_rgb565_quality_v20_200mhz_board.zip`
- **文件体积**：7.5 MB
- **SHA256 校验**：`f30713b9031e270428f5bdef0d63ea3b9b95db1e4a54b12b951fe9cbd2df3d8c`（与服务器端 `SHA256SUMS` 100% 一致）；
- **解压完整性**：解压至 `board_package/` 验证包含全部 71 个必备固件、驱动与软件脚本。

---

## 4. 下一步计划（待连板后执行）
1. 物理连接 KV260 板卡，上电建立网络连接；
2. 执行安装部署与 3 帧 smoke 验证；
3. 针对白板擦除、蓝黑颜色识别与噪点抑制进行实拍评测。
