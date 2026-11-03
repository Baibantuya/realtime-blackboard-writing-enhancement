"""Resolve scene registers from actual IP-XACT or the final Vivado HWH.

No hardcoded offsets. The retained legacy BD cell name does not identify its ABI.
"""
from pathlib import Path
import xml.etree.ElementTree as ET

from scene_stage import validate_registers
from scene_tracking import ABI

VLNV = 'whiteboard.org:hls:board_scene_quantize:1.0'
NS = {'s': 'http://www.spiritconsortium.org/XMLSchema/SPIRIT/1685-2009'}


def number(value):
    text = str(value).strip()
    return int(text, 16 if text.lower().startswith('0x') else 10)


def canonical(name):
    return {'CTRL':'AP_CTRL', 'ap_return':'AP_RETURN', 'control_r':'control'}.get(name, name)


def insert(registers, name, offset, width):
    name = canonical(name)
    if name in registers:
        raise ValueError('Duplicate register: '+name)
    registers[name] = {'offset':number(offset), 'width':number(width)}


def from_component(path):
    root = ET.parse(str(path)).getroot()
    vlnv = ':'.join(root.findtext('s:'+tag, namespaces=NS) or ''
                    for tag in ('vendor','library','name','version'))
    if vlnv != VLNV:
        raise ValueError('Wrong component VLNV: '+vlnv)
    registers = {}
    for register in root.findall('.//s:memoryMap/s:addressBlock/s:register', NS):
        insert(registers, register.findtext('s:name', namespaces=NS),
               register.findtext('s:addressOffset', namespaces=NS),
               register.findtext('s:size', namespaces=NS))
    validate_registers(registers, ABI, vlnv)
    return registers


def from_hwh(path, component=None):
    root = ET.parse(str(path)).getroot()
    modules = [module for module in root.iter('MODULE')
               if module.get('VLNV') == VLNV]
    if len(modules) != 1:
        raise ValueError('Expected exactly one scene IP in final HWH')
    module = modules[0]
    registers = {}
    for register in module.iter('REGISTER'):
        # Vivado HWH stores offsets/sizes in PROPERTY children; simplified
        # XML fixtures and some exporters put them directly on REGISTER.
        fields=dict(register.attrib)
        fields.update({p.attrib['NAME']:p.attrib['VALUE']
                       for p in register.findall('./PROPERTY')})
        insert(registers, register.attrib['NAME'],
               fields['ADDRESS_OFFSET'], fields['SIZE'])
    validate_registers(registers, ABI, VLNV)
    if component is not None:
        expected = from_component(component)
        if registers != expected:
            raise ValueError('HWH registers differ from exported scene component')
    name = module.get('FULLNAME', '/'+module.attrib['INSTANCE']).lstrip('/')
    ranges = [entry for entry in root.iter('MEMRANGE')
              if entry.get('INSTANCE') in (name, module.attrib['INSTANCE'])
              and entry.get('SLAVEBUSINTERFACE') == 's_axi_control']
    spans = {(number(entry.attrib['BASEVALUE']), number(entry.attrib['HIGHVALUE']))
             for entry in ranges}
    if len(spans) != 1:
        raise ValueError('Missing or ambiguous scene control address range')
    base, high = spans.pop()
    if high < base or high-base+1 < max(r['offset']+r['width']//8 for r in registers.values()):
        raise ValueError('Scene control address range is too small')
    return {'instance':name, 'vlnv':VLNV, 'abi':ABI, 'base':base,
            'length':high-base+1, 'registers':registers}
