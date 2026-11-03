"""Copy selected existing UI history evidence; never execute historical commands."""
from pathlib import Path
import hashlib,json,re,struct

OUT=Path(__file__).resolve().parents[1]
PROJECT=OUT.parents[1]
def digest(b): return hashlib.sha256(b).hexdigest()
def load(p): return json.loads(p.read_text('utf-8-sig'))
def save_new(p,b):
    p.parent.mkdir(parents=True,exist_ok=True)
    if p.exists() and p.read_bytes()!=b: raise RuntimeError('Refuse overwrite: '+str(p))
    if not p.exists(): p.write_bytes(b)

selection=[]
def add(src,dst,case,reason):selection.append((Path(src),dst,case,reason))
base=PROJECT/'evidence/member_c/light_overlay_linux_20261018'
for run,files in {
 'x11_04':['main.png','initialize.png','recovery.png','disconnected.png','interaction_receipt.json'],
 'x11_11':['main.png','startup-collapsed.png','initialize.png','recovery.png','interaction_receipt.json'],
 'x11_12':['main.png','auto-collapsed.png','interaction_receipt.json'],
 'x11_13':['main.png','interaction_receipt.json'],
 'x11_14':['initialize.png','recovery.png']}.items():
 for f in files:add(base/run/f,'evidence/ui_history/linux/'+run+'/'+f,'U01','Historical renderer capture or interaction receipt')
add(base/'export_sha256.json','evidence/ui_history/linux/export_sha256.json','U01','Existing export manifest; authenticates selected archived bytes, not independent signature')
provenance=load(OUT/'evidence/ui_history/conversation_tools_and_images.json')
for a in provenance['attachments']:
 name='wording_question.png' if a['message_id']=='01a14ae0-bb09-7fd3-93be-7ca1276915fd' else 'recovery_color_feedback.png'
 add(a['path'],'evidence/ui_history/attachments/'+name,'U01','Exact localImage path from user message '+a['message_id'])

for n,suffix in [(1,''),(2,'_v2'),(3,'_v3'),(4,'_v4')]:
 root=PROJECT/'ui/camera_guidance'
 for f in ['manifest.json','validation.json','guidance_up_then_clockwise.png']:
  add(root/('preview_20261018'+suffix)/f,f'evidence/ui_history/guidance/v{n}/'+f,'U02','Linked intermediate preview and existing validation')
 add(root/('assets_20261018'+suffix)/'manifest.json',f'evidence/ui_history/guidance/v{n}/assets_manifest.json','U02','Versioned typography and asset hashes')

full=PROJECT/'model_integration/v16_ps_full_ui_20261018'
for f in ['evidence/full_regression_01/validation.json','evidence/full_regression_02/validation.json','evidence/full_regression_02/unittest.log','evidence/full_window_01/expanded.png','evidence/full_window_01/interaction.json','FULL_UI_README.md']:
 add(full/f,'evidence/ui_history/full_ui/'+f,'U03','Intermediate single-frame integration; distinct from final pipeline')

records=[]
for src,dst,case,reason in selection:
 rec={'case':case,'source':str(src),'copy':dst,'reason':reason}
 if not src.is_file():rec['status']='missing';records.append(rec);continue
 b=src.read_bytes();save_new(OUT/dst,b)
 rec.update(status='read_and_copied',bytes=len(b),source_sha256=digest(b),copy_sha256=digest(b),transformation='none; byte-for-byte copy')
 if b.startswith(b'\x89PNG\r\n\x1a\n'):rec['image_size']=list(struct.unpack('>II',b[16:24]))
 records.append(rec)

# Link actual visible messages to referenced files without changing message text.
message_links=[]
for case in ['user_01_ui_linux','user_02_ui_guidance','user_03_ui_pipeline']:
 for m in load(OUT/'report/ai_session'/case/'messages.json'):
  for raw in re.findall(r'\]\(([^)]+)\)',m['content']):
   if not raw.startswith('D:/'):continue
   p=Path(re.sub(r':\d+$','',raw));b=p.read_bytes() if p.is_file() and p.suffix.lower() in ['.png','.json','.md'] else None
   message_links.append({'case':case,'organizer_id':m['organizer_id'],'message_id':m['message_id'],'turn_id':m['turn_id'],'link':raw,'exists':p.is_file(),'sha256_if_read':digest(b) if b is not None else None})

checks=[]
historical=load(base/'export_sha256.json')
for rec in records:
 try:rel=Path(rec['source']).relative_to(base).as_posix()
 except ValueError:continue
 if rel in historical:
  checks.append({'check':'linux_historical_export_hash','source':rel,'match':rec.get('source_sha256')==historical[rel]})

guidance=[]
for n,suffix in [(1,''),(2,'_v2'),(3,'_v3'),(4,'_v4'),(5,'_v5')]:
 root=PROJECT/'ui/camera_guidance'
 am=load(root/('assets_20261018'+suffix)/'manifest.json');pm=load(root/('preview_20261018'+suffix)/'manifest.json')
 pairs=[('asset',root/('assets_20261018'+suffix)/name,h) for name,h in am['sha256'].items()]
 pairs += [('preview',root/('preview_20261018'+suffix)/p['name'],p['sha256']) for p in pm['pages']]
 mismatch=[str(p.relative_to(PROJECT)) for _,p,h in pairs if not p.is_file() or digest(p.read_bytes())!=h]
 center=[]
 for page,lines in am['text_layout'].items():
  if not page.startswith('guidance'):continue
  for line in lines:
   if line['role'] not in ['action','body','next'] or line.get('align')!='center':continue
   bounds=line['bounds'];center.append(abs((bounds[0]+bounds[2])/2-1696))
 guidance.append({'version':n,'checked':len(pairs),'matched':len(pairs)-len(mismatch),'mismatches':mismatch,
  'sidebar_alignment':am.get('sidebar_alignment'),'selected_centered_rows':len(center),'max_recorded_bounds_offset_px':max(center) if center else None,
  'bounds_warning':'v1-v3 layout bounds and v4-v5 visible glyph bounds are different metrics; arithmetic on manifest, not pixel rerender'})

result={'review_date':'2026-10-22','scope':'Scoped local reads/copies, existing message links and manifest arithmetic only. No rendering, UI execution, training or board tests.',
 'files':records,'message_links':message_links,'historical_hash_checks':checks,'guidance_version_checks':guidance,
 'attachment_identity_limit':'Recovered from exact localImage paths; hashes computed now. Historical message does not carry an independent image digest.',
 'intermediate_binary_limit':'x11_04/11/12/13 receipts lack binary hashes; link via message/command/run directory and export manifest, not final binary identity.'}
save_new(OUT/'ui_history_inventory.json',(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
print(json.dumps({'files':len(records),'copied':sum(x['status']=='read_and_copied' for x in records),'missing':[x['source'] for x in records if x['status']=='missing'],
 'historical_hashes':len(checks),'historical_matches':sum(x['match'] for x in checks),'guidance':guidance},ensure_ascii=False))
