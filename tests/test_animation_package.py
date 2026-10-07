"""Structural tests only; these are NOT Maya runtime/visual tests."""
import hashlib
import importlib.util
from pathlib import Path
import re
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('builder', ROOT/'scripts/build_animation.py')
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)

class NativeAnimationPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = zipfile.ZipFile(ROOT/'deliverables/Reimu_native_source.zip')
        cls.package = zipfile.ZipFile(ROOT/'deliverables/Reimu_Greeting_DRAFT_Maya.zip')
        cls.scene = cls.package.read('Reimu/Reimu_Greeting_DRAFT.ma').decode('cp1252')

    @classmethod
    def tearDownClass(cls):
        cls.source.close()
        cls.package.close()

    def test_zip_integrity(self):
        self.assertIsNone(self.package.testzip())

    def test_all_animation_curves_are_time_driven_and_connected(self):
        for plug, keys in builder.TRACKS.items():
            name = 'arenaGreeting_' + plug.replace('.', '_')
            self.assertIn(f'connectAttr "time1.outTime" "{name}.i";', self.scene)
            self.assertIn(f'connectAttr "{name}.o" "{plug}";', self.scene)
            expected = f'setAttr -s {len(keys)} ".ktv[0:{len(keys)-1}]" ' + ' '.join(f'{t} {v}' for t,v in keys) + ';'
            block = re.search(r'^createNode animCurveT[AL] -n "' + name + r'";.*?(?=^createNode |^connectAttr )', self.scene, re.M|re.S)
            self.assertIsNotNone(block)
            self.assertIn(expected, block.group(0))

    def test_original_mesh_blocks_unchanged(self):
        old = self.source.read('Reimu/Reimu_Rig_master.ma').decode('cp1252')
        pattern = r'^createNode mesh .*?(?=^createNode |^select -ne |\Z)'
        before = re.findall(pattern, old, re.M|re.S)
        after = re.findall(pattern, self.scene, re.M|re.S)
        self.assertEqual(239, len(before))
        self.assertEqual(before, after)

    def test_original_texture_bytes_unchanged(self):
        count = 0
        for name in self.source.namelist():
            if Path(name).suffix.lower() not in ('.tga','.png','.tx'):
                continue
            self.assertEqual(hashlib.sha256(self.source.read(name)).digest(),
                             hashlib.sha256(self.package.read(name)).digest())
            count += 1
        self.assertGreater(count, 10)

    def test_usage_instructions_and_preview_script_present(self):
        doc = self.package.read('Reimu/READ_ME_FIRST.md').decode()
        self.assertIn('belum diuji', doc)
        self.assertIn('Megabubu', doc)
        self.assertIn('nonkomersial', doc)
        compile(self.package.read('Reimu/open_preview.py'), 'open_preview.py', 'exec')
        self.assertIn('workspace -fr "sourceImages" ".";', self.package.read('Reimu/workspace.mel').decode())

if __name__ == '__main__':
    unittest.main()
