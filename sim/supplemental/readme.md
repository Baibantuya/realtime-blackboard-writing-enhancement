# Supplemental validation and isolated candidates

这些资料接续 C5/R5 冻结后的本机验证。Rectify 63 次小图、12 次最大宽高边界调用及 18 次复位事件已有通过记录；完整 1080p RTL 输出比较待完成。AE AXIS Monitor 元数据和 DTBO 三项能力声明修正均为独立候选，尚未合并本包 C5 位流。

子目录源码/脚本中的历史路径用于说明原实验现场；本目录不属于 `build/run_all.*` 的硬件输入。当前主工程重建使用 `src/`、`sim/tb/` 和 `build/`。如要合并 AE 候选，需要重新完成整机布局布线；DTBO 候选需要板端驱动检查。

`local7/readme.md` 记录完整帧联仿内存增长的最新定位：初始化已结束，增长发生于 RTL 运行期间。早期记录中“卡在初始化”的判断保留为历史过程。
