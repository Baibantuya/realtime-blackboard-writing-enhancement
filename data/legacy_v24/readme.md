# V24 测试数据与参考结果

`v24_scene_cosim/` 来自原 V24 量化核工程 `build/board_scene_quantize_hls/solution1/sim/tv/`，不是本次生成的演示数据。

- `cdatafile/*autotvin*`：原 C/RTL 联仿输入，含控制寄存器和接口内存快照。
- `cdatafile/*autotvout*`：原 C 模型参考输出。
- `rtldatafile/*autotvout*`：原 RTL 仿真实际输出。

本次已核对 C/RTL 的 `gmem1` 输出逐字节一致、9 次返回值序列相同。比较工具为 `sim/compare_scene_vectors.py`，它不会重新执行仿真。

数据是 Vitis 自动生成格式，部分文件含二进制负载，不应强行按文本或普通图像读取。为避免混淆，没有加入 V24 早期失败 PS 版本的实拍图，也没有把这些合成数据当作当前现场视觉验收。
