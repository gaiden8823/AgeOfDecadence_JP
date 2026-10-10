from pathlib import Path
import hashlib,json,shutil,datetime,sys,zipfile,subprocess,tempfile,os
sys.stdout.reconfigure(encoding='utf-8')
R=Path('C:/GameModding/AgeOfDecadence_JP');G=R/'addon_validation';S=R/'source'
TOOL_DIR=Path(__file__).resolve().parent
O=Path.cwd()/'outputs/mod_release';stamp=datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
P=O/('AoDJP_candidate_'+stamp);P.mkdir(parents=True,exist_ok=False)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
extensions={'.cs','.dso','.xml','.mis','.png','.dds','.taml'}
files=[];mods={'AoDJapaneseFont','AoDJPAddonProbe','AoDJPRouteFix'}
for p in sorted(G.rglob('*')):
 if not p.is_file() or p.suffix.lower() not in extensions:continue
 rel=p.relative_to(G);parts=rel.parts
 if parts[0]=='mods':
  if len(parts)<2 or parts[1] not in mods:continue
 elif parts[0] not in {'art','scripts','levels'} and rel.as_posix()!='main.cs':continue
 original=S/rel
 if original.exists() and digest(original)==digest(p):continue
 q=P/'payload'/rel;q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
 files.append({'path':rel.as_posix(),'sha256':digest(p),'baseline_sha256':digest(original) if original.exists() else None,'bytes':p.stat().st_size})
archives=[{'path':p.relative_to(S).as_posix(),'sha256':digest(p)} for p in S.rglob('*.aod')]
manifest={'version':stamp,'scope':'local_distribution_candidate','mode':'hybrid','files':files,'baseline_archives':archives,'dependency':'Windows BIZ UDPMincho Medium font; Python 3.10+','public_release':False}
(P/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
shutil.copy2(TOOL_DIR/'install_mod.py',P/'install_mod.py')
shutil.copy2(TOOL_DIR/'README_ja.md',P/'導入・更新手順.md')
# Disposable minimal installation baseline, not the user's game.
test=P/'installation_test';test.mkdir();(test/'AoD.exe').touch()
for r in archives+files:
 original=S/r['path']
 if original.exists():
  q=test/r['path'];q.parent.mkdir(parents=True,exist_ok=True)
  if q.exists():continue
  if original.suffix=='.aod':os.link(original,q)
  else:shutil.copy2(original,q)
before={p.relative_to(test).as_posix():digest(p) for p in test.rglob('*') if p.is_file()}
def run(*args):
 result=subprocess.run([sys.executable,str(P/'install_mod.py'),*args],capture_output=True,text=True,encoding='utf-8');assert result.returncode==0,result.stdout+result.stderr;print(result.stdout.strip())
run('check',str(test));run('install',str(test))
assert all(digest(test/r['path'])==r['sha256'] for r in files)
backup=next((test/'.aodjp_backups').iterdir());run('restore',str(test),'--backup',str(backup))
after={p.relative_to(test).as_posix():digest(p) for p in test.rglob('*') if p.is_file() and '.aodjp_backups' not in p.parts}
assert before==after
report={'files':len(files),'payload_bytes':sum(r['bytes'] for r in files),'check_install_restore':'passed','restored_baseline_identical':True,'game_unchanged':True,'candidate':str(P)}
(O/('verification_'+stamp+'.json')).write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
archive=O/(P.name+'.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
 for p in P.rglob('*'):
  if p.is_file() and 'installation_test' not in p.relative_to(P).parts:z.write(p,(Path(P.name)/p.relative_to(P)).as_posix())
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps(report,ensure_ascii=False,indent=2));print('ZIP',archive)
