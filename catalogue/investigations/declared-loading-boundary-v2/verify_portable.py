from pathlib import Path
import hashlib,json,subprocess,sys
p=Path(__file__).resolve().parent;m=json.loads((p/'portable-manifest-v1.json').read_text())
assert hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest()==m['original_manifest_sha256']
for name,h in m['files'].items():assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
assert set(m['omitted_incidental_bytecode'])=={'__pycache__/assess.cpython-314.pyc'}
subprocess.run([sys.executable,'-B',str(p/'assess.py'),'--both'],check=True)
print('portable replay verified every tracked original manifest member; ignored bytecode is not required')
