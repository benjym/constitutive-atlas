"""Package the browser application from the exact native/Wasm model catalogue."""
import argparse
import json
from pathlib import Path
import shutil
import sys
import subprocess
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from build_experiments import bundle
from build_publications import bundle as bundle_publications
from build_evidence import bundle as bundle_evidence
from build_benchmark import bundle as bundle_benchmark
from build_development import bundle as bundle_development
from build_applicability import bundle as bundle_applicability

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview-experiments', action='store_true', help='Include pending datasets in web/preview for local review only')
    parser.add_argument('--wasm-dir',type=Path,default=ROOT/'build-wasm',help='Verified engine directory containing atlas.js, atlas.wasm and generated/models.json')
    parser.add_argument('--output',type=Path,help='Explicit local output directory')
    args=parser.parse_args()
    dest=args.output or ROOT/('web/preview' if args.preview_experiments else 'web/dist');dest.mkdir(parents=True,exist_ok=True)
    generated=args.wasm_dir/'generated'
    # Do not package an engine alongside a stale generated model catalogue.
    if not (generated/'models.json').exists():raise SystemExit('Build the Emscripten target first.')
    import tempfile
    with tempfile.TemporaryDirectory() as check:
        generate(check)
        if (Path(check)/'models.json').read_bytes() != (generated/'models.json').read_bytes():
            raise SystemExit('Wasm catalogue is stale: rebuild before packaging.')
    for name in ['index.html','style.css','app.js','worker.js','experiments.mjs','numerics.mjs','loading.mjs','laboratory-scope.mjs','laboratory-document.mjs','laboratory-view.mjs','laboratory-worker.mjs','recorded.mjs','recorded-scope.mjs','recorded-scope-execution.mjs','recorded-document.mjs','recorded-worker.mjs','recorded-view.mjs','catalogue.mjs','state-contract.mjs','laboratory-examples.mjs','laboratory-examples-view.mjs','formulation-view.mjs','applicability-view.mjs']:
        shutil.copyfile(ROOT/'web'/name,dest/name)
    shutil.copyfile(ROOT/'docs/benchmarks/kfs-tmd2-research-range-v1/results/reproduction.png',dest/'tmd2-reproduction.png')
    shutil.copyfile(ROOT/'protocols/recorded-linear-elastic-run.json',dest/'recorded-example.json')
    for name in ['atlas.js','atlas.wasm']:
        shutil.copyfile(args.wasm_dir/name,dest/name)
    shutil.copyfile(generated/'models.json',dest/'models.json')
    subprocess.run(['node',str(ROOT/'tools/build_laboratory_examples.mjs'),str(ROOT),str(dest),str(generated/'models.json')],check=True)
    shutil.copyfile(ROOT/'catalogue/manifest.json',dest/'catalogue.json')
    bundle_applicability(dest)
    bundle_publications(dest)
    bundle_evidence(dest)
    bundle_benchmark(dest)
    bundle_development(dest)
    shutil.copytree(ROOT/'schemas',dest/'schemas',dirs_exist_ok=True)
    shutil.copytree(ROOT/'models',dest/'models',dirs_exist_ok=True)
    experiment_manifest=bundle(dest/'experiments', preview=args.preview_experiments)
    print(f"Prepared {len(experiment_manifest['experiments'])} built-in experiments ({experiment_manifest['release']})")
    (dest/'.nojekyll').touch()
    print(f'Packaged {dest}')

if __name__=='__main__':main()
