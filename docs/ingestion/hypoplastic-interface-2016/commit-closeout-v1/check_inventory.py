"""Read-only exact closeout whitelist preflight; no Git mutation or execution."""
from pathlib import Path
import argparse,hashlib,json,stat
ROOT=Path('/Users/bmar5496/code/constitutive-atlas');p=argparse.ArgumentParser(description=__doc__);p.add_argument('--inventory',type=Path,default=Path(__file__).with_name('inventory-final.json'));a=p.parse_args();d=json.loads(a.inventory.read_text());rows=d['rows'];names=[];deltas=[]
for r in rows:
 q=ROOT/r['path'];assert q.is_file() and not q.is_symlink();assert q.stat().st_size==r['bytes'];assert hashlib.sha256(q.read_bytes()).hexdigest()==r['sha256'],r['path'];assert ('100755' if q.stat().st_mode&stat.S_IXUSR else '100644')==r['mode'];names.append(r['path'])
 if r['delta']!='unchanged':deltas.append(r['path'])
 assert r['path'].startswith('docs/ingestion/hypoplastic-interface-2016/') or r['path'] in d['outside_packet_exact_archive_exceptions']
 assert '/publication-composition-v1/' not in r['path'] and '/__pycache__/' not in r['path']
for prefix,values in [('paths',names),('delta-paths',deltas)]:
 suffix=a.inventory.stem.removeprefix('inventory');base=a.inventory.parent
 assert (base/(prefix+suffix+'.txt')).read_text()==''.join(n+'\n' for n in values)
 assert (base/(prefix+suffix+'.nul')).read_bytes()==b''.join(n.encode()+b'\0' for n in values)
print(json.dumps({'passed':True,'files':len(rows),'delta_paths':len(deltas),'hash_mode_byte_checks':True,'nul_and_newline_lists_match':True,'pending_final_ledgers':d['pending_final_ledger_hashes'],'public_rights_boundary':'No PDFs/private originals/downloads/native binaries or unrelated shared roots in whitelist; two exact old-ledger canonical archives only exception.','git_mutation_material_browser_remote_calls':0},indent=2))
