# AI Session: 2026-10-12-004-rgb565-pipeline-build
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 新独立RGB565全链/B16候选，远程Vivado并行构建，下载打包部署评估。
- Status: In progress
- Report candidate: yes
## Context Read
AGENTS/完整政策/状态/决策/索引/session003与002、Git及B32源码构建/runtime。输出长历史截断但当前相关章节已读取。
## Task and Constraints
用户授权全链修改、远程综合多任务并行、下载部署。最新纠正：借鉴A6/B32不用原参数，面积紧时用B16。旧实际包/板端备份保留，独立新文件夹无旧固件混入。
## Contributions
待补齐。
## Decisions and Adoption
全链标准RGB565 little-endian R[15:11]/G[10:5]/B[4:0]，宽AXI packed。数学/累加/状态不机械缩16bit；初步B16 line16/sets4/ways2，参数最终按验证选择。
## Commands and Tools
PowerShell、本地C++/Python/RTL、远程Vivado2021.2与板端KV260。
## Validation and Evidence
本次远程SSH配置114.212.10.200拒绝无密钥认证；实际历史Vivado为leisheng@[private_ip]，待连接。新综合/板测未执行。
## Errors and Corrections
读取默认SSH配置不是实际Vivado服务器；发现历史连接后纠正，未泄露凭据。
## Files Changed
本记录。
## Remaining Work
接口/源修改、native/RTL、远程构建/时序/匹配导出、包校验/下载部署/FPS/资源。
## Handoff Notes
当前板B32保持运行，A6/B32历史保留；仅构建匹配完成再切换。

## Implementation Progress
- 正式独立源码/测试/远程目录已建立，B32/A6原包和运行未改。实际远程leisheng@[private_ip]密钥可用。
- 565标准helper、restore input/output/background/previous与pixels FIFOs16bit、quantize窗口/流16bit和2word/4pixel pack、rectify源565/输出565完成。内部亮度/加法/坐标保持足够位宽。
- Native独立expanded888恢复baseline与numpy量化27组（3HD）PASS；额外golden TB quantize12（含stride/channel模式），rectify20小帧及恢复12帧PASS。
- 四IP实际HLS C/RTL仿真PASS：校正原HLS20/扩展共63调用；quantizer12；restore12独立黄金向量；capture565 SOF/TLAST/packing/stride。与手写fetch集成不同，不能把HLS nativefetch仿真当新fetch顶层仿真。
- 手写565 fetch消除cross-word，B16P4/P6 strict xsim矩阵进行；C99/Python独立黄金一致、真实AXI响应/背压/尾部/无效地址验证。
- 真RGB565相机writer独立HLS、V4L2异步媒体master wb565_control ARM64 kernel5.15.0-1027编译成功。原builtin xilinx_frmbuf保持不修改，新overlay禁用原DMA node；原六subdev由新master启动。当前未上板，实际bind/stream及RG16需板测。
- 8jobs/synth4threads/impl8threads整机启动，准备脚本只接受四matchingHLS导出与strict565 PASS。新565 HLS生成coordinate/pack/write/control+手写B16 fetch，不能复用旧RGB888 pack生成物。
## Errors and Corrections (During Work)
- Python3.9 Path.write_text newline不支持，改open(newline)。PowerShell通配/brace语法和一次嵌套python quoting错误后纠正；均保留在工具结果。
- 新shell首次CRLF导致pipefail错误，所有候选文本规范LF；工具patch仅候选launcher引用共享只读依赖。
- 恢复/capture cosim小帧TB未按m_axi最大depth分配，wrapper越界段错；纠正最大depth分配、同golden prefix比较后真实PASS。独立运行wrapper还需Vitisgcc6libstdc++，环境路径明确。一次resume使用HLS不支持绝对project名已改cd+相对名。
- vendor frame writer源码加密不可编辑，初读产生二进制乱码；停止读取，采用自有writer，不修改vendor。
- 初版capture RGB总线按RGB低R假设；官方UG934核对后改R高/B中/G低并重新综合/C-RTL全PASS，未将旧PASS用于发布。
- 无Icarus，改用远程Vivado xsim做同独立严格RTL矩阵。
## Files Changed (During Work)
新formal/source kernels/runtime/media driver/build/test/565 contract；测试native脚本/黄金；本记录/D-090。尚未修改部署配置或运行中的B32。

## Validations and Integration Update
- 四IP最终实际HLS RTL PASS/导出：rectify63/quantize12/restore12/capture1（SOF/TLAST与stride）；采集总线按AMD UG934 R高/B中/G低重新构建。
- B16P4和P6各五项strict xsim，10项全部PASS，C99/Python黄金一致，真实accepted outstanding/背压/非法地址/尾部验证。默认P4/window32/token32/line16/ways2。
- 混合IP完整来源包括同一次HLS导出的五个floating-point XCI，不把syn/verilog内缺少子IP当无实现。脚本核对真实XCI后通过闭包。
- Vivado初次XML编码utf8别名不被parser接受，改为UTF-8和标准namespace；后续新BD已完成接口/地址集成，正在生成系统目标。
- 新核/模块/显示已编译/仿真，不代表板端graph bind/DRM格式验证。B32运行仍未切换。

