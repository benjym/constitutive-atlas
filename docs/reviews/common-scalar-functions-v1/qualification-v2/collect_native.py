from pathlib import Path
import ctypes,sys,struct,json,hashlib
p=Path(__file__).parent;out=Path(sys.argv[2]);assert not out.exists();library=Path(sys.argv[1]);lib=ctypes.CDLL(str(library.resolve()));fn=lib.atlas_scalar_functions_probe;fn.argtypes=[ctypes.c_int,ctypes.c_double,ctypes.c_double,ctypes.c_int];fn.restype=ctypes.c_char_p
rows=[]
for c in json.loads((p/'requests.json').read_text())['cases']:
 a=struct.unpack('>d',bytes.fromhex(c['a_bits']))[0];b=struct.unpack('>d',bytes.fromhex(c['b_bits']))[0];raw=fn(c['kind'],a,b,c['seeds']).decode();rows.append(dict(id=c['id'],raw=raw,response=json.loads(raw)));out.write_text(json.dumps({'backend':'native','artifact_sha256':hashlib.sha256(library.read_bytes()).hexdigest(),'rows':rows},indent=2)+'\n')
print(len(rows),'native scalar observations retained')
