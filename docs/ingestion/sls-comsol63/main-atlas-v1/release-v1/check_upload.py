"""Read-only exact CI upload/model/review/source binding verification."""
import argparse,json,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('artifact',type=Path);p.add_argument('revision');p.add_argument('output',type=Path);a=p.parse_args();r=a.artifact;here=Path(__file__).resolve().parents[1];h=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();freeze=json.loads((here/'composed-freeze-v3.json').read_text());rows=[]
for source,expected in freeze['files'].items():
 target=source.removeprefix('web/') if source.startswith('web/') else 'catalogue.json' if source=='catalogue/manifest.json' else None
 if target is not None:assert h(r/target)==expected,(source,target);rows.append(dict(source=source,asset=target,sha256=expected))
manifest=json.loads((r/'engine-sls/package-manifest.json').read_text())
for path,expected in manifest['files'].items():assert h(r/path)==expected,path
identity=json.loads((r/'engine-sls/identity.json').read_text());assert identity['release_revision']==a.revision
assert identity['model']=='sls-comsol63-deviatoric-zero-spin-ode';assert identity['model_sha256']=='eccfeb372810afd81a5e9cddf5d8ac33e2cb5df6921fc88e14e9175c73e50906'
assert identity['catalogue_hash']=='11dd07e8b896a71bdc72ce4ff93aba664916af583c703fd6b8671a0727a6ff6e'
assert identity['review_sha256']=='eda7775348b6b5fbd40cfedf2876d1550505f17c83fdd148b83eb153c2d7582c';assert identity['approval_sha256']=='763c29f59b7156094fd15f9edb73b24b2de70c44e748704c8612a5d42170399b'
metadata=json.loads((r/'models.json').read_text());assert len(metadata['models'])==12;assert not (r/'sls.html').exists()
a.output.write_text(json.dumps(dict(ok=True,revision=a.revision,reviewed_sources=rows,guarded_assets=len(manifest['files']),ordinary_models=len(metadata['models']),identity=identity,standalone_sls_absent=True),indent=2)+'\n');print('PASS exact tested upload: reviewed source, approved model,12ordinary models and12guarded SLS assets.')