## Toolchain and Board Interface Update
- 整机BD验证通过；8jobs OOC实际启动。五个官方video HLS IP出现2026日期261011...超过旧revision int范围，使用原recover_generated_hls限定本候选run tree修复；等待其他本候选OOC正常结束后并行恢复，不修改共享安装或旧工程。
- 原手写fetch替换IP XML输出utf8别名引起Vivado schema编码错误，统一UTF-8后目录识别/BD集成通过。实际报告路径是sim/report/*_cosim.rpt，审核脚本已修正。
- 独立master补齐原GPIO82 active-low写帧复位；匹配ARM64模块重新编译/设备树DTC编译成功。所有原子设备驱动保留。
- RG16未改变现有mode的PRIME/AddFB探针正在板端验证；当前B32仍运行。
- 清理拷贝来的旧v8/v10结果manifest到测试reference目录，避免被当成新候选证据；新发布清单仅在匹配构建完成后生成。

RG16板端探针实际PASS：pitch3840/allocated4149248/address0x3df00000，PRIME和AddFB2成功；未改变mode/current scanout，原B32运行不变。真实capture ring代码的所有权模型(cpu lease/pl read/drop-latest/drain-close)PASS，明确不是硬件测试。

## Synthesis/Display Progress
- Five vendor generated-video date revisions repaired successfully within the candidate; parallel synthesis resumed and top-level synthesis completed.
- Genuine new rectifier IP OOC synthesis reports LUT16765/FF17631/BRAM2.5/DSP47 (includes HLS coordinates/control/pack and hand B16 fetch, not merely standalone fetch); no routed whole-system resource claim yet.
- PRIME RG16 creation hardware PASS (no modeset/current scanout changed). Camera ring ownership model PASS in both test and portable formal source; Linux lease helpers split from obsolete V4L2 DMA import.
- GPIO82 reset ownership added to new media master; updated module and DTC compiled. Waiting final route/signoff before board switch.

## Packaging/Runtime Review
- Minimal board runtime no longer imports obsolete RGB888 V4L2 DMA for ABI validation; common hardware_abi and shared_lease helpers split out.
- RGB565 smoke range uses int32 to avoid signed16 overflow. Capture control readiness is polled before media setup; HWH requires actual capture_rgb565 module.
- Scanout directly configures the CRTC using the RG16 PRIME framebuffer; PYNQ is used only for DRM descriptor/event setup, avoiding its RGB888 mode API.
- Board packager prepared: requires real routed timing/primary-clock signoff and actual matching exports/modules; generates new source/runtime SHA manifests and CRC-verifiable ZIP. It has not been run/reported successful before artifacts are ready.
- Placed system provisional resources:79775 LUT(68.11%),96123FF(41.04%),120BRAM(83.33%),8URAM. Final routed numbers pending; do not substitute provisional for final.

## Matched Build / Delivery Ready
- 实际new full-system route/primary-clock signoff PASS：WNS+0.650ns/WHS+0.010ns，DRC0 errors，bitgen0Critical/0Errors；bit/HWH/DTBO/bin/LTX/XSA新导出匹配。
- 最终资源79775LUT/96123FF/120BRAM/8URAM/239DSP；LUT68.11%、BRAM83.33%、FF41.04%、DSP19.15%，CLB占用99.13%。相比B32 LUT减少20681，BRAM少9；DSP增加42，不隐瞒。CLB已占用不是等同LUT全满，未声称布局空闲很多。
- 正式board_package38文件新生成，服务器ZIP SHA0300fbb8a91c1d3dc058377005c9ccca7ddb94d5a9d8e3d4aaf870e84b9e59ea；下载SHA/CRC/双清单PASS，本地最终runtime逐文件一致。源/生成IP/报告完整交付包待归档下载。
- 已准备限定B32保留脚本；本地部署配置备份并目标指新formal board_package。实际B32停止/新board部署待完成，不把准备工作记为上板成功。

## Resume Deployment
上次sudo认证输入被自动审批服务用量限制拒绝，动作未执行。此前已正常停B32/独立保留并安装38文件565包，FPGA切换尚未确认。用户再次授权继续，先核实实际状态；另一个相关对话内容待核对。

用户提供另一对话事实摘要：已加载overlay、writerAP_CTRL1、低DDR地址合法、拓扑完整，但CSI被TREADY压住；拟修writer持续缓冲/SOF状态机。本次原run.sh部署已加载matching565，但media_setup失败upstream media graph did not bind；writer实读AP_CTRL4/尺寸和地址均0，CSI_CCR1/ISR20000。当前media control status只读ioctl等待，须先核实旧驱动/绑定状态，不把两个现场混同。读取另会话session005只见初始记录，无writer源码新改动；session006为未实施恢复评估。

## Kernel Reload Recovery
Actual kernel stack PID8379 blocked misc_open; dmesg CPU soft lockup misc_open and stale misc device suspected after overlay removal. wb565_control.remove no longer returns EBUSY before misc_deregister; matching ARM64 module rebuilt PASS. Repackaged 38 files SHA4a88428bfbf99023df98eb84507094efae4590045c39f2ca3fe53842f27643a3 downloaded/verified. User-authorized systemctl reboot accepted; immediate deployment retry found SSH connection refused while rebooting. Capture hardware acceptance and FPS still not measured.

Recovery result: after systemctl reboot SSH refused three subsequent probes over more than one minute. Cannot confirm reboot finished; board remains externally unreachable via SSH. No fresh deployment after reboot, no camera acceptance/live FPS. Next step owner power-cycle KV260, then original deploy script with revised 38-file package. Old misc lifetime defect is confirmed in source; stack/dmesg consistent with stale linked misc data but memory corruption cause is not exclusively proven. Capture writer buffering/SOF redesign has NOT yet been implemented; old bitstream unchanged by kernel-only fix.
