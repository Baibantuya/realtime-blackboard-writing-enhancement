"""Create review copies and verify recorded identities. Does not run project tests."""
from pathlib import Path
import json, hashlib
from prepare_sources import ROOT, OUT, clean, write_new, digest

def main():
    selected = {}
    def add(src, dst): selected[src]=dst
    ui='evidence/member_c/light_overlay_linux_20261018/'
    for n in ['validation_receipt.json','ctest.log','linux_display_selftest.log','font_medium_resources.json','font_regular_1080p_resources.json','windows_regression/idle-assert-before-fix.log','windows_regression/ctest.log','windows_regression/preview.log','x11_14/interaction_receipt.json','x11_14/main.png','x11_14/startup-collapsed.png','history/ctest-1792256470684824932.log']:
        add(ui+n,'evidence/ui_linux/'+n)
    add('ui/lvgl/README-linux.md','sources/user_ui/linux_readme.md')
    add('ui/lvgl/tools/verify_linux.py','evidence/ui_linux/verify_linux.py')
    add('ui/lvgl/tools/verify_x11_interaction.py','evidence/ui_linux/verify_x11_interaction.py')
    add('ui/camera_guidance/README.md','sources/user_ui/guidance_readme.md')
    for n in ['assets_20261018_v5/manifest.json','preview_20261018_v5/manifest.json','preview_20261018_v5/guidance_up_then_clockwise.png']:
        add('ui/camera_guidance/'+n,'evidence/ui_guidance/'+n)
    for variant,dst in [('v16_ps_pipeline_ui_20261018','ui_pipeline'),('v16_ps_ui_2hz_20261018','ui_2hz')]:
        b='model_integration/'+variant+'/'
        add(b+'evidence/integration_receipt.json','evidence/'+dst+'/integration_receipt.json')
        if dst=='ui_pipeline':
            add(b+'PIPELINE_UI_README.md','sources/user_ui/pipeline_readme.md')
            for n in ['regression_03/validation.json','regression_03/unittest.log','window_grouped_01/interaction.json','window_grouped_01/expanded.png']:
                add(b+'evidence/'+n,'evidence/'+dst+'/'+n)
        else:
            add(b+'UI_2HZ_README.md','sources/user_ui/refresh_2hz_readme.md')
            for n in ['wsl_regression_01/validation.json','wsl_regression_01/unittest.log','wsl_window_01/replay.json']:
                add(b+'evidence/'+n,'evidence/'+dst+'/'+n)
    for name,dst in [('模型物体漏检与ONNX一致性分析_20261017.md','detection_analysis.md'),('三条模型优化路线试验记录_20261019.md','three_routes.md'),('手形RGB565三种子重复实验记录_20261019.md','rgb565_replicates.md'),('手势连续回放与关键点对照记录_20261019.md','sequence_boundary.md')]:
        add('docs/'+name,'sources/user_models/'+dst)
    for n in ['objects/summary.json','objects/cached_followup.json','export/details.json','export/optimization_replay.json','original_artifact_integrity.json','local_receipt.json']:
        add('evidence/member_c/hand_object_analysis_20261017/'+n,'evidence/model_detection/'+n)
    for n in ['server_results/three_seed_summary.json','server_results/replication_config.json','local_verification.json','server_results/phone66_multiseed_native_cpu.json']:
        add('evidence/member_c/gesture_rgb565_replicates_20261019_01/'+n,'evidence/model_rgb565/'+n)
    add('docs/V22背景核验记录_20261022.json','evidence/team_v22/local_prior_audit.json')
    add('docs/V22架构与背景更新_20261022.md','sources/background/v22_review.md')
    add('docs/V23现场进度与模型部署边界更新_20261022.md','sources/background/v23_scope.md')
    inventory=[]
    for src,dst in selected.items():
        p=ROOT/src
        if not p.is_file():inventory.append({'source':src,'copy':dst,'status':'missing'});continue
        b=p.read_bytes(); redactions=0; encoding='binary'
        out=b
        if p.suffix.lower() in ['.md','.json','.py','.log','.txt']:
            encoding='utf-8-sig'
            try: s=b.decode(encoding)
            except UnicodeDecodeError:
                encoding='utf-16' if b.startswith((b'\xff\xfe',b'\xfe\xff')) else 'gb18030'
                s=b.decode(encoding)
            s,redactions=clean(s);out=s.encode('utf-8')
        write_new(OUT/dst,out)
        inventory.append({'source':src,'copy':dst,'status':'read_and_copied','bytes':len(b),'source_sha256':digest(b),'copy_sha256':digest(out),'redactions':redactions,'source_encoding':encoding})
    checks=[]
    for receipt,base,label in [(ui+'validation_receipt.json','ui/lvgl','ui_linux'),('model_integration/v16_ps_pipeline_ui_20261018/evidence/regression_03/validation.json','model_integration/v16_ps_pipeline_ui_20261018','ui_pipeline')]:
        data=json.loads((ROOT/receipt).read_text(encoding='utf-8-sig'))
        items=[]
        for name,expected in data['source_sha256'].items():
            p=ROOT/base/name
            actual=digest(p.read_bytes()) if p.is_file() else None
            items.append({'file':name,'expected':expected,'actual':actual,'match':expected==actual})
        checks.append({'label':label,'receipt':receipt,'checked':len(items),'matched':sum(x['match'] for x in items),'items':items})
    j=json.loads((ROOT/ui/'x11_14/interaction_receipt.json').read_text(encoding='utf-8'))
    checks.append({'label':'ui_final_receipts','checks':len(j['checks']),'binary_hash_equal':j['binary_sha256']==json.loads((ROOT/ui/'validation_receipt.json').read_text())['linux_binary_sha256'],'scope':j['scope']})
    result={'review_date':'2026-10-22','scope':'Local bytes, JSON and historical receipt checks only; no retraining, UI execution, deployment or hardware tests','files':inventory,'checks':checks}
    write_new(OUT/'evidence_inventory.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
    print(json.dumps({'copied':sum(x['status']=='read_and_copied' for x in inventory),'missing':[x['source'] for x in inventory if x['status']=='missing'],'checks':[{k:v for k,v in c.items() if k!='items'} for c in checks]},ensure_ascii=False))

if __name__=='__main__':main()
