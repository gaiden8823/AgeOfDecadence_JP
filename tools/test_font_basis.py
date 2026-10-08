import json, shutil, tempfile, unittest
from pathlib import Path
from unittest.mock import patch
import font_basis as basis

class FontBasisTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);self.source=self.root/'source';self.game=self.root/'font_validation'
        self.source.mkdir();self.tools=self.root/'tools';self.tools.mkdir()
        shutil.copytree(basis.ROOT/'font_basis',self.tools/'font_basis')
        for name in ('AoD.exe','scripts.aod','main.cs'):(self.source/name).write_bytes(b'original')
        for attr,value in [('ROOT',self.tools),('SOURCE',self.source),('GAME',self.game),('STATE',self.tools/'state')]:
            p=patch.object(basis,attr,value);p.start();self.addCleanup(p.stop)
        p=patch.object(basis.tool,'SELF',self.tools/'state');p.start();self.addCleanup(p.stop)
        p=patch.object(basis.tool,'LAYOUT',{});p.start();self.addCleanup(p.stop)
        p=patch.object(basis.tool,'assert_closed');p.start();self.addCleanup(p.stop)
        (self.tools/'state').mkdir()
        self.config={'source':str(self.source),'game':str(self.game)}
    def test_prepare_and_restore_without_touching_source(self):
        basis.prepare(self.config)
        module=self.game/'mods/AoDJapaneseFont'
        self.assertTrue((module/'font.module.taml').exists())
        state=json.loads((basis.STATE/'font_backup.json').read_text())
        (module/'main.cs.dso').write_bytes(b'engine cache')
        basis.tool.rollback(Path(state['backup']))
        self.assertFalse((module/'font.module.taml').exists())
        self.assertTrue((module/'main.cs.dso').exists())
        self.assertEqual((self.source/'main.cs').read_bytes(),b'original')
    def test_refuse_existing_validation_folder(self):
        self.game.mkdir()
        with self.assertRaisesRegex(ValueError,'already exists'):basis.prepare(self.config)
    def test_refuse_old_test_module(self):
        (self.source/'mods/JapaneseDisplayTest').mkdir(parents=True)
        with self.assertRaisesRegex(ValueError,'old test'):basis.prepare(self.config)
        self.assertFalse(self.game.exists())
    def test_refuse_restore_if_user_changed_module(self):
        basis.prepare(self.config)
        (self.game/'mods/AoDJapaneseFont/main.cs').write_text('user change')
        state=json.loads((basis.STATE/'font_backup.json').read_text())
        with self.assertRaisesRegex(ValueError,'changed after install'):basis.tool.rollback(Path(state['backup']))
        self.assertEqual((self.game/'mods/AoDJapaneseFont/main.cs').read_text(),'user change')
    def test_package_has_no_game_assets_or_fixed_translation(self):
        out=basis.package(self.config)
        manifest=json.loads((out/'manifest.json').read_text())
        self.assertEqual(len(manifest['files']),2)
        script=(out/'payload/mods/AoDJapaneseFont/main.cs').read_text()
        for forbidden in ('setText(','.text0 =','.text1 =','setBitmap(','addDialogueFolder(','schedule('):
            self.assertNotIn(forbidden,script)

if __name__=='__main__':unittest.main()
