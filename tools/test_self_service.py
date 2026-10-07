import csv, hashlib, json, tempfile, unittest
from types import SimpleNamespace
from pathlib import Path
from unittest.mock import patch
import aod_self_service as tool

class ToolTests(unittest.TestCase):
    def setUp(self):
        layout_patch=patch.object(tool,'LAYOUT',{})
        layout_patch.start();self.addCleanup(layout_patch.stop)
        self.temp=tempfile.TemporaryDirectory();self.root=Path(self.temp.name)
        self.base=[{'id':'a','source_raw':'Hello <value>','source_hash':hashlib.sha256(b'Hello <value>').hexdigest(),'target_ja':'こんにちは<value>'}]
    def tearDown(self):self.temp.cleanup()
    def test_blank_preserves_translation(self):
        self.assertEqual(tool.merge(self.base,[dict(self.base[0],target_ja='')],'source_raw'),self.base)
    def test_holds_are_sticky_and_never_selected(self):
        held=dict(self.base[0],status='technical_review',target_ja='タグ不一致',target_draft='候補')
        merged=tool.merge([held],[dict(self.base[0],status='approved')],'source_raw')
        for drafts in [False,True]:
            selected,counts=tool.select_translations(merged,drafts)
            self.assertEqual(selected,[]);self.assertEqual(counts['skipped_hold_rows'],1)
        added=tool.merge(self.base,[dict(self.base[0],status='hold')],'source_raw')
        self.assertTrue(tool.blocked(added[0]))
    def test_drafts_opt_in_priority_and_token_validation(self):
        draft=dict(self.base[0],target_ja='',target_draft='下訳<value>',status='draft')
        self.assertEqual(tool.select_translations([draft])[0],[])
        selected,counts=tool.select_translations([draft],True)
        self.assertEqual(selected[0]['target_ja'],'下訳<value>');self.assertEqual(counts['draft_rows_used'],1)
        self.assertEqual(draft['target_ja'],'')
        self.assertEqual(tool.select_translations([dict(draft,target_ja='確定<value>')],True)[0][0]['target_ja'],'確定<value>')
        with self.assertRaises(ValueError):tool.select_translations([dict(draft,target_draft='タグなし')],True)
        self.assertEqual(tool.select_translations([dict(draft,status='pending_translation')],True)[0],[])
    def test_torque_numbered_token_does_not_consume_next_word(self):
        self.assertEqual(tool.tokens('<value>% increase in damage<spop>'),['<value>','<spop>'])
        self.assertEqual(tool.tokens('Wait %1 seconds.'),['%1'])
        tool.validate_target('Wait %1 seconds.','あと%1秒お待ちください。','numbered')
        self.assertEqual(tool.tokens('%1$s'),['%1$s'])
    def test_render_font_override_preserves_size_and_other_tags(self):
        text='<spush><font:Myriad Pro Bold:16><color:FFFFFF>説明<spop>'
        self.assertEqual(tool.render_fonts(text),'<spush><font:BIZ UDPMincho Medium:16><color:FFFFFF>説明<spop>')
        self.assertEqual(tool.render_fonts('THC:94%'),'THC:94%')
    def test_layout_override_is_instruction_specific(self):
        instructions=[]
        def emit(op,identifier='',text=None):
            instructions.append(SimpleNamespace(ip=len(instructions)*3,op=op,identifier=identifier,text=text))
        emit('LOADIMMED_IDENT','fbTextCtrl');emit('PUSH');emit('LOADIMMED_IDENT','CS_Str_effect');emit('PUSH');emit('CREATE_OBJECT')
        for key,value in [('position','233 127'),('extent','63 37')]:
            emit('LOADIMMED_STR',text=value);emit('ADVANCE_STR');emit('SETCUROBJECT_NEW');emit('SETCURFIELD',key)
        changes=tool.layout_overrides(SimpleNamespace(instructions=instructions),'CharScreen_1080.english.gui.dso')
        self.assertEqual(set(changes.values()),{'186 127','158 37'})
        self.assertEqual(tool.layout_overrides(SimpleNamespace(instructions=instructions),'Other.gui.dso'),{})
    def test_duplicate_unknown_source_and_tag_errors(self):
        b=self.base[0]
        for incoming in [[b,b],[dict(b,id='unknown')],[dict(b,source_raw='Changed')],[dict(b,target_ja='タグなし')]]:
            with self.assertRaises(ValueError):tool.merge(self.base,incoming,'source_raw')
    def test_newline_variants(self):
        r={'id':'a','source_raw':'line1\nline2','source_hash':hashlib.sha256(b'line1\r\nline2').hexdigest(),'target_ja':''}
        self.assertEqual(tool.merge([r],[],'source_raw'),[r])
    def test_source_path_escape(self):
        for p in ['../bad','C:/bad','/bad','folder/../../bad']:
            with self.assertRaises(ValueError):tool.safe(self.root,p)
    def test_nested_script_preserves_code(self):
        text='sayPhrase("Hello"); next();'
        entries=[{'locator':'text/char:10','source_raw':'Hello','target_ja':'こんにちは'}]
        self.assertEqual(tool.rewrite_script(text,entries),'sayPhrase("こんにちは"); next();')
    def test_xml_preserves_layout(self):
        blob=b'<root>\r\n<item><Name>Hello</Name></item>\r\n</root>'
        result=tool.patch_xml(blob,[{'id':'a','locator':'xml_element:2:Name','source_raw':'Hello','target_ja':'こんにちは'}])
        self.assertEqual(result,blob.replace(b'Hello','こんにちは'.encode()))
    def test_csv_input(self):
        p=self.root/'input.csv';tool.writecsv(p,self.base,list(self.base[0]))
        self.assertEqual(tool.read_table(p,{'id','source_raw','target_ja'}),self.base)
    def test_xlsx_input_and_formula_rejection(self):
        # Temporary test fixture only, not a delivered spreadsheet.
        import openpyxl
        p=self.root/'input.xlsx';w=openpyxl.Workbook();s=w.active
        s.append(['id','source_raw','target_ja']);s.append(['a','Hello <value>','こんにちは<value>']);w.save(p);w.close()
        self.assertEqual(tool.read_table(p,{'id','source_raw','target_ja'})[0]['target_ja'],'こんにちは<value>')
        w=openpyxl.load_workbook(p);w.active['C2']='=1+1';w.save(p);w.close()
        with self.assertRaises(ValueError):tool.read_table(p,{'id','source_raw','target_ja'})
    def test_install_restore_and_post_install_edit_guard(self):
        game=self.root/'game';game.mkdir();(game/'AoD.exe').write_bytes(b'test');(game/'scripts.aod').write_bytes(b'test')
        source=self.root/'source';source.mkdir();out=self.root/'build';payload=out/'payload';payload.mkdir(parents=True)
        rel='scripts/a.english.cs.dso';dest=tool.safe(game,rel);dest.parent.mkdir(parents=True);dest.write_bytes(b'original')
        companion=dest.with_suffix('');companion.write_bytes(b'source original')
        new=tool.safe(payload,rel);new.parent.mkdir(parents=True);new.write_bytes(b'new')
        add='scripts/new.cs';tool.safe(payload,add).write_bytes(b'new file')
        tool.savejson(out/'manifest.json',{'files':[{'path':rel,'sha256':tool.digest(b'new')},{'path':add,'sha256':tool.digest(b'new file')}]})
        with patch.object(tool,'SELF',self.root/'tool'),patch.object(tool,'assert_closed'):
            tool.install({'game':str(game),'source':str(source)},out,confirm=False)
            backup=Path(json.loads((tool.SELF/'latest_backup.json').read_text())['backup'])
            self.assertEqual(dest.read_bytes(),b'new');self.assertFalse(companion.exists())
            dest.write_bytes(b'external edit')
            with self.assertRaises(ValueError):tool.rollback(backup)
            dest.write_bytes(b'new');tool.rollback(backup)
            self.assertEqual(dest.read_bytes(),b'original');self.assertEqual(companion.read_bytes(),b'source original');self.assertFalse(tool.safe(game,add).exists())
    def test_tampered_package_does_not_write(self):
        game=self.root/'game';game.mkdir();(game/'AoD.exe').write_bytes(b'test');(game/'scripts.aod').write_bytes(b'test')
        source=self.root/'source';source.mkdir();out=self.root/'build';out.mkdir()
        tool.safe(out/'payload','scripts/a.cs').parent.mkdir(parents=True);tool.safe(out/'payload','scripts/a.cs').write_bytes(b'tampered')
        tool.savejson(out/'manifest.json',{'files':[{'path':'scripts/a.cs','sha256':tool.digest(b'expected')}]})
        with patch.object(tool,'assert_closed'):
            with self.assertRaises(ValueError):tool.install({'game':str(game),'source':str(source)},out,confirm=False)
        self.assertFalse((game/'scripts').exists())

if __name__=='__main__':unittest.main()
