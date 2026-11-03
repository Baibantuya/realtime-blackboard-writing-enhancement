# U01：历史X11执行记录索引

2026-10-22通过Codex只读接口再次读取“项目综合”的四个已选轮次，补取14条运行verify_x11_interaction.py的可见执行记录；2026-10-23整理本索引。下面均为历史执行，本轮没有运行这些命令。

[原始可见字段JSON](../../../evidence/ui_history/conversation_tools_and_images.json)保留thread/turn/command ID、命令、退出码、状态和输出；另有两项localImage路径及21项imageView引用。只选取相关可见字段，没有导出隐藏推理或完整工具历史。

| 结果目录 | 退出码 | 可见结果 | 平台command ID |
| --- | --- | --- | --- |
| x11_01 | 1 | AssertionError：未取得main预期截图 | `exec-95e1cad1-0975-4996-b9d6-b9cfb03af666` |
| x11_02 | 0 | 37项交互/截图检查通过 | `exec-0b14403a-560a-4931-9e35-df35a6527c26` |
| x11_03 | 0 | 37项交互/截图检查通过 | `exec-65681237-4727-4e2a-a2e9-6610cd237526` |
| x11_04 | 0 | 37项交互/截图检查通过 | `exec-3f84880d-9647-4823-8dff-62a1a7a35c4c` |
| x11_05 | 1 | AssertionError：未取得startup-collapsed预期截图 | `exec-0cb41552-0a3f-4177-8dab-52e571c34db3` |
| x11_06 | 1 | AssertionError：未取得startup-collapsed预期截图 | `exec-1d2e0f1e-ce4b-4e7a-ba2a-3fb3fb6e5df1` |
| x11_07 | 1 | AssertionError：未取得startup-collapsed预期截图 | `exec-34d8bc24-0f6c-4f03-9c16-5c9f126d31ad` |
| x11_08 | 1 | AssertionError：未取得startup-collapsed预期截图 | `exec-f3634831-c614-4d99-9ab9-fb392e7a0c30` |
| x11_09 | 1 | xdotool鼠标同步移动超过8秒超时 | `exec-4649ecd5-ff0a-4a14-a173-e32c492e2035` |
| x11_10 | 1 | AssertionError：Mouse did not reach our test target | `exec-a89b0c8e-8e64-48cf-b6c8-c7506ec68d0e` |
| x11_11 | 0 | 47项交互/截图检查通过 | `exec-e37e262d-070e-4a88-94c4-a65e20400ef4` |
| x11_12 | 0 | 64项交互/截图检查通过 | `exec-7be42df8-07f8-4fb4-9fce-391837b7fce9` |
| x11_13 | 0 | 64项交互/截图检查通过 | `exec-c0580ba3-c6b6-4ddd-a722-3755c1c8ca06` |
| x11_14 | 0 | 65项交互/截图检查通过 | `exec-f829083d-e37b-43da-963c-f3234becd405` |

## 如何与图片、消息对应

- x11_01–04对应Linux适配轮次，37项通过后的x11_04图由U12链接；x11_04输出还记录导出82份记录/截图。此数字是当时导出数，不是本轮归档数。
- x11_05–11对应U13/U14/U16的文案、颜色和收起反馈；x11_11形成47项回执，U23给出窗口图。
- x11_12/13对应自动隐藏和Medium尝试所在轮次；U35链接Medium图。x11_14对应用户恢复Regular并放宽资源限制后的最终轮次，U41链接最终图。
- 精确轮次ID和命令以JSON为准；[证据链](evidence_chain.md)与[附件索引](attachment_index.md)连接到原消息，不把目录号当独立时间戳。

## 输出与结论边界

14条记录的output.truncated均为false，但只说明此次返回的这些输出未标为截断，不能证明整个会话完整。部分输出开头保留原接口返回的WSL乱码/空字符；没有将清理后的文本冒充原输出。

表中检查数量取自末尾“interaction/capture checks”汇总和对应回执，不是逐行计算PASS字符串数量。7条非零退出与7条零退出发生在不同版本/步骤，不能当可靠性抽样；单凭截图超时也不能断定产品UI本身失效。失败定位须结合当时可见解释和具体测试条件。

x11_04/11/12/13回执未记录二进制哈希；最终x11_14的哈希不能回填给早期版本。全部范围仍为WSL/WSLg合成界面、X11输入，不能延伸为KV260验收。
