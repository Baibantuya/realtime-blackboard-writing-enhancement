"""Constructed offline tests; fake bit/DTBO bytes are never FPGA images."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
SCRIPT = HERE.parent / 'scripts/preflight.py'
spec = importlib.util.spec_from_file_location('offline_preflight', SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
XML = '''<SYSTEM><MODULES><MODULE INSTANCE="accelerator_0" FULLNAME="/accelerator_0" VLNV="example.org:hls:accelerator:1.0">
<REGISTERS><REGISTER NAME="CTRL"><PROPERTY NAME="ADDRESS_OFFSET" VALUE="0"/><PROPERTY NAME="SIZE" VALUE="32"/>
<PROPERTY NAME="ACCESS" VALUE="read-write"/><FIELDS><FIELD NAME="AP_DONE"><PROPERTY NAME="BIT_OFFSET" VALUE="1"/><PROPERTY NAME="BIT_WIDTH" VALUE="1"/></FIELD></FIELDS></REGISTER></REGISTERS>
</MODULE></MODULES><MEMRANGE INSTANCE="accelerator_0" MEMTYPE="REGISTER" SLAVEBUSINTERFACE="s_axi_control" BASEVALUE="0x40000000" HIGHVALUE="0x4000ffff"/></SYSTEM>'''


class OfflineTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='preflight_test_', dir=HERE)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        for name, data in {'demo.bit': b'SYNTHETIC_NOT_A_BITSTREAM', 'demo.hwh': XML.encode(), 'demo.dtbo': b'SYNTHETIC_NOT_A_DTBO'}.items():
            (self.root / name).write_bytes(data)
        files = {role: {'path': name, 'sha256': module.sha(self.root / name)}
                 for role, name in [('bit', 'demo.bit'), ('hwh', 'demo.hwh'), ('dtbo', 'demo.dtbo')]}
        self.c = {'schema': 1, 'release': 'constructed-example', 'backend': 'other_board_documented_only',
                  'files': files, 'ips': [{'fullname': '/accelerator_0', 'vlnv': 'example.org:hls:accelerator:1.0',
                    'address': {'interface': 's_axi_control', 'base': '0x40000000', 'high': '0x4000ffff'},
                    'registers': {'CTRL': {'offset': 0, 'width': 32, 'access': 'read-write', 'fields': {'AP_DONE': {'offset': 1, 'width': 1}}}}}]}
        self.config = self.root / 'config.json'

    def run_check(self):
        self.config.write_text(json.dumps(self.c), encoding='utf-8')
        return module.inspect(self.root, self.config)

    def failure(self, prefix):
        r = self.run_check()
        self.assertEqual(r['status'], 'FAIL')
        self.assertTrue(any(x['status'] == 'fail' and x['code'].startswith(prefix) for x in r['checks']), r)

    def test_normal_and_no_input_writes(self):
        self.config.write_text(json.dumps(self.c), encoding='utf-8')
        before = {p.name: module.sha(p) for p in self.root.iterdir()}
        r = module.inspect(self.root, self.config)
        self.assertEqual(r['status'], 'PASS_OFFLINE')
        self.assertEqual(before, {p.name: module.sha(p) for p in self.root.iterdir()})
        self.assertTrue(any(x['code'] == 'board_function' and x['status'] == 'not_checked' for x in r['checks']))

    def test_missing_file(self):
        (self.root / 'demo.dtbo').unlink()
        self.failure('file:dtbo')

    def test_corrupt_bit(self):
        (self.root / 'demo.bit').write_bytes(b'corrupt')
        self.failure('sha256:bit')

    def test_name_mismatch(self):
        (self.root / 'demo.hwh').rename(self.root / 'renamed.hwh')
        self.c['files']['hwh']['path'] = 'renamed.hwh'
        self.failure('hwh_pair_name')

    def test_missing_ip(self):
        self.c['ips'][0]['fullname'] = '/absent'
        self.failure('ip_count:')

    def test_wrong_vlnv(self):
        self.c['ips'][0]['vlnv'] = 'example.org:hls:wrong:1.0'
        self.failure('vlnv:')

    def test_register_offset(self):
        self.c['ips'][0]['registers']['CTRL']['offset'] = 4
        self.failure('register_offset:')

    def test_register_width(self):
        self.c['ips'][0]['registers']['CTRL']['width'] = 64
        self.failure('register_width:')

    def test_missing_register(self):
        self.c['ips'][0]['registers']['missing'] = {'offset': 16, 'width': 32}
        self.failure('register_count:')

    def test_field_drift(self):
        self.c['ips'][0]['registers']['CTRL']['fields']['AP_DONE']['offset'] = 2
        self.failure('field_offset:')

    def test_address_drift(self):
        self.c['ips'][0]['address']['base'] = '0x40001000'
        self.failure('address:')

    def test_malformed_xml(self):
        (self.root / 'demo.hwh').write_text('<SYSTEM>', encoding='utf-8')
        self.c['files']['hwh']['sha256'] = module.sha(self.root / 'demo.hwh')
        self.failure('hwh')

    def test_duplicate_module(self):
        raw = XML.replace('</MODULE></MODULES>', '</MODULE>' + XML.split('<MODULES>')[1].split('</MODULES>')[0] + '</MODULES>')
        (self.root / 'demo.hwh').write_text(raw, encoding='utf-8')
        self.c['files']['hwh']['sha256'] = module.sha(self.root / 'demo.hwh')
        self.failure('ip_count:')

    def test_xml_entities_rejected(self):
        (self.root / 'demo.hwh').write_text('<!DOCTYPE SYSTEM [<!ENTITY x "data">]>' + XML, encoding='utf-8')
        self.c['files']['hwh']['sha256'] = module.sha(self.root / 'demo.hwh')
        self.failure('hwh')

    def test_path_traversal(self):
        self.c['files']['bit']['path'] = '../outside.bit'
        self.failure('path:bit')

    def test_unknown_config_field(self):
        self.c['ipz'] = []
        self.failure('config_schema')

    def test_empty_contract(self):
        self.c['ips'] = []
        self.failure('config_schema')

    def test_null_json(self):
        self.config.write_text('null', encoding='utf-8')
        self.assertEqual(module.inspect(self.root, self.config)['status'], 'FAIL')

    def test_manifest_drift(self):
        entries = {s['path']: {'sha256': s['sha256'], 'size': (self.root / s['path']).stat().st_size} for s in self.c['files'].values()}
        entries['demo.bit']['sha256'] = '0' * 64
        (self.root / 'manifest.json').write_text(json.dumps({'release': self.c['release'], 'files': entries}), encoding='utf-8')
        self.c['manifest'] = {'path': 'manifest.json'}
        self.failure('manifest_sha256:bit')

    def test_identity_drift(self):
        (self.root / 'identity.json').write_text('{"release":"wrong"}', encoding='utf-8')
        self.c['identity'] = {'path': 'identity.json', 'fields': {'release': self.c['release']}}
        self.failure('identity:release')

    def test_environment_mismatch(self):
        (self.root / 'env.json').write_text('{"kernel":"other"}', encoding='utf-8')
        self.c['environment'] = {'expected': {'kernel': 'expected'}, 'record': 'env.json'}
        self.failure('environment:kernel')

    def test_cli_exit_codes_and_json(self):
        self.config.write_text(json.dumps(self.c), encoding='utf-8')
        command = [sys.executable, str(SCRIPT), '--root', str(self.root), '--config', str(self.config)]
        passed = subprocess.run(command, capture_output=True, encoding='utf-8')
        self.assertEqual(passed.returncode, 0, passed.stderr)
        self.assertEqual(json.loads(passed.stdout)['status'], 'PASS_OFFLINE')
        (self.root / 'demo.bit').unlink()
        failed = subprocess.run(command, capture_output=True, encoding='utf-8')
        self.assertEqual(failed.returncode, 1, failed.stderr)
        self.assertEqual(json.loads(failed.stdout)['status'], 'FAIL')

    def test_malformed_metadata_types(self):
        (self.root / 'bad.json').write_text('[]', encoding='utf-8')
        variants = {'manifest': {'path': 'bad.json'},
                    'identity': {'path': 'bad.json', 'fields': {'release': 'expected'}},
                    'environment': {'record': 'bad.json', 'expected': {'kernel': 'expected'}}}
        for field, value in variants.items():
            with self.subTest(field=field):
                self.c[field] = value
                self.failure(field)
                del self.c[field]


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(OfflineTests)
    names = [test.id() for test in suite]
    outcome = unittest.TextTestRunner(verbosity=2).run(suite)
    print(json.dumps({'kind': 'constructed_offline_tests', 'tests_run': outcome.testsRun,
        'successful': outcome.wasSuccessful(), 'failures': len(outcome.failures), 'errors': len(outcome.errors),
        'cases': names, 'python': platform.python_version(), 'os': platform.system(),
        'script_sha256': module.sha(SCRIPT), 'test_sha256': module.sha(Path(__file__))}, indent=2))
    raise SystemExit(0 if outcome.wasSuccessful() else 1)
