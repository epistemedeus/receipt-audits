#!/usr/bin/env python3
"""Integrity failure/recovery tests with cached public archives only."""
import copy
import importlib.util
import json
import pathlib
import shutil
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('pinned_prepare', ROOT / 'prepare.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class PreparationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / '.scratch')
        self.root = pathlib.Path(self.temp.name)
        (self.root / '.scratch').mkdir(mode=0o700)
        self.old_root, self.old_lock = module.ROOT, module.LOCK
        module.ROOT, module.LOCK = self.root, copy.deepcopy(self.old_lock)
        for version in module.LOCK['packages']:
            shutil.copyfile(ROOT / '.scratch' / (version + '.tgz'), self.root / '.scratch' / (version + '.tgz'))

    def tearDown(self):
        module.ROOT, module.LOCK = self.old_root, self.old_lock
        self.temp.cleanup()

    def test_verified_offline_recovery(self):
        module.prepare(offline=True)
        for version in module.LOCK['packages']:
            data = json.loads((self.root / '.scratch' / (version + '-source.json')).read_text())
            self.assertEqual(set(data), set(module.LOCK['packages'][version]['sources']))

    def test_missing_offline_archive_refused(self):
        (self.root / '.scratch' / '1.13.2.tgz').unlink()
        with self.assertRaisesRegex(RuntimeError, 'Missing cached archive'):
            module.prepare(offline=True)

    def test_tampered_archive_refused_then_original_recovers(self):
        archive = self.root / '.scratch' / '1.13.2.tgz'
        original = archive.read_bytes()
        archive.write_bytes(original + b'tampered')
        with self.assertRaisesRegex(RuntimeError, 'Archive integrity mismatch'):
            module.prepare(offline=True)
        self.assertFalse((self.root / '.scratch' / '1.13.2-source.json').exists())
        archive.write_bytes(original)
        module.prepare(offline=True)

    def test_member_hash_refused(self):
        module.LOCK['packages']['1.13.2']['sources']['builder']['sha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'Member hash mismatch'):
            module.prepare(offline=True)

    def test_excerpt_hash_refused(self):
        module.LOCK['packages']['1.13.2']['sources']['builder']['excerptSha256'] = '0' * 64
        with self.assertRaisesRegex(RuntimeError, 'Excerpt hash mismatch'):
            module.prepare(offline=True)

if __name__ == '__main__':
    unittest.main()
