# PYNQ 寄存器生成器候选修正

2026-10-29。候选文件为 `codegen_pynq_driver.py`。原 submission_v24 的 Skill 文件没有替换；本目录生成的类只是低层寄存器访问骨架，不是整机 PS 调度器或可直接启动的视频应用。

## 修复内容

- 正确读取 HWH 中 REGISTER 的直接 PROPERTY 子项，也兼容属性形式及 PROPERTIES 容器；不会把 FIELD 内的 ADDRESS_OFFSET 当作寄存器地址。缺失偏移不再默认写入 0。
- 使用完整实例名匹配，拒绝模糊命中、多实例歧义、重复地址、重叠寄存器、非对齐地址及冲突元数据。
- 保留应用寄存器 `control`（0x68），只跳过地址 0 的标准控制寄存器。
- 识别实际 HLS 头文件中的下划线名称、位宽，以及 HWH 的只读／只写属性。64 位字段写入高低两个字，拒绝越界地址；只读 `_1/_2` 字段不会误生成可写指针。
- 自动生成的测试使用实际输出文件名导入，解决自定义类名与模块名不一致的问题。

## 实际结果

Windows Python 3.12 与 WSL Ubuntu 22.04 Python 3 均通过 19 项 unittest；见 `final_tests_windows.log`、`final_tests_linux.log`。真实 v24 和 R5 HWH 各有三个自定义核，共 70 项寄存器元数据。旧生成器每版有 67 处地址不符，候选为 0 处；所有非控制寄存器的 Mock 读写地址均核对，恢复核每版另核对 7 对 64 位指针。见 `real_contract_result.json` 和 `audit_real_contracts.py`。

实际输入依赖原工作区的 `r5/` 及 v24 材料，因此本目录的真实合同测试不是脱离工程的独立演示包。只运行已生成的 `generated/` 类不需要这些构建目录，但调用者仍须提供匹配的 IP 句柄。

```powershell
python -m unittest discover -s . -p "test*.py" -v
python audit_real_contracts.py
```

输入示例：`python codegen_pynq_driver.py --input design_1.hwh --ip whiteboard_restore_0 --class-name RestoreDriver --output restore_driver.py --generate-test`。文件名仅为示例，需换成实际 HWH 路径和实例名。

<span style="color:#C00000">【范围限制】未执行 PYNQ 硬件 MMIO／DMA；生成器默认标准 ap_ctrl_hs 控制协议，不适用于所有 AXI 外设。普通 JSON 地址字典没有位宽／权限元数据时仍按 32 位可读写处理；旧式 `_1/_2` 命名是本项目约定，不能推广为所有 IP 的指针规则。多字读取不保证原子性，生成骨架不会自动处理缓存、物理内存分配或视频流水调度。</span>

失败记录按阶段保留。`readonly_pair_before.log` 是测试类名写错导致的测试入口错误，真正的修复前断言失败是 `readonly_pair_before_valid.log`；不要混用。最初 temp 清理权限问题及审计脚本对指针对应方法的误判也保留为工具／测试框架记录，不计为硬件缺陷。
