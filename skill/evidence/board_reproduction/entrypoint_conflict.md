# V22交接预检入口冲突（已确认，未修复）

2026-10-27范围说明：本页仅为V22历史案例。V24 slim已改为schema 2与app/main.py，启动链已重新核查，不能沿用本页失败结论。当前说明见 [V24复现](readme.md)。

发现日期：2026-10-22。来源：原始V22 ZIP中的 `board/runtime/deployment.json`、`verify_runtime.py`、`kv260_board_run.py`、`run.sh`。所有相关副本哈希与MANIFEST一致，详见 [source_review.json](../evidence/20261022/source_review.json)。

配置实际值：`deployment.json.live[1] = "{dir}/run_ps_runtime_v2.py"`。

`verify_runtime.py` 在 `verify_package(root)` 返回后检查：

```python
if config['live'][1] != '{dir}/run_stage_pipeline_archive.py':
    raise RuntimeError('Deployment does not select the v22 archive UI entry')
```

`run.sh check`和`deploy`均进入 `prepare_check`，其 `preflight`配置调用 `verify_runtime.py --board`。因此，前面的包验证即便通过，仍会在该条件抛错。若前面的包验证失败，则更早停止；本轮没有运行整个预检链，也不声称已取得板端实际报错。

验证方法：本轮工具用AST提取这个字面量，再与原始JSON比较，结果 `stale_entry_guard_would_raise: true`。没有import交付模块，没有访问FPGA/相机/设备，也没有制造原始历史日志。该发现不否认历史上“已加载同一硬件、手动启动v2”的运行记录；两种路径不同。

建议PS维护者在**新的发布副本**中使预检与正式v2入口契约一致，并核对UI/ABI/驱动检查仍有效；增加该入口的离线回归，重建system_manifest、bundle、MANIFEST及发布身份所需哈希，然后验证完整check与冷启动。不能绕过全部预检，也不建议直接修改原包后忽略校验失败。

本轮没有实施这项源程序修改；其状态保持M01，等待新发布证据。若新vision版本已修复，应比对新源码和对应输出后再关闭。
