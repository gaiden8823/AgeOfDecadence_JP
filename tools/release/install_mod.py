"""Install an exact-baseline local MOD candidate with transactional backups."""
from pathlib import Path
import argparse,json,hashlib,shutil,datetime,subprocess,csv,io,os
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def safe(root,rel):
 p=(root/rel).resolve()
 if not p.is_relative_to(root.resolve()) or p==root.resolve():raise ValueError('Unsafe path: '+rel)
 return p
def main():
 parser=argparse.ArgumentParser();parser.add_argument('mode',choices=['check','install','restore']);parser.add_argument('game');parser.add_argument('--backup')
 args=parser.parse_args();game=Path(args.game).resolve();base=Path(__file__).resolve().parent
 assert (game/'AoD.exe').is_file(),'AoD.exe not found'
 if args.mode!='check' and os.name=='nt':
  result=subprocess.run(['tasklist','/FO','CSV','/NH'],capture_output=True,text=True,check=True)
  running={row[0].lower() for row in csv.reader(io.StringIO(result.stdout)) if row}
  assert not running.intersection({'aod.exe','aod64.exe'}),'Close the game before install/restore'
 if args.mode=='restore':
  assert args.backup,'Specify --backup'
  backup=Path(args.backup).resolve();assert backup.is_relative_to(game/'.aodjp_backups')
  state=json.loads((backup/'restore.json').read_text(encoding='utf-8'));assert state['game']==str(game)
  for r in state['files']:
   p=safe(game,r['path']);assert p.exists() and digest(p)==r['installed'],'Modified installed file: '+r['path']
   if r['existed']:assert digest(safe(backup/'original',r['path']))==r['original']
  for r in reversed(state['files']):
   p=safe(game,r['path'])
   if r['existed']:shutil.copy2(safe(backup/'original',r['path']),p)
   else:p.unlink()
  print('Restored. Backup retained:',backup);return
 manifest=json.loads((base/'manifest.json').read_text(encoding='utf-8'))
 for r in manifest['baseline_archives']:
  p=safe(game,r['path']);assert p.is_file() and digest(p)==r['sha256'],'Different game version: '+r['path']
 for r in manifest['files']:
  p=safe(game,r['path']);src=safe(base/'payload',r['path']);assert digest(src)==r['sha256'],'Package changed'
  if p.exists():assert r['baseline_sha256'] is not None and digest(p)==r['baseline_sha256'],'Existing MOD/conflict: '+r['path']
  elif r['baseline_sha256'] is not None:raise ValueError('Missing original: '+r['path'])
 print('Package and baseline verified:',len(manifest['files']),'files')
 if args.mode=='check':return
 backup=game/'.aodjp_backups'/datetime.datetime.now().strftime('%Y%m%d_%H%M%S_%f');backup.mkdir(parents=True)
 records=[]
 for r in manifest['files']:
  p=safe(game,r['path']);record={'path':r['path'],'installed':r['sha256'],'existed':p.exists(),'original':digest(p) if p.exists() else None}
  if p.exists():q=safe(backup/'original',r['path']);q.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(p,q)
  records.append(record)
 (backup/'restore.json').write_text(json.dumps({'game':str(game),'files':records},ensure_ascii=False,indent=2),encoding='utf-8')
 completed=[]
 try:
  for r in records:
   p=safe(game,r['path']);p.parent.mkdir(parents=True,exist_ok=True);completed.append(r);shutil.copy2(safe(base/'payload',r['path']),p)
 except Exception:
  for r in reversed(completed):
   p=safe(game,r['path'])
   if r['existed']:shutil.copy2(safe(backup/'original',r['path']),p)
   elif p.exists():p.unlink()
  raise
 print('Installed. Restore backup:',backup)
if __name__=='__main__':main()
