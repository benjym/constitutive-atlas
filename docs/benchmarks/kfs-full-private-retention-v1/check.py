"""Destination-only retention audit and adversarial integrity probes."""
import argparse,hashlib,json,runpy,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
    verify=runpy.run_path(str(HERE/'verify.py'))['verify']
    receipt=json.loads((HERE/'receipts.json').read_text());base=ROOT/receipt['private_root']
    # The verifier accepts only the retained root and records; origin paths are deliberately removed.
    records=[{k:v for k,v in r.items() if k!='origin'} for r in receipt['files']]
    result=verify(base,records)
    failures=[]
    with tempfile.TemporaryDirectory(prefix='kfs-retention-probes-') as directory:
        alternate=Path(directory);p=alternate/'retained';p.write_bytes(b'original');p.chmod(0o600)
        item={'retained_path':'retained','bytes':8,'sha256':hashlib.sha256(b'original').hexdigest()}
        assert verify(alternate,[item])=={'files':1,'bytes':8}
        def reject(name,items):
            try:verify(alternate,items)
            except (ValueError,FileNotFoundError):failures.append(name)
            else:raise AssertionError('Mutation accepted: '+name)
        p.write_bytes(b'changed!');reject('same_length_corruption',[item]);p.write_bytes(b'original')
        reject('wrong_length',[{**item,'bytes':7}]);reject('missing_file',[{**item,'retained_path':'missing'}])
        reject('path_traversal',[{**item,'retained_path':'../retained'}]);reject('absolute_path',[{**item,'retained_path':str(p)}])
        reject('duplicate_path',[item,item]);p.chmod(0o700);reject('executable_file',[item]);p.chmod(0o600)
        (alternate/'link').symlink_to(p);reject('symlink_file',[{**item,'retained_path':'link'}])
    assert len(failures)==8
    # Every explicit pinned review input has an exact retained destination.
    origins={r['origin']:r for r in receipt['files']}
    binding=next(r for r in receipt['files'] if r['retained_path']=='governing/private-input-bindings.json')
    b=json.loads((base/binding['retained_path']).read_text());expected=dict(b['root_inputs']);expected.update({s['path']:s['sha256'] for s in b['private_sources']})
    for study in b['study_metadata']:expected.update({str(Path(study['root'])/n):h for n,h in study['metadata_files'].items()})
    assert len(expected)==receipt['explicit_review_bindings']
    for n,h in expected.items():assert origins[n]['sha256']==h,n
    assert (HERE/'inventory-before.json').read_bytes()==(HERE/'receipts.json').read_bytes()
    out={'result':'pass',**result,'explicit_review_bindings':len(expected),'origin_fields_removed_from_verifier_input':True,'negative_probes_rejected':failures,'alternate_root_fixture_passed':True,'before_after_inventory_identical':True,'scientific_or_numerical_requalification':False}
    args.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out))
if __name__=='__main__':main()
