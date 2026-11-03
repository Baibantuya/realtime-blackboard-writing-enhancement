"""Parse the bounded Xilinx .bit container; no FPGA packet execution."""
import struct

def parse_bit(data):
    pos=0
    def read(n):
        nonlocal pos
        if pos+n>len(data):raise ValueError('Truncated bit container')
        v=data[pos:pos+n];pos+=n;return v
    def size(n):return int.from_bytes(read(n),'big')
    magic=read(size(2))
    if magic!=bytes.fromhex('0ff00ff00ff00ff000'):raise ValueError('Unexpected bit magic')
    if size(2)!=1:raise ValueError('Unexpected initial tag length')
    fields={}
    while True:
        tag=read(1).decode('ascii')
        if tag=='e':
            payload=read(size(4))
            if pos!=len(data):raise ValueError('Unexpected trailing bit data')
            if set(fields)!={'a','b','c','d'}:raise ValueError('Incomplete bit header')
            return fields,payload
        if tag not in 'abcd' or tag in fields:raise ValueError('Unexpected bit header tag')
        fields[tag]=read(size(2)).rstrip(b'\0').decode('ascii')
