"""Real release contracts plus controlled negative tests; all IO handles are mocks."""
import gc
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import weakref
import xml.etree.ElementTree as ET

PACKAGE = Path(__file__).resolve().parents[1]
W = PACKAGE
E = PACKAGE / 'tests/fixtures'
TEMP_BASE = (E / 'test_tmp').resolve()
if not TEMP_BASE.is_relative_to(W.resolve()):
    raise RuntimeError('test scratch must remain inside workspace')
TEMP_BASE.mkdir(exist_ok=True)
tempfile.tempdir = str(TEMP_BASE)
HWH = E / 'v24.hwh'
sys.path.insert(0, str(PACKAGE))
from pynq_tools import codegen, dma, overlay, benchmark

HEADERS = {
    '/board_rectify_rgb_0': 'rectify/xboard_rectify_rgb_hw.h',
    '/board_quantize_rgb_0': 'scene/xboard_scene_quantize_hw.h',
    '/whiteboard_restore_0': 'restore/xwhiteboard_restore_hw.h',
}
SCENE_POINTERS = {n: {'width': 32, 'words': [n]} for n in ('src', 'canvas_in', 'canvas_out', 'metadata', 'dst')}
RESTORE_POINTERS = {n: {'width': 64, 'words': [n + '_1', n + '_2']} for n in ('input_r', 'output_r', 'background', 'previous', 'pixel_quiet', 'block_state', 'roi')}


class MockIP:
    def __init__(self, mode='done'):
        self.started, self.mode, self.mem, self.writes = False, mode, {}, []
    def read(self, off):
        if off != 0: return self.mem.get(off, 0)
        if not self.started: return 4
        if self.mode == 'read_error': raise OSError('mock read failure')
        return 6 if self.mode == 'done' else 0
    def write(self, off, value):
        self.writes.append((off, value)); self.mem[off] = value
        if off == 0:
            self.started = True
            if self.mode == 'write_error': raise OSError('mock write took effect then failed')


class MockBuffer:
    def __init__(self, addr=0x1000):
        self.physical_address, self.nbytes = addr, 64
        self.events, self.freed = [], False
    def flush(self): self.events.append('flush')
    def invalidate(self): self.events.append('invalidate')
    def freebuffer(self): self.freed = True; self.events.append('free')


class Clock:
    def __init__(self): self.value = 0
    def __call__(self): self.value += .01; return self.value
    def sleep(self, duration): self.value += duration


