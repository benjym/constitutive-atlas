"""Resume exact unmodified standard pipeline after independently reviewed closure repair.

The failed prior output/log remain immutable. Copy their exact partial package to
new site-v7 and execute every remaining production builder operation verbatim.
Earlier guards and their unchanged file identities are retained in the plan;
whole-package support/static/browser checks follow. Remote CI reruns it all.
"""
from pathlib import Path
import hashlib,json,shutil,sys,tempfile,textwrap
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[5];sys.path[:0]=[str(ROOT),str(ROOT/'tools')]
import build_web
HERE=Path(__file__).resolve().parent
prior=Path('/Users/bmar5496/code/constitutive-atlas/.local/barodesy-sand-delivery-v1/site-v6');dest=prior.with_name('site-v7')
source=(ROOT/'tools/build_web.py').read_text();tail=source[source.index('    from build_maxwell_laboratory import bundle as bundle_maxwell'):source.index("\nif __name__=='__main__'")]
files={p.relative_to(prior).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in prior.rglob('*') if p.is_file()}
plan={'standard_builder_sha256':hashlib.sha256(source.encode()).hexdigest(),'prior_partial_site':str(prior),'prior_files':files,'earlier_guards':'Original standard builder v6 ran profile coverage, stale catalogue check, all metadata/data/evidence, Burgers, power-creep, SLS, Kelvin-Voigt, J2 and NorSand guards successfully; retained terminal failure was Maxwell closure. Only new independently approved Maxwell qualification/helper changed, outside earlier stage inputs.','remaining_operations':textwrap.dedent(tail),'scope':'Resume production pipeline verbatim into a new copy, no standard gate removed. Whole-package and actual browser qualification still required.'}
assert not dest.exists();(HERE/'resumed-pipeline-plan.json').write_text(json.dumps(plan,indent=2)+'\n');shutil.copytree(prior,dest)
assert files=={p.relative_to(dest).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in dest.rglob('*') if p.is_file()}
args=SimpleNamespace(maxwell_wasm_dir=ROOT/'.local/barodesy-current-maxwell-v3',implicit_path_wasm_dir=Path('/Users/bmar5496/code/constitutive-atlas/.local/lade-main-atlas-v1/implicit-path'),orthotropic_wasm_dir=Path('/private/tmp/atlas-orthotropic-execution-v1/wasm'),hill_wasm_dir=ROOT/'web/engines/hill')
env=dict(build_web.__dict__,dest=dest,args=args,tempfile=tempfile);exec(compile(textwrap.dedent(tail),'exact_remaining_build_web_operations','exec'),env)
assert (dest/'.nojekyll').is_file()
