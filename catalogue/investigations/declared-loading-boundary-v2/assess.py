from pathlib import Path
import csv, hashlib, json, sys
p=Path(__file__).resolve().parent
freeze=json.loads((p/'pre-build-freeze.json').read_text())
for name,h in freeze['files'].items():
    assert hashlib.sha256((p/name).read_bytes()).hexdigest()==h,name
expected=json.loads((p/'expected.json').read_text())
def assess(path):
    with Path(path).open()as f:
        reader=csv.DictReader(f)
        assert reader.fieldnames==['id','phase','ok','inputs_unchanged']
        rows=list(reader)
    assert len(rows)==len(expected)==406
    for e,o in zip(expected,rows):
        assert (e['id'],e['phase'])==(o['id'],o['phase'])
        assert o['ok']in('0','1')and o['inputs_unchanged']in('0','1')
        assert bool(int(o['ok']))==e['ok'],e['id']
        assert bool(int(o['inputs_unchanged']))==e['inputs_unchanged'],e['id']
    return rows
if __name__=='__main__':
    native=assess(p/'native/observe.stdout.txt')
    result={'outcome':'passed','native_rows':len(native)}
    if len(sys.argv)>1 and sys.argv[1]=='--both':
        wasm=assess(p/'wasm/observe.stdout.txt');assert native==wasm
        result.update(wasm_rows=len(wasm),exact_status_parity=True)
    print(json.dumps(result,indent=2))