class CodegenTests(unittest.TestCase):
    def test_all_70_real_register_words_match_independent_hls_headers(self):
        total = 0
        for ip, header in HEADERS.items():
            with self.subTest(ip=ip):
                regs = codegen.parse_hwh_file(HWH, ip)
                words = codegen.header_words(codegen.parse_hls_header(E / header))
                self.assertEqual({n: {k: r[k] for k in ('offset', 'width')} for n, r in regs.items()}, words)
                total += len(regs)
        self.assertEqual(total, 70)

    def test_exact_instance_rejects_substring(self):
        self.assertEqual(codegen.parse_hwh_file(HWH, 'board_quantize_rgb_0'), codegen.parse_hwh_file(HWH, '/board_quantize_rgb_0'))
        with self.assertRaises(ValueError): codegen.parse_hwh_file(HWH, 'quantize')

    def mutate_xml(self, action, expected=ValueError):
        tree = ET.parse(HWH)
        module = next(m for m in tree.getroot().iter('MODULE') if m.get('FULLNAME') == '/board_quantize_rgb_0')
        action(tree.getroot(), module)
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'bad.hwh'; tree.write(p)
            with self.assertRaises(expected): codegen.parse_hwh_file(p, '/board_quantize_rgb_0')

    def test_missing_offset_fails(self):
        def action(root, m):
            r = next(m.iter('REGISTER')); r.remove(r.find("./PROPERTY[@NAME='ADDRESS_OFFSET']"))
        self.mutate_xml(action)

    def test_duplicate_instance_fails(self):
        self.mutate_xml(lambda root, m: root.append(m))

    def test_duplicate_register_fails(self):
        self.mutate_xml(lambda root, m: m.append(next(m.iter('REGISTER'))))

    def test_overlap_fails(self):
        def action(root, m):
            list(m.iter('REGISTER'))[1].find("./PROPERTY[@NAME='ADDRESS_OFFSET']").set('VALUE', '0')
        self.mutate_xml(action)

    def test_bad_xml_fails(self):
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'bad.hwh'; p.write_text('<broken', encoding='utf-8')
            with self.assertRaises(ET.ParseError): codegen.parse_hwh_file(p, '/x')

    def test_namespace_supported(self):
        tree = ET.parse(HWH)
        for e in tree.getroot().iter(): e.tag = '{urn:test}' + e.tag
        with tempfile.TemporaryDirectory() as t:
            p = Path(t) / 'namespaced.hwh'; tree.write(p)
            self.assertEqual(codegen.parse_hwh_file(p, '/board_quantize_rgb_0'), codegen.parse_hwh_file(HWH, '/board_quantize_rgb_0'))

    def driver(self, ip, pointers):
        ns = {}; exec(codegen.generate_python_driver(codegen.parse_hwh_file(HWH, ip), pointers=pointers), ns)
        mock = MockIP(); return ns['GeneratedIPDriver'](mock), mock

    def test_scene_control_not_skipped_and_32bit_pointer_rejects_truncation(self):
        driver, mock = self.driver('/board_quantize_rgb_0', SCENE_POINTERS)
        driver.write_register('control', 3)
        self.assertEqual(mock.writes[-1], (0x68, 3))
        driver.write_pointer('src', 0xffffffff)
        self.assertEqual(mock.writes[-1], (0x18, 0xffffffff))
        for bad in (-1, 2**32, 1.2, True):
            with self.assertRaises(ValueError): driver.write_pointer('src', bad)
        self.assertEqual(len(mock.writes), 2)

    def test_restore_64bit_pointer_writes_both_words(self):
        driver, mock = self.driver('/whiteboard_restore_0', RESTORE_POINTERS)
        driver.write_pointer('input_r', 0x123456789abcdef0)
        self.assertEqual(mock.writes, [(0x18, 0x9abcdef0), (0x1c, 0x12345678)])
        with self.assertRaises(PermissionError): driver.write_register('ap_return', 1)

    def test_pointer_contract_mismatch_fails(self):
        regs = codegen.parse_hwh_file(HWH, '/board_quantize_rgb_0')
        for spec in ({'src': {'width': 64, 'words': ['src', 'canvas_in']}}, {'src': {'width': 64, 'words': ['src']}}):
            with self.assertRaises(ValueError): codegen.generate_python_driver(regs, pointers=spec)

    def test_class_name_injection_rejected(self):
        with self.assertRaises(ValueError): codegen.generate_python_driver({'r': {'offset': 0, 'width': 32, 'access': 'read-write'}}, 'Bad: pass')

    def test_cli_and_generated_test_actual_filename(self):
        with tempfile.TemporaryDirectory() as t:
            output = Path(t) / 'different_name.py'
            command = [sys.executable, '-B', '-m', 'pynq_tools.codegen', '--input', str(HWH), '--ip', '/board_quantize_rgb_0', '--output', str(output), '--class-name', 'SceneIP', '--generate-test']
            result = subprocess.run(command, cwd=PACKAGE, text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            result = subprocess.run([sys.executable, '-B', str(output.with_name('test_' + output.name))], text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            old = output.read_bytes()
            result = subprocess.run(command, cwd=PACKAGE, text=True, capture_output=True, timeout=20)
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(old, output.read_bytes())


class DmaTests(unittest.TestCase):
    def make(self, mode='done', confirm=True):
        b = MockBuffer(); p = dma.DmaBufferPool((64,), pool_size=1, allocate_fn=lambda **_: b)
        c = Clock(); g = dma.CacheCoherentGuard(MockIP(mode), completion_confirmed=lambda *_: confirm,
                 timeout_seconds=.02, clock=c, sleep=c.sleep)
        return b, p, g

    def recover(self, p):
        p.recover(verify_quiescent=lambda *_: True, reason='mock master disabled and outstanding count zero')

    def test_completed_buffer_flush_invalidate_then_release(self):
        b, p, g = self.make()
        with p.acquire() as lease:
            with g.run_hardware([lease], outputs=[lease]):
                self.assertEqual(b.events, ['flush', 'invalidate'])
                self.assertEqual(lease.state, 'leased')
        with p.acquire() as lease: self.assertIs(lease.buffer, b)
        p.close(); self.assertTrue(b.freed)

    def exercise_failure(self, mode, error, confirm=True):
        b, p, g = self.make(mode, confirm)
        with self.assertRaises(error):
            with p.acquire() as lease:
                with g.run_hardware([lease], outputs=[lease]): pass
        self.assertEqual(lease.state, 'quarantined')
        with self.assertRaises(BufferError):
            with p.acquire(): pass
        with self.assertRaises(BufferError): p.close()
        self.assertFalse(b.freed)
        with self.assertRaises(RuntimeError): p.recover(verify_quiescent=lambda *_: False, reason='not stopped')
        self.assertFalse(b.freed)
        self.recover(p); p.close(); self.assertTrue(b.freed)

    def test_timeout_quarantine_until_confirmed_recovery(self): self.exercise_failure('busy', TimeoutError)
    def test_start_write_may_take_effect_before_exception(self): self.exercise_failure('write_error', OSError)
    def test_mmio_read_error_quarantines(self): self.exercise_failure('read_error', OSError)
    def test_done_without_confirmed_contract_still_quarantines(self): self.exercise_failure('done', TimeoutError, False)

    def test_close_during_cpu_lease_rejected(self):
        b, p, _ = self.make()
        with p.acquire():
            with self.assertRaises(BufferError): p.close()
        p.close()

    def test_gc_retains_unresolved_buffers(self):
        b, p, g = self.make('busy')
        with self.assertRaises(TimeoutError):
            with p.acquire() as lease:
                with g.run_hardware([lease], outputs=[lease]): pass
        ref = weakref.ref(p); del p, lease; gc.collect()
        self.assertIsNotNone(ref()); self.assertFalse(b.freed)
        self.recover(ref()); ref().close()

    def test_allocator_overlap_and_partial_failure_cleanup(self):
        a, b = MockBuffer(), MockBuffer(0x1020)
        it = iter([a, b])
        with self.assertRaises(ValueError): dma.DmaBufferPool((64,), pool_size=2, allocate_fn=lambda **_: next(it))
        self.assertTrue(a.freed and b.freed)
        a = MockBuffer(); it = iter([a])
        with self.assertRaises(StopIteration): dma.DmaBufferPool((64,), pool_size=2, allocate_fn=lambda **_: next(it))
        self.assertTrue(a.freed)

    def test_no_implicit_numpy_or_pynq_allocator(self):
        with self.assertRaises(TypeError): dma.DmaBufferPool((64,))


CANDIDATE_HWH = PACKAGE.parents[1] / 'board/runtime/hardware/imx219-v24-2025-2-c5.hwh'

class OverlayTests(unittest.TestCase):
    def setUp(self):
        self.args = {'backend': 'kv260-fpgautil', 'dtbo': CANDIDATE_HWH.with_suffix('.dtbo')}
        self.hashes = {role: hashlib.sha256(path.read_bytes()).hexdigest() for role, path in {
            'bit': CANDIDATE_HWH.with_suffix('.bit'), 'hwh': CANDIDATE_HWH, 'bit_bin': CANDIDATE_HWH.with_suffix('.bit.bin'), 'dtbo': CANDIDATE_HWH.with_suffix('.dtbo')}.items()}

    def test_readonly_inspection_creates_no_directory_and_does_not_import_pynq(self):
        before = 'pynq' in sys.modules
        with tempfile.TemporaryDirectory() as t:
            destination = Path(t) / 'metadata'
            plan = overlay.inspect_overlay(CANDIDATE_HWH.with_suffix('.bit'), expected_hashes=self.hashes, metadata_dir=destination, **self.args)
            self.assertFalse(destination.exists()); self.assertEqual(plan['side_effects_performed'], [])
        self.assertEqual('pynq' in sys.modules, before)

    def test_wrong_hash_and_missing_file_fail(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError): overlay.inspect_overlay(CANDIDATE_HWH.with_suffix('.bit'), expected_hashes={}, metadata_dir=Path(t)/'m', **self.args)
            with self.assertRaises(FileNotFoundError): overlay.inspect_overlay(Path(t)/'missing.bit', backend='pynq-native', expected_hashes={})

    def test_no_automatic_backend_or_metadata_with_dtbo(self):
        with self.assertRaises(ValueError): overlay.inspect_overlay(CANDIDATE_HWH.with_suffix('.bit'), backend='auto', expected_hashes=self.hashes)
        with self.assertRaises(ValueError): overlay.inspect_overlay(CANDIDATE_HWH.with_suffix('.bit'), metadata_dir=CANDIDATE_HWH.parent, expected_hashes=self.hashes, **self.args)
        with self.assertRaises(NotImplementedError): overlay.execute_overlay()


class BenchmarkTests(unittest.TestCase):
    def make(self, events=(0, 10, 11, 12), warmup=0):
        it = iter(events)
        return benchmark.PynqBenchmarker(event_name='presented_content', latency_scope='PS content stage',
               start_event='process entry', clock=lambda: next(it), warmup_frames=warmup)

    def test_stage_latency_not_startup_or_interval_jitter(self):
        b = self.make()
        for v in (1, 9, 1): b.record_frame(v)
        r = b.compute_statistics()
        self.assertEqual(r['start_to_first_event_ms'], 10000)
        self.assertEqual(r['first_event_stage_latency_ms'], 1)
        self.assertEqual(r['frame_interval_stdev_ms'], 0)
        self.assertGreater(r['stage_latency_stdev_ms'], 0)
        self.assertEqual(r['observed_fps'], 1)
        self.assertEqual(r['performance_evaluation'], 'NOT_EVALUATED')

    def test_explicit_threshold_fails_positive_fps(self):
        b = self.make(); b.record_frame(1); b.record_frame(1, True)
        r = b.compute_statistics(thresholds={'min_observed_fps': 10, 'max_bad_frame_rate': 0})
        self.assertEqual(r['performance_evaluation'], 'FAIL')
        self.assertEqual(r['dropped_frames'], 'NOT_MEASURED')

    def test_empty_and_one_frame_have_no_rate_claim_and_reports_work(self):
        b = self.make()
        with tempfile.TemporaryDirectory() as t:
            b.generate_report(t)
            self.assertIsNone(b.compute_statistics()['observed_fps'])
            b.record_frame(2); b.generate_report(t)
            self.assertEqual(b.compute_statistics(thresholds={'min_observed_fps': 0})['performance_evaluation'], 'NOT_CHECKED')

    def test_warmup_explicit_window(self):
        b = self.make((0, 10, 11, 13), warmup=1)
        for _ in range(3): b.record_frame(1)
        r = b.compute_statistics()
        self.assertEqual((r['window_events'], r['observed_fps'], r['window_start_s']), (2, .5, 11))

    def test_bad_metric_input_rejected(self):
        with self.assertRaises(ValueError): self.make().record_frame(float('nan'))
        b = self.make((0, 1, 1)); b.record_frame(1)
        with self.assertRaises(ValueError): b.record_frame(1)
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError): b.generate_report(t, name='../escape')

    def test_golden_no_false_nan_empty_or_unsigned_wrap_pass(self):
        import numpy as np
        self.assertFalse(benchmark.compare_golden(np.array([0], dtype='uint8'), np.array([255], dtype='uint8'))['is_match'])
        self.assertTrue(benchmark.compare_golden([1, 2], [2, 3], tolerance=1)['is_match'])
        for a, b, kw in (([], [], {}), ([float('nan')], [1], {}), ([1], [1], {'mask': [False]}), ([1], [1], {'tolerance': -1})):
            with self.assertRaises(ValueError): benchmark.compare_golden(a, b, **kw)


if __name__ == '__main__':
    sys.stderr.reconfigure(encoding='utf-8')
    unittest.main(verbosity=2)
