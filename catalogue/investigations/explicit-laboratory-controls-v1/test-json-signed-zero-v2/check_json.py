"""Source/JSON-only witness; no Atlas, C++ or backend execution."""
from pathlib import Path
import json,struct,difflib,hashlib
stage=Path(__file__).parent
bits=lambda x:struct.pack('>d',x).hex()
if bits(json.loads('-0'))!='0000000000000000':raise RuntimeError('initial decoder witness')
checks=1
for text in ['-0','0','5001','100000','30000000','-5000','100000000','0.001','5e-324','-5e-324']:
 value=json.loads(text,parse_int=float)
 if bits(value)!=bits(float(text)):raise RuntimeError(text)
 checks+=1
old=(stage.parent/'test_laboratory_controls.py').read_text();new=(stage/'test_laboratory_controls.py').read_text()
if old.replace('return json.loads(result.stdout)','return json.loads(result.stdout, parse_int=float)')!=new:raise RuntimeError('unrelated test edit')
checks+=1
print(json.dumps({'passed':True,'checks':checks,'original_default_decoder_loses_negative_zero':True,'only_change':'json.loads parse_int=float','corrected_test_sha256':hashlib.sha256(new.encode()).hexdigest(),'candidate_calls':0}))
