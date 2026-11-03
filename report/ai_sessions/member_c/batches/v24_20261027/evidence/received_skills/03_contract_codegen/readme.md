# 模块 03: 接口契约驱动与测试骨架代码生成器 (03_contract_codegen)

## 1. 适用范围与功能职责

### 适用场景
- 任何通过 Vitis HLS、Vivado IP Packager 导出自定义 AXI-Lite 控制接口的加速核；
- 每次 HLS 修改算法签名（参数增加、位宽调整、重新综合）后，需要主机 PS 端 Python 驱动无缝同步；
- 希望在没有实际上板前，在宿主机或 CI 环境中通过生成的测试骨架进行 Mock 单测。

### 核心功能
1. **多源接口契约解析**：
   - 支持解析 Vivado 导出的 `.hwh`（XML 格式的硬件元数据）；
   - 支持解析 Vitis HLS 自动导出的 C 驱动头文件（`x<ip_name>_hw.h`）；
   - 支持解析轻量级 JSON 寄存器配置文件。
2. **强类型 Python 驱动自动生成**：
   - 自动生成符合 PEP 8 与 Python 3 强类型提示的 IP 控制类；
   - 自动识别 64 位物理地址拆分（`low_word = addr & 0xFFFFFFFF`, `high_word = addr >> 32`）；
   - 自动包装 `AP_CTRL`（`start()`, `is_idle()`, `is_done()`）与状态机看门狗等待。
3. **即用型单元测试骨架生成**：
   - 同步生成基于 `unittest` / `MockIP` 的测试骨架，可在任何未连接板卡的开发机上一键运行验证。

### 失效条件
- HWH 文件损坏或缺少 `<MEMORYMAP>` 节点；
- C 头文件宏定义格式严重非标准（本脚本原生支持 Vitis HLS 2020.1 ~ 2026.1 标准生成格式）。

---

## 2. 命令行使用方法

### 2.1 从 Vitis HLS C 头文件生成
```bash
python skill/03_contract_codegen/codegen_pynq_driver.py \
    --input path/to/xmy_ip_hw.h \
    --class-name MyAcceleratorIP \
    --output my_accelerator_driver.py \
    --generate-test
```

### 2.2 从 Vivado HWH 生成
```bash
python skill/03_contract_codegen/codegen_pynq_driver.py \
    --input path/to/design_1.hwh \
    --ip my_ip_instance_name \
    --class-name MyAcceleratorIP \
    --output my_accelerator_driver.py \
    --generate-test
```

---

## 3. 经验来源与失败复盘

本模块直接源自项目中的以下排查实证：
1. **人工维护寄存器偏移极易错位**：在 v18 到 v19 升级过程中，HLS 增加了一个配置寄存器导致后续寄存器基址发生 4 字节偏移，人工修改 Python 字典漏改一项，导致板端配置错位、模块拒绝流出数据。
2. **通过接口契约代码生成彻底杜绝人因失误**：自动从 HLS 输出的 `_hw.h` 提取权威偏移，生成包含断言的强类型代码，实现“硬件接口一改，代码秒级同步”。
