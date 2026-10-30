"""Package the browser application from the exact native/Wasm model catalogue."""
import json
from pathlib import Path
import shutil
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.compiler import generate

def main():
    dest=ROOT/'web/dist';dest.mkdir(parents=True,exist_ok=True)
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
    shutil.copytree(ROOT/'schemas',dest/'schemas',dirs_exist_ok=True)
    shutil.copytree(ROOT/'models',dest/'models',dirs_exist_ok=True)
    (dest/'.nojekyll').touch()
    print(f'Packaged {dest}')

if __name__=='__main__':main()
