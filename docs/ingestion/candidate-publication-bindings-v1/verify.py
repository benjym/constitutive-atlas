"""Verify the retained publication addition without builds or material calls."""
from pathlib import Path
from contextlib import closing
import hashlib,json,sqlite3,sys,tempfile
p=Path(__file__).resolve().parent;root=p.parents[2];sys.path.insert(0,str(root))
from atlas.evidence import checked_receipt
from atlas.research import export_database,load_publications
from tools.build_publications import bundle
sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
read=lambda f:json.loads(f.read_text())
manifest=read(p/'manifest.json');doc=(p/'manifest.json').relative_to(root).as_posix()
for name,h in manifest['files'].items():assert sha(p/name)==h,name
for name,h in manifest['dependencies'].items():assert sha(checked_receipt(root,doc,name,h))==h,name
plan=read(p/'archive-plan.json')
for name,h in plan['original_bytes'].items():assert sha(checked_receipt(root,(p/'archive-plan.json').relative_to(root).as_posix(),name,h))==h,name
for ref in plan['references']:assert sha(checked_receipt(root,ref['document'],ref['original_path'],ref['sha256']))==ref['sha256']
original=read(root/'catalogue/source-snapshots'/plan['original_bytes']['catalogue/publications.json']/'catalogue/publications.json')
graph=read(checked_receipt(root,doc,'catalogue/publications.json',manifest['dependencies']['catalogue/publications.json']))
assert graph['publications'][:len(original['publications'])]==original['publications']
assert graph['relations']==original['relations'] and len(graph['relations'])==8
assert len(graph['publications'])==26 and sum(len(n['model_ids']) for n in graph['publications'])==16
nodes={n['doi']:n for n in graph['publications']};records=read(p/'source-receipts.json')['records'];assert len(records)==9
for r in records:
    f=root/r['path'];assert sha(f)==r['sha256'] and f.stat().st_size==r['bytes']
    m=read(f)['message'];n=nodes[r['doi']]
    assert n['doi']==m['DOI'].lower() and n['title']==m['title'][0]
    assert n['authors']==[(a.get('given','')+' '+a['family']).strip() for a in m['author']]
    assert n['model_ids']==[r['model_id']]
    assert n['publication_date_parts']==m['published-print']['date-parts'][0]
    assert n['evidence'][0]['path']==r['path'] and n['evidence'][0]['sha256']==r['sha256']
for name,h in manifest['model_bytes_at_baseline'].items():
    assert sha(root/name)==h,name
# Current exporter/package consume canonical data. This is an execution check of
# provenance transport, not equation validation or future graph-size restriction.
current=load_publications();current_nodes={n['id']:n for n in current['publications']}
for r in records:assert current_nodes['doi:'+r['doi']]==nodes[r['doi']]
with tempfile.TemporaryDirectory() as folder:
    d=Path(folder);export_database(d/'atlas.sqlite')
    with closing(sqlite3.connect(d/'atlas.sqlite')) as db:
        assert db.execute('PRAGMA foreign_key_check').fetchall()==[]
        for r in records:
            ident='doi:'+r['doi'];data=db.execute('SELECT record_json FROM publications WHERE id=?',(ident,)).fetchone();assert json.loads(data[0])==nodes[r['doi']]
            assert db.execute('SELECT model_id FROM publication_models WHERE publication_id=?',(ident,)).fetchall()==[(r['model_id'],)]
    bundle(d/'constitutive-atlas');assert (d/'constitutive-atlas/publications.json').read_bytes()==(root/'catalogue/publications.json').read_bytes()
print('PASS: nine primary identities/bindings; prior17 nodes/eight edges preserved; all model bytes unchanged; archive receipts, SQLite and static package verified.')
