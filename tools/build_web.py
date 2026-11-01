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
from build_evidence import bundle as bundle_evidence
from build_benchmark import bundle as bundle_benchmark
from build_development import bundle as bundle_development
from build_applicability import bundle as bundle_applicability
from build_power_creep_web import bundle as bundle_power_creep

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview-experiments', action='store_true', help='Include pending datasets in web/preview for local review only')
    parser.add_argument('--wasm-dir',type=Path,default=ROOT/'build-wasm',help='Verified engine directory containing atlas.js, atlas.wasm and generated/models.json')
    parser.add_argument('--power-creep-wasm-dir',type=Path,help='Qualified dedicated physical-time power-creep engine; defaults to --wasm-dir')
    parser.add_argument('--sls-wasm-dir',type=Path,default=ROOT/'build-sls-wasm',help=argparse.SUPPRESS)
    parser.add_argument('--burgers-wasm-dir',type=Path,default=ROOT/'build-burgers-wasm',help='Dedicated common physical-time Burgers engine')
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
    # Remove retired public pages and their dedicated assets from reused output directories.
    for name in ['publications.html', 'publications.mjs', 'publications.json', 'j2.html', 'sls.html', 'power-creep.html', 'recorded-view.mjs', 'recorded-example.json',
                 'j2-contract.mjs', 'power-creep-contract.mjs', 'j2-delivery.html',
                 'j2-review.html', 'sls-review.html', 'power-creep-review.html',
                 'j2-approval.json', 'sls-approval.json', 'power-creep-approval.json',
                 'j2-agent-review.json', 'sls-agent-review.json', 'power-creep-agent-review.json']:
        (dest/name).unlink(missing_ok=True)
    for name in ['engine-j2', 'engine-sls', 'engine']:
        if (dest/name).is_dir():
            shutil.rmtree(dest/name)
    for name in ['timed-route.mjs','index.html','style.css','app.js','worker.js','experiments.mjs','numerics.mjs','loading.mjs','laboratory-scope.mjs','laboratory-document.mjs','laboratory-view.mjs','laboratory-worker.mjs','recorded.mjs','recorded-scope.mjs','recorded-scope-execution.mjs','recorded-document.mjs','recorded-worker.mjs','catalogue.mjs','state-contract.mjs','laboratory-examples.mjs','laboratory-examples-view.mjs','formulation-view.mjs','applicability-view.mjs']:
        shutil.copyfile(ROOT/'web'/name,dest/name)
    shutil.copyfile(ROOT/'docs/benchmarks/kfs-tmd2-research-range-v1/results/reproduction.png',dest/'tmd2-reproduction.png')
    for name in ['atlas.js','atlas.wasm']:
        shutil.copyfile(args.wasm_dir/name,dest/name)
    shutil.copyfile(generated/'models.json',dest/'models.json')
    subprocess.run(['node',str(ROOT/'tools/build_laboratory_examples.mjs'),str(ROOT),str(dest),str(generated/'models.json')],check=True)
    shutil.copyfile(ROOT/'catalogue/manifest.json',dest/'catalogue.json')
    bundle_applicability(dest)
    bundle_evidence(dest)
    bundle_benchmark(dest)
    bundle_development(dest)
    shutil.copytree(ROOT/'schemas',dest/'schemas',dirs_exist_ok=True)
    shutil.copytree(ROOT/'models',dest/'models',dirs_exist_ok=True)
    experiment_manifest=bundle(dest/'experiments', preview=args.preview_experiments)
    print(f"Prepared {len(experiment_manifest['experiments'])} built-in experiments ({experiment_manifest['release']})")
    bundle_power_creep(dest,args.power_creep_wasm_dir or args.wasm_dir)
    subprocess.run(['node',str(ROOT/'tools/test_power_creep_package.mjs'),str(dest)],check=True)
    from build_burgers_web import bundle as bundle_burgers
    bundle_burgers(dest,args.burgers_wasm_dir)
    subprocess.run(['node',str(ROOT/'tools/test_burgers_package.mjs'),str(dest)],check=True)
    from build_sls_laboratory import bundle as bundle_sls_laboratory
    bundle_sls_laboratory(dest,args.sls_wasm_dir)
    subprocess.run(['node',str(ROOT/'tools/test_sls_laboratory_package.mjs'),str(dest)],check=True)
    (dest/'.nojekyll').touch()
    print(f'Packaged {dest}')

if __name__=='__main__':main()
