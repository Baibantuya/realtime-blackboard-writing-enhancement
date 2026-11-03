# AI Session: 2026-10-12-003-rectifier-rgb565-assessment
- Date: 2026-10-12
- Operator: Project owner
- AI product/model: Codex / GPT-6
- Participants: Project owner, Codex (single agent)
- Objective: 评估RGB565及A6+B32合并，只优化校正核。
- Status: In progress
- Report candidate: no
## Context Read
AGENTS、政策、当前状态、决策、索引、最近B32记录、Git；核对B32源/相机链与资源报告。
## Task and Constraints
仅评估，不修改/构建/上板；当前B32保留运行。
## Contributions
待补齐。
## Decisions and Adoption
待补齐。
## Commands and Tools
本地源码/报告与官方传感器驱动文档检索。
## Validation and Evidence
未执行新硬件/综合/性能测试。
## Errors and Corrections
待补齐。
## Files Changed
本记录。
## Remaining Work
格式边界、缓存/并发可行性与资源/性能判断。
## Handoff Notes
B32校正约70ms，LUT85.77%/CLB99.80%/BRAM89.58%。

## Assessment Results
- 本地configure_restore_capture明确sensor S*8/RAW8和video RGB3；DTS CSI0x2a/demosaic/gamma/frmbuf RGB888。官方Linux源imx219_mbus_formats仅BayerRAW8/10：https://raw.githubusercontent.com/torvalds/linux/master/drivers/media/i2c/imx219.c。传感器直接RGB565不可按提出的寄存器方式实现。
- RGB565需ISP后打包、PL/DMA DDR输出格式支持；当前frmbuf vid-formats无RGB565，必须改writer或合适支持的实现及Linux接口，不可仅改DTS/寄存器。PS稀疏AE/定位、共享池size/stride、校正源地址也适配。建议565输入/RGB888输出保持恢复/量化，不声称全链均2字节。
- HD帧RGB8886220800B→RGB5654147200B，减少1/3。32bit载两个相邻源像素，无跨word；透视索引未必相邻，不能宣称两输出像素/周期。当前RTL每像素3byte使idx%4=2/3跨word，565可消除第二字查询/等待/拼接。
- 量化误差R/B5bit约8级步长，G6bit约4级；展开无法恢复低位，弱字/邻域/色度可能变化，精度验收需与565量化基准对比，非原888逐字节。
- A6 pending6/window8/line16/sets4/ways1；B32 pending4/window4/line32/sets4/ways2。共享参数化RTL；混合pending6/window8/line32/sets4/ways2逻辑可行，资源/时序未验证，不能相乘加速。
- 当前cache data寄存器多路器/全line提交，token wait0/wait1广播。BRAM同步读bank需重写，不是加属性保证；可用BRAM预算仅15 tiles，整体LUT85.77%/CLB99.80%。565同32word line覆盖64pixel，888约42.7pixel；需比较16/32word overfetch。输入565/输出888仅减少源端带宽，校正坐标和输出888流量不变。
- 来源验证：wb_rectify_fetch_v10.sv positions_index*3、phase0/word0/word1、WINDOW=min(PREFETCH_DISTANCE,TOKEN_DEPTH)与cache arrays；B32/A6实际性能/资源沿用session002。无测试/源码修改/上板/新综合，方案未采用为实现。
## Final Contributions / Adoption
AI完成格式事实纠正、接口边界/位宽收益/资源限制和组合路线评估；建议作为proposal(D-089)，未实施。
## Files Changed (Final)
本记录、DECISIONS、PROJECT_STATE、INDEX。代码与当前B32运行不变。
## Remaining Work (Final)
用户选择输入565/输出888或全链迁移范围；后续接口与writer实现验证、合并参数A/B与资源/时序实测。精确性能不承诺。
## Status (Final)
Completed feasibility assessment; no implementation.

## Follow-up: Downstream 16-bit Pixel Path
用户问565后下游b16与多IP优化；按b16指16bit像素解释。开始评估，非实施授权。

评估结论：若b16为16bit像素格式，校正/恢复/量化可统一565存储、缓存和像素流；DDR仍保留32/64bit按2/4像素打包，不能将所有计算/坐标/累加/state机械降16bit。恢复源码input/output/background/previous均packedRGB888，多读写路径可减1/3像素流量；mask/TTL/pixel_quiet不同位宽不变。恢复局部亮度行缓存本来uint16，不承诺再降1/3。量化7x7原RGB数据缓存可用16bit存565、运算时展开，但亮度/和保留足够位宽，黑/彩色弱字需重新参考验收。最终扫描当前RG24/5888pitch，如果输出565须DRM RGB565 format支持/驱动匹配/stride等同步验证；可先在最终量化输出888保持现有显示。当前不存在实施或新性能证据。
