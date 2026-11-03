# PYNQ tools and workflows

| Directory | Purpose | Verification |
|---|---|---|
| `contract_codegen/` | Current HWH/header register parser and driver generator | Actual 2021.2/2025.2 HWH contract regression; no hardware required |
| `reviewed_tools/` | Buffer lifecycle, overlay plans, benchmark helpers | Offline/mocked tests; board validation pending |
| `overlay_preflight/` | Read-only overlay/artifact preflight | Local fixtures and syntax checks |
| `legacy_tools/` | Six originally submitted modules, retained for review and attribution | Contains earlier implementation issues; use reviewed tools above as the current entry |

旧版六模块按原始来源保留，当前入口使用上表的 `contract_codegen/`、`reviewed_tools/` 与 `overlay_preflight/`。PS运行时保持当前配套实现。

仓库文件统一小写。安装到要求 `SKILL.md` 文件名的代理时，将相应 `skill.md` 复制为该环境的 `SKILL.md`；无需修改仓库命名规则。
