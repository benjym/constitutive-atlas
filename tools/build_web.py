"""Package the browser application from the exact native/Wasm model catalogue."""
import argparse
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate
from build_experiments import bundle
from build_publications import bundle as bundle_publications

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--preview-experiments', action='store_true', help='Include pending datasets in web/preview for local review only')
    args=parser.parse_args()
    dest=ROOT/('web/preview' if args.preview_experiments else 'web/dist');dest.mkdir(parents=True,exist_ok=True)
    generated=ROOT/'build-wasm/generated'
    # CMake owns code generation; do not silently create a mismatched catalogue.
    if not (generated/'models.json').exists():raise SystemExit('Build the Emscripten target first.')
    import tempfile
    with tempfile.TemporaryDirectory() as check:
        generate(check)
        if (Path(check)/'models.json').read_bytes() != (generated/'models.json').read_bytes():
            raise SystemExit('Wasm catalogue is stale: rebuild before packaging.')
    for name in ['index.html','style.css','app.js','worker.js','experiments.mjs']:
        shutil.copyfile(ROOT/'web'/name,dest/name)
    for name in ['atlas.js','atlas.wasm']:
        shutil.copyfile(ROOT/'build-wasm'/name,dest/name)
    shutil.copyfile(generated/'models.json',dest/'models.json')
    shutil.copyfile(ROOT/'catalogue/manifest.json',dest/'catalogue.json')
    bundle_publications(dest)
    shutil.copytree(ROOT/'schemas',dest/'schemas',dirs_exist_ok=True)
    shutil.copytree(ROOT/'models',dest/'models',dirs_exist_ok=True)
    experiment_manifest=bundle(dest/'experiments', preview=args.preview_experiments)
    print(f"Prepared {len(experiment_manifest['experiments'])} built-in experiments ({experiment_manifest['release']})")
    (dest/'.nojekyll').touch()
    print(f'Packaged {dest}')

if __name__=='__main__':main()
