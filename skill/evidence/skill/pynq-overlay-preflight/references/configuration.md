# JSON配置约定（schema 1）

全部文件路径使用相对于 `--root` 的POSIX路径。profile本身可在根目录外。核心顶层字段如下，未知字段返回FAIL，避免拼写错误被静默忽略。

| 字段 | 要求/含义 |
| --- | --- |
| schema | 整数1 |
| release | 必填非空发布标识 |
| backend | 必填文字标签；仅记录，不运行任何命令 |
| target_part | 可选器件声明；脚本不解码bit器件，因此保留target_device未检查 |
| files | 必填对象，至少bit/hwh两个角色；其他角色如dtbo、bit_bin、驱动由平台配置。每项 `path`、64位小写sha256，可选正整数size |
| manifest | 可选 `{"path":"MANIFEST.json"}`；支持其 `release` 和 `files: {path: {size,sha256}}` 格式，只检查profile列出的文件 |
| identity | 可选 `path` 和非空 `fields` 对象，对顶层JSON字段精确比较；无嵌套路径表达式 |
| ips | 必填非空列表。每项fullname对应HWH FULLNAME，vlnv精确匹配，registers非空 |
| environment | 可选 `expected`对象、`record`相对路径；按顶层字段精确比对，不采集环境/不执行命令/不判断版本范围 |
| provenance | 可选文本，说明预期值来源；作为资料说明，不提供真实性认证 |

每个IP的registers使用原始HWH REGISTER NAME（如CTRL而非程序别名AP_CTRL）；每项包含offset/width，可选access和fields。fields按字段名给出offset/width，对应BIT_OFFSET/BIT_WIDTH。偏移/宽度可用整数或 `0x` 字符串；只支持字节整宽、32位对齐的常见寄存器，单寄存器最多4096位。非标准布局需适配后重新测试。

IP可选 `address: {interface,base,high}`，对应MEMRANGE的SLAVEBUSINTERFACE和闭区间BASEVALUE/HIGHVALUE，MEMTYPE要求REGISTER。实例名不唯一时拒绝猜测归属；重复相同地址记录折叠后比较。

示例结构（以下片段省略了真实哈希，不应直接执行；完整可执行配置见 [v22_profile.json](../examples/v22_profile.json)）：

```json
{"fullname":"/example_0","vlnv":"vendor:library:example:1.0",
 "registers":{"CTRL":{"offset":0,"width":32,"fields":{"AP_DONE":{"offset":1,"width":1}}}},
 "address":{"interface":"s_axi_control","base":"0x40000000","high":"0x4000ffff"}}
```

脚本不会将其他字段如DTBO firmware-name、位流器件号、驱动ABI或系统资源使用量从外部猜出；这些明确列为not_checked。对没有manifest/identity的最小项目，只能报告其profile对照，不报告发布来源已认证。

V22 profile中的期望寄存器是本轮观察HWH冻结的回归快照；不是另外独立编写、经过硬件验证的规格。未来新版本不能直接重跑生成器覆盖该profile。本工作区的 `tools/record_review.py`只用于本次快照且拒绝覆盖有差异的profile。
