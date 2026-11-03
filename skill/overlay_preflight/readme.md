# pynq-overlay-preflight 0.1

2026-10-27增量：检查器实现与V22配置/历史结果保留；新增 [v24_slim_profile.json](examples/v24_slim_profile.json)，用于 `evidence/20261027/runtime_v24`。该配置为本次观测快照，另由三份真实HLS头文件交叉核对；结果439 pass / 0 fail / 8 not_checked。schema 2 runtime清单由独立脚本核验，不传给原通用manifest解析器。V22旧入口问题不适用于V24。见 [本轮结果](../evidence/v24_review_20261027.md)。

状态：可运行的离线检查器与Skill草稿，未板测、未跨板实测、未安装为全局Skill。

适用：已有Vivado HWH和 `.bit` 的PYNQ候选发布包，审查文件配套、清单/身份及明确给定的HWH契约。UTF-8 XML、PROPERTY式寄存器字段；其他HWH方言或不能唯一定位的层级需另行适配。只用Python标准库，本轮环境见验证记录。

输入：只读发布根目录、JSON profile；可选包清单、身份JSON、板端环境记录。输出：JSON中的pass/fail/not_checked、预期与实际差异；退出码0表示PASS_OFFLINE，1表示FAIL，命令行用法错误可返回2。

在本工作区根目录运行：

```powershell
python skill/pynq-overlay-preflight/scripts/preflight.py --root evidence/20261022/selected_v22 --config skill/pynq-overlay-preflight/examples/v22_profile.json
python skill/pynq-overlay-preflight/validation/test_preflight.py
```

独立使用时只需复制本技能目录并提供自己的输入根目录。V22输入大文件保留在工作区证据中，不嵌入通用脚本。可把stdout重定向到新的报告文件；不要覆盖输入原件或旧证据。

检查内容：必需文件非空与SHA256/可选大小；bit/HWH同目录同基名；MANIFEST中配置文件的哈希/大小和release；身份字段；IP FULLNAME/VLNV；寄存器存在性、偏移、宽度、可选访问类型与位字段、所检查寄存器间重叠；控制地址范围；已有环境记录与期望的字面值比较。路径限制在输入根目录内，不接受越界或指向根外的符号链接。

失效条件：文件缺失/不匹配、IP或寄存器漂移、XML/JSON不可解析、契约不完整、未知配置字段、地址歧义时返回FAIL。缺失实际板端环境返回not_checked。DTBO仅比较字节，没有解析 `firmware-name`/绑定；驱动仅核对配置的文件字节，没有检查模块vermagic/运行ABI。所有not_checked必须在最终结论中保留。

验证：真实V22副本9文件、3IP、70寄存器对照；23项构造测试包括合成的其他IP名称/地址/后端和异常输入。合成bit/DTBO只是占位字节，绝不能下载。详见 [validation/README.md](validation/readme.md)。PASS_OFFLINE不证明独立构建来源、位流内部功能、同次构建、已加载状态或系统正确。

经验来源：V22配套文件及清单；加载器check-only副作用；Q的实例名仍为 `board_quantize_rgb_0`，实际VLNV却是 `board_scene_quantize`，需检查类型而非名称猜测；本轮发现旧入口预检冲突。来源与真实AI原文状况见 [来源经验](references/provenance.md)。
