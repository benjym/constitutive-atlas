from pathlib import Path
import json,hashlib,shutil,subprocess,sys,tempfile
repo=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[3]
src=Path(sys.argv[2]).resolve() if len(sys.argv)>2 else repo/'docs/reviews/mc-stored-reference-v1'
out=Path(tempfile.mkdtemp(prefix='mc-reference-coordinator-',dir='/private/tmp'))
packet=out/'packet';shutil.copytree(src,packet)
verified=0
for manifest in ('manifest.json','prospective-freeze.json','derivative-self-check-prospective-freeze.json','pre-generation-source-freeze.json'):
    d=json.loads((packet/manifest).read_text())
    for name,record in d['files'].items():
        b=(packet/name).read_bytes()
        assert hashlib.sha256(b).hexdigest()==record['sha256'],(manifest,name)
        assert len(b)==record['bytes'],(manifest,name)
        verified+=1
assert (packet/'corpus/inputs.json').read_bytes()==(repo/'docs/reviews/mc-stored-input-v1/inputs.json').read_bytes()
for name in ('FORMULAS.md','sources.json','results.json','check_certificates.py'):
    assert (packet/'source'/name).read_bytes()==(repo/'docs/ingestion/mohr-coulomb'/name).read_bytes()
helpers=[repo/'catalogue/investigations/symmetric-spectral-primitive-v1/reference/generate.py']
assert helpers, 'prior spectral helper missing'
assert any(p.read_bytes()==(packet/'spectral_source.py').read_bytes() for p in helpers)
replay=out/'replay';replay.mkdir()
steps=[('p280',['generate.py','corpus/inputs.json','280',str(replay/'reference-p280.json.gz')]),('p360',['generate.py','corpus/inputs.json','360',str(replay/'reference-p360.json.gz')]),('precision',['check.py','corpus/inputs.json',str(replay/'reference-p280.json.gz'),str(replay/'reference-p360.json.gz'),'reference-policy.json']),('derivatives',['check_derivatives.py','corpus/inputs.json',str(replay/'reference-p360.json.gz'),'derivative-self-check-policy.json'])]
print(out,flush=True)
for label,args in steps:
    with (out/(label+'.stdout')).open('wb') as stdout,(out/(label+'.stderr')).open('wb') as stderr:
        r=subprocess.run([sys.executable,'-B',*args],cwd=packet,stdout=stdout,stderr=stderr)
    assert r.returncode==0,(label,r.returncode)
    if label in ('p280','p360'):
        name='reference-'+label+'.json.gz'
        assert (replay/name).read_bytes()==(packet/name).read_bytes(),name
    else:
        expected='check-initial.json' if label=='precision' else 'derivative-self-check-results.json'
        assert json.loads((out/(label+'.stdout')).read_text())==json.loads((packet/expected).read_text()),label
    print(label+' exact replay passed',flush=True)
result={'passed':True,'verified_manifest_entries':verified,'source_mirrors_exact':True,'prior_spectral_helper_exact':True,'corpus_exact':True,'both_reference_gzip_files_byte_exact':True,'precision_and_derivative_reports_semantically_exact':True,'candidate_calls':0,'compiled_observations':0}
(out/'results.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result),flush=True)
