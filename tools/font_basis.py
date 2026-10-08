"""Isolated font validation environment; never installs into working."""
import argparse, json, shutil
from pathlib import Path
import aod_self_service as tool

ROOT=Path(__file__).resolve().parent
PROJECT=ROOT.parent
SOURCE=PROJECT/'source'
GAME=PROJECT/'font_validation'
STATE=ROOT/'state/font_validation'

def configure():
    tool.SELF=STATE
    tool.LAYOUT={'builds':'../builds/font_validation','backups':'../backups/font_validation'}
    STATE.mkdir(parents=True,exist_ok=True)
    return {'source':str(SOURCE),'game':str(GAME)}

def package(config):
    out=tool.storage('builds')/'font_basis'
    entries=[]
    for name in ('main.cs','font.module.taml'):
        data=(ROOT/'font_basis'/name).read_bytes()
        rel='mods/AoDJapaneseFont/'+name
        dest=tool.safe(out/'payload',rel)
        dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        entries.append({'path':rel,'sha256':tool.digest(data)})
    tool.savejson(out/'manifest.json',{'game':config['game'],'scope':'font_only_unverified','files':entries})
    return out

def prepare(config):
    tool.assert_closed(GAME)
    if GAME.exists():tool.fail('Validation folder already exists; refusing overwrite: '+str(GAME))
    for name in ('AoD.exe','scripts.aod','main.cs'):
        if not (SOURCE/name).is_file():tool.fail('Missing reference file: '+name)
    if (SOURCE/'mods/JapaneseDisplayTest').exists():tool.fail('Reference contains old test module')
    if (SOURCE/'mods/AoDJapaneseFont').exists():tool.fail('Reference already contains font module')
    if any(p.is_symlink() for p in SOURCE.rglob('*')):tool.fail('Reference contains links; review before copying')
    shutil.copytree(SOURCE,GAME)
    tool.install(config,package(config),confirm=False)
    font_backup=json.loads((STATE/'latest_backup.json').read_text(encoding='utf-8'))
    tool.savejson(STATE/'font_backup.json',font_backup)
    print('Font-only candidate installed in validation copy. Not game-tested.')
    print('Next: font_basis.py build-text (non-dialogue drafts only).')

def main():
    p=argparse.ArgumentParser();p.add_argument('action',choices=('prepare','build-text','install-text','restore-text','restore-font'));a=p.parse_args()
    config=configure()
    if a.action=='prepare':prepare(config)
    elif a.action=='build-text':
        if not (GAME/'mods/AoDJapaneseFont/font.module.taml').is_file():tool.fail('Prepare validation first')
        tool.INVENTORY=PROJECT/'translations'
        tool.build(config,tool.INVENTORY,include_drafts=True)
    elif a.action=='install-text':
        state=json.loads((STATE/'latest_build.json').read_text(encoding='utf-8'))
        if state.get('status')!='READY':tool.fail('Build not ready')
        tool.install(config,Path(state['build']))
    else:
        name='font_backup.json' if a.action=='restore-font' else 'latest_backup.json'
        backup=Path(json.loads((STATE/name).read_text(encoding='utf-8'))['backup'])
        if a.action=='restore-text' and (backup/'restore.json').is_file():
            manifest=json.loads((backup/'restore.json').read_text(encoding='utf-8'))
            if all(r['path'].startswith('mods/AoDJapaneseFont/') for r in manifest['files']):tool.fail('No text installation to restore; use restore-font')
        tool.rollback(backup)
        print('Unmanaged engine cache files are retained; module definition removal disables this module.')

if __name__=='__main__':
    try:main()
    except Exception as e:print('STOP:',e);raise SystemExit(1)
