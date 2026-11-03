"""Regression against actual old/new HWH files and malformed contracts; no hardware."""
from pathlib import Path
import importlib.util, os, subprocess, sys, tempfile, unittest, xml.etree.ElementTree as ET

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
target=Path(os.environ.get('WB_CODEGEN_UNDER_TEST',str(HERE/'codegen_pynq_driver.py')))
spec=importlib.util.spec_from_file_location('under_test',target)
codegen=importlib.util.module_from_spec(spec); spec.loader.exec_module(codegen)
HWH=[HERE/'fixtures/v24_2021_2.hwh', HERE/'fixtures/c5_2025_2.hwh']
IPS={'board_rectify_rgb_0':15,'board_quantize_rgb_0':20,'whiteboard_restore_0':35}

class RegisterContractTests(unittest.TestCase):
    def parse(self, xml, name='core'):
        fixtures=HERE/'fixtures';fixtures.mkdir(exist_ok=True)
        with tempfile.NamedTemporaryFile('w',suffix='.hwh',dir=fixtures,encoding='utf-8',delete=False) as f:
            f.write(xml);p=Path(f.name)
        try:return codegen.parse_hwh_file(p,name)
        finally:p.unlink()

    def test_actual_old_and_new_hwh(self):
        for path in HWH:
            tree=ET.parse(path)
            for ip,count in IPS.items():
                with self.subTest(path=path.name,ip=ip):
                    modules=[m for m in tree.iter('MODULE') if m.get('INSTANCE')==ip or m.get('NAME')==ip]
                    self.assertEqual(len(modules),1)
                    expected={r.attrib['NAME'].lower():int(r.find("PROPERTY[@NAME='ADDRESS_OFFSET']").attrib['VALUE'],0)
                              for r in modules[0].iter('REGISTER')}
                    self.assertEqual(len(expected),count)
                    self.assertEqual(codegen.parse_hwh_file(path,ip),expected)

    def test_property_decimal_and_attribute_hex(self):
        xml='<ROOT><MODULE NAME="core"><REGISTER NAME="A"><PROPERTIES><PROPERTY NAME="ADDRESS_OFFSET" VALUE="16"/></PROPERTIES></REGISTER><REGISTER NAME="B" OFFSET="0X18"/></MODULE></ROOT>'
        self.assertEqual(self.parse(xml),{'a':16,'b':24})

    def test_exact_instance_not_substring(self):
        xml='<ROOT><MODULE NAME="core_extra"><REGISTER NAME="A" OFFSET="4"/></MODULE><MODULE NAME="core"><REGISTER NAME="A" OFFSET="8"/></MODULE></ROOT>'
        self.assertEqual(self.parse(xml),{'a':8})

    def test_full_hierarchy_disambiguates(self):
        xml='<ROOT><MODULE NAME="core" FULLNAME="/a/core"><REGISTER NAME="A" OFFSET="4"/></MODULE><MODULE NAME="core" FULLNAME="/b/core"><REGISTER NAME="A" OFFSET="8"/></MODULE></ROOT>'
        self.assertEqual(self.parse(xml,'/b/core'),{'a':8})
        with self.assertRaises(ValueError):self.parse(xml)

    def test_xml_namespace(self):
        xml='<ROOT xmlns="urn:test"><MODULE NAME="core"><REGISTER NAME="A"><PROPERTIES><PROPERTY NAME="ADDRESS_OFFSET" VALUE="0x10"/></PROPERTIES></REGISTER></MODULE></ROOT>'
        self.assertEqual(self.parse(xml),{'a':16})

    def test_field_offsets_are_not_register_offsets(self):
        xml='<ROOT><MODULE INSTANCE="core" NAME="generic"><REGISTER NAME="A"><PROPERTY NAME="ADDRESS_OFFSET" VALUE="24"/><FIELDS><FIELD NAME="A"><PROPERTY NAME="ADDRESS_OFFSET" VALUE="0"/></FIELD></FIELDS></REGISTER></MODULE></ROOT>'
        self.assertEqual(self.parse(xml),{'a':24})

    def test_missing_offset_is_rejected(self):
        with self.assertRaises(ValueError):self.parse('<ROOT><MODULE NAME="core"><REGISTER NAME="A"/></MODULE></ROOT>')

    def test_conflicting_metadata_is_rejected(self):
        xml='<ROOT><MODULE NAME="core"><REGISTER NAME="A" OFFSET="4"><PROPERTIES><PROPERTY NAME="ADDRESS_OFFSET" VALUE="8"/></PROPERTIES></REGISTER></MODULE></ROOT>'
        with self.assertRaises(ValueError):self.parse(xml)

    def test_duplicate_register_name_is_rejected(self):
        with self.assertRaises(ValueError):self.parse('<ROOT><MODULE NAME="core"><REGISTER NAME="A" OFFSET="4"/><REGISTER NAME="a" OFFSET="8"/></MODULE></ROOT>')

    def test_duplicate_offsets_are_rejected(self):
        with self.assertRaises(ValueError):self.parse('<ROOT><MODULE NAME="core"><REGISTER NAME="A" OFFSET="4"/><REGISTER NAME="B" OFFSET="4"/></MODULE></ROOT>')

    def test_invalid_offsets_are_rejected(self):
        for value in ['-4','3','junk']:
            with self.subTest(value=value),self.assertRaises(ValueError):
                self.parse(f'<ROOT><MODULE NAME="core"><REGISTER NAME="A" OFFSET="{value}"/></MODULE></ROOT>')

    def test_no_partial_name_match(self):
        with self.assertRaises(ValueError):self.parse('<ROOT><MODULE NAME="my_core"><REGISTER NAME="A" OFFSET="4"/></MODULE></ROOT>')

    def test_empty_or_invalid_register_name(self):
        for name in ['', 'a-b']:
            with self.subTest(name=name),self.assertRaises(ValueError):
                self.parse(f'<ROOT><MODULE NAME="core"><REGISTER NAME="{name}" OFFSET="4"/></MODULE></ROOT>')

    def test_application_control_register_is_generated(self):
        namespace={}
        exec(compile(codegen.generate_python_driver({'ap_ctrl':0,'control':0x68},'CandidateDriver'),'<generated>','exec'),namespace)
        class Mock:
            def __init__(self):self.writes=[]
            def write(self,offset,value):self.writes.append((offset,value))
            def read(self,offset):return 4
        mock=Mock();driver=namespace['CandidateDriver'](mock)
        driver.set_control(0x12345678)
        self.assertEqual(mock.writes,[(0x68,0x12345678)])

    def test_real_header_and_64_bit_width(self):
        header=HERE/'fixtures/xwhiteboard_restore_hw.h'
        registers=codegen.parse_hls_header(header)
        self.assertEqual(registers['input_r'],0x18)
        self.assertEqual(registers.widths['input_r'],64)

    def test_generated_wide_register_and_access(self):
        registers=self.parse('<ROOT><MODULE NAME="core"><REGISTER NAME="ap_ctrl" OFFSET="0"/><REGISTER NAME="buffer" OFFSET="24"><PROPERTY NAME="SIZE" VALUE="64"/><PROPERTY NAME="ACCESS" VALUE="write-only"/></REGISTER><REGISTER NAME="result" OFFSET="40"><PROPERTY NAME="ACCESS" VALUE="read-only"/></REGISTER></MODULE></ROOT>')
        namespace={};exec(compile(codegen.generate_python_driver(registers,'WideDriver'),'<generated>','exec'),namespace)
        class Mock:
            def __init__(self):self.writes=[]
            def write(self,offset,value):self.writes.append((offset,value))
            def read(self,offset):return 0xA5
        mock=Mock();driver=namespace['WideDriver'](mock)
        driver.set_buffer(0x12345678ABCDEF01)
        self.assertEqual(mock.writes,[(24,0xABCDEF01),(28,0x12345678)])
        self.assertFalse(hasattr(driver,'get_buffer'))
        self.assertFalse(hasattr(driver,'set_result'))
        self.assertEqual(driver.get_result(),0xA5)
        for value in [-1,1<<64]:
            with self.assertRaises(ValueError):driver.set_buffer(value)

    def test_read_only_suffix_pair_is_not_a_writable_pointer(self):
        registers=self.parse('<ROOT><MODULE NAME="core"><REGISTER NAME="counter_1" OFFSET="24"><PROPERTY NAME="ACCESS" VALUE="read-only"/></REGISTER><REGISTER NAME="counter_2" OFFSET="28"><PROPERTY NAME="ACCESS" VALUE="read-only"/></REGISTER></MODULE></ROOT>')
        namespace={};exec(compile(codegen.generate_python_driver(registers,'CounterDriver'),'<generated>','exec'),namespace)
        driver=namespace['CounterDriver'](None)
        self.assertFalse(hasattr(driver,'set_counter_address'))
        self.assertTrue(hasattr(driver,'get_counter_1'))
        self.assertTrue(hasattr(driver,'get_counter_2'))

    def test_generated_test_imports_output_module(self):
        # Keep each output run for inspection, without deleting directory trees.
        out=HERE/'generated_cli';out.mkdir(exist_ok=True)
        contract=out/'contract.json';contract.write_text('{"registers":{"ap_ctrl":0,"value":16}}',encoding='utf-8')
        driver=out/'demo_driver.py'
        result=subprocess.run([sys.executable,'-B',str(target),'--input',str(contract),'--class-name','DemoIP',
                               '--output',str(driver),'--generate-test'],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        result=subprocess.run([sys.executable,'-B',str(out/'test_demo_driver.py')],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
