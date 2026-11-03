"""Package c5 for future board bring-up, without deployment or board-pass claims."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,shutil,sys,zipfile
sys.dont_write_bytecode=True
r=Path(__file__).resolve().parent
legacy=r.parent/'最终素材/submission_v24/submission_v24/board/runtime'
out=r/'runtime_candidate5';out.mkdir(exist_ok=False)
name='imx219-v24-2025-2-c5'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
load=lambda p:json.loads(p.read_text(encoding='utf-8-sig'))
assert load(r/'report_review_impl5.json')['status']=='NUMERIC_TIMING_PASS_REVIEW_PENDING'
assert load(r/'hardware_candidate5/pairing_validation.json')['status']=='PASS_XSA_BIT_HWH_PAIRING'
assert load(r/'hardware_candidate5/bin_validation.json')['status']=='PASS_BOOTGEN_AND_PAYLOAD_COMPARISON'
assert load(r/'dtbo_candidate5/validation.json')['status']=='PASS_DTC_AND_STATIC_FDT_COMPARISON'
arm=load(r/'arm_ui4b/validation.json')
assert arm['status']=='PASS_ARM64_BUILD_AND_STATIC_API' and arm['sha256']==sha(r/'arm_ui4b/libboard_ps_ui.so')
for n,h in arm['source_sha256'].items():assert sha(r/n)==h,n
origins={}
def copy(src,rel,kind):
    dst=out/rel;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst)
    origins[rel]={'source':str(src),'sha256':sha(src),'kind':kind}
for folder in ['app','drivers','ui']:
    for src in sorted((r/'r4b/src/ps'/folder).rglob('*.py')):
        copy(src,src.relative_to(r/'r4b/src/ps').as_posix(),'sealed_ps_source')
for folder in ['ui/assets','ui/licenses']:
    for src in sorted((legacy/folder).rglob('*')):
        if src.is_file():copy(src,src.relative_to(legacy).as_posix(),'unchanged_v24_asset_or_license')
for n in ['wb_frame_pool.ko','wb_rgb565_format.ko','whiteboard_registers.json']:
    copy(legacy/'hardware'/n,'hardware/'+n,'unchanged_v24_kernel_or_register_metadata')
for ext in ['.bit','.bit.bin','.hwh']:
    copy(r/'hardware_candidate5'/(name+ext),'hardware/'+name+ext,'paired_c5_hardware')
copy(r/'dtbo_candidate5'/(name+'.dtbo'),'hardware/'+name+'.dtbo','c5_firmware_name_only_overlay')
copy(r/'arm_ui4b/libboard_ps_ui.so','ui/libboard_ps_ui.so','arm64_cross_build_not_executed_on_arm')
config=load(legacy/'config/deployment.json')
config.update(name=name,firmware_basename=name,firmware_name=name+'.bit.bin',version='V24-2025.2-C5-BOARD-CANDIDATE',
              hardware_revision='C5-200MHz-TIMING-PASS-BOARD-NOT-TESTED',algorithm_baseline='v24-reviewed-2025.2-hls')
for k,ext in [('bit','.bit'),('bit_bin','.bit.bin'),('hwh','.hwh'),('dtbo','.dtbo')]:config[k]='hardware/'+name+ext
(out/'config').mkdir()
(out/'config/deployment.json').write_text(json.dumps(config,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
launcher=(legacy/'run.sh').read_text(encoding='utf-8')
assert '${1:-deploy}' in launcher
(out/'run.sh').write_text(launcher.replace('${1:-deploy}','${1:-check}'),encoding='utf-8',newline='\n')
(out/'candidate_provenance.json').write_text(json.dumps({'status':'PACKAGED_FOR_BOARD_VALIDATION_NOT_BOARD_VERIFIED',
    'created_at':datetime.datetime.now().astimezone().isoformat(),'files':origins,'timing':'impl5: WNS +0.011ns, setup/hold/pulse failures zero',
    'cdc':'Critical 0; Warning 70; review pending','kernel_target':'5.15.0-1027-xilinx-zynqmp',
    'arm_ui_execution':'NOT_RUN','board_test':'NOT_RUN','full_clean_rebuild':'r5 in progress; do not claim complete',
    'default_action':'check (may prepare PYNQ cache/temp files; not purely read-only)'},indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(out/'readme.md').write_text('''# KV260 / 2025.2 C5 联调候选

这是配套文件齐全的板级联调候选，尚未在KV260运行。原v24保留，请先保留板上可用环境和回退方式。
固件标识：imx219-v24-2025-2-c5；必须配套使用本包bit、bit.bin、hwh和dtbo，不与旧固件混用。

已完成：2025.2布线数值检查（200MHz，WNS+0.011ns，建立／保持／脉宽违例0）、
位流／XSA载荷配对、HWH一致性、Bootgen转换、设备树静态属性、PS寄存器解析、ARM64 UI交叉编译。

<span style="color:#C00000">未完成：实机画面／帧率／键鼠／翻页笔／相机与DMA／Linux驱动验证；
CDC仍有70条Warning，方法学警告待审查；11ps建立裕量较小。两个内核模块沿用原包，目标为
5.15.0-1027-xilinx-zynqmp，须与实际运行内核核对。UI库尚未在ARM执行。完整源码重建r5尚在运行。</span>

XSA单独保存于硬件导出目录；其导出工具有K26设备名称WARNING::74，平台影响未确认，
不能将文件配对通过等同于Vitis软件平台全部验证。PYNQ运行入口使用本包bit/HWH/DTBO。

上板前先对照独立KV260检查包做环境核验。本包run.sh默认check，不默认部署；
check会准备临时文件／PYNQ缓存并解析元数据，不能当作纯只读文件检查。本机未执行check/deploy。
实际切换固件须在确认内核、PYNQ、设备树及回退条件后操作，板端结果另存，不能沿用旧v24日志。

离线完整性检查可运行Python导入app/verify_manifest.py中的verify_package(runtime目录)；
仅验证文件哈希，不会配置FPGA。源码重建包与时序、CDC、导出记录另见本次交付索引。
''',encoding='utf-8')
payload=sorted(p for p in out.rglob('*') if p.is_file())
manifest={'schema':2,'sha256':{p.relative_to(out).as_posix():sha(p) for p in payload}}
(out/'config/runtime_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n',encoding='utf-8')
spec=importlib.util.spec_from_file_location('verify_runtime_candidate5',out/'app/verify_manifest.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
assert module.verify_package(out)==manifest
assert set(manifest['sha256'])=={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p!=out/'config/runtime_manifest.json'}
archive=r/'KV260_2025_2_c5_board_candidate.zip'
assert not archive.exists()
with zipfile.ZipFile(archive,'x',zipfile.ZIP_DEFLATED) as z:
    for p in sorted(out.rglob('*')):
        if not p.is_file():continue
        rel=p.relative_to(out).as_posix()
        info=zipfile.ZipInfo.from_file(p,'runtime_candidate5/'+rel)
        info.create_system=3;info.external_attr=(0o100755 if p.suffix in ('.sh','.so') else 0o100644)<<16
        info.compress_type=zipfile.ZIP_DEFLATED
        z.writestr(info,p.read_bytes())
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
    for n,h in manifest['sha256'].items():assert hashlib.sha256(z.read('runtime_candidate5/'+n)).hexdigest()==h,n
result={'status':'PASS_PACKAGE_INTEGRITY_NOT_BOARD_TESTED','archive':archive.name,'bytes':archive.stat().st_size,'sha256':sha(archive),
        'payload_files':len(payload),'manifest_schema':2,'board_test':'NOT_RUN','full_clean_rebuild':'r5 still in progress',
        'hardware_identity':name,'bit_sha256':sha(out/config['bit']),'hwh_sha256':sha(out/config['hwh']),
        'bit_bin_sha256':sha(out/config['bit_bin']),'dtbo_sha256':sha(out/config['dtbo'])}
(r/'runtime_package5.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
print(json.dumps(result))
