from pathlib import Path
import datetime,hashlib,json
from bit_format5 import parse_bit
r=Path(__file__).resolve().parent;p=r/'hardware_candidate5';name='imx219-v24-2025-2-c5'
assert json.loads((p/'bootgen5_status.json').read_text(encoding='utf-8-sig'))['exit_code']==0
bit=p/(name+'.bit');binfile=p/(name+'.bit.bin')
header,payload=parse_bit(bit.read_bytes())
assert len(payload)%4==0
expected=bytearray(len(payload))
for i in range(4):expected[i::4]=payload[3-i::4]
assert binfile.read_bytes()==expected, 'BIN is not the expected word-swapped configuration payload'
out={'status':'PASS_BOOTGEN_AND_PAYLOAD_COMPARISON','checked_at':datetime.datetime.now().astimezone().isoformat(),
     'expected_transform':'Swap byte order within each 32-bit configuration word; bit header removed.',
     'bytes':len(expected),'bit_sha256':hashlib.sha256(bit.read_bytes()).hexdigest(),'bin_sha256':hashlib.sha256(expected).hexdigest(),
     'board_test':'NOT_RUN'}
(p/'bin_validation.json').write_text(json.dumps(out,indent=2)+'\n',encoding='utf-8')
print(json.dumps(out))
