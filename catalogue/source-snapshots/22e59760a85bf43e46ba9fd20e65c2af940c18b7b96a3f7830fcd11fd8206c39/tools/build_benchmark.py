"""Package the read-only TMD2 benchmark snapshot, without measurements or execution."""
import argparse
import hashlib
from html import escape
import io
import json
from pathlib import Path
import shutil
import tarfile

ROOT = Path(__file__).resolve().parents[1]
PACKET = Path('docs/benchmarks/kfs-tmd2-research-range-v1')
FILES = {
    'parameters.json': 'inputs/parameter-set.json',
    'protocol.json': 'inputs/protocol.json',
    'requests.json': 'inputs/requests.json',
    'summary.json': 'results/summary.json',
    'reproduction.png': 'results/reproduction.png',
}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def bundle(destination, root=ROOT):
    root, destination = Path(root), Path(destination)
    packet = root / PACKET
    pins = json.loads((packet / 'packet-manifest.json').read_text())

    def checked(name):
        data = (packet / name).read_bytes()
        if digest(data) != pins[name]:
            raise ValueError(f'TMD2 snapshot hash mismatch: {name}')
        return data

    # Explicit allowlist: case.json includes private measured first-row values.
    # Neither that record nor arbitrary packet siblings are public assets.
    assets = {name: checked(source) for name, source in FILES.items()}
    source_pins = json.loads(checked('source-manifest.json'))
    case = json.loads(checked('inputs/case.json'))
    with tarfile.open(fileobj=io.BytesIO(checked('source.tar.gz')), mode='r:gz') as archive:
        member = archive.getmember('source/models/hypoplastic-sand-igs97.json')
        if not member.isfile():
            raise ValueError('TMD2 model archive member must be a regular file')
        model_bytes = archive.extractfile(member).read()
    model_hash = digest(model_bytes)
    if model_hash != source_pins['models/hypoplastic-sand-igs97.json'] or model_hash != case['definition_sha256']:
        raise ValueError('TMD2 archived model identity mismatch')
    assets['model.json'] = model_bytes
    model = json.loads(model_bytes)
    params = json.loads(assets['parameters.json'])
    requests = json.loads(assets['requests.json'])
    # This page names the exact frozen benchmark, never the live catalogue defaults.
    names = list(model['parameters'])
    for request in requests:
        if request['parameters'] != [params['parameters'][name] for name in names] or request['initial'] != case['initial']['flat_state']:
            raise ValueError('TMD2 request/input binding mismatch')

    def code(value):
        return '<code>' + escape(str(value)) + '</code>'

    rows = ''.join('<tr><th scope="row">' + escape(name) + '</th><td>' + code(params['parameters'][name]) + '</td><td>' + escape(model['parameters'][name]['unit']) + '</td></tr>' for name in names)
    initial = escape(json.dumps(case['initial']['named_state'], indent=2))
    settings = escape(json.dumps(requests[0]['integration_settings'], indent=2))
    downloads = ''.join(f'<li><a href="./benchmark-tmd2/{name}">{escape(name)}</a> — SHA-256 {code(digest(data))}</li>' for name, data in assets.items())
    page = f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>TMD2 benchmark snapshot · Constitutive Atlas</title><link rel="stylesheet" href="./style.css">
<style>main{{margin:0 auto;max-width:1100px}}table{{border-collapse:collapse}}th,td{{padding:.4rem 1rem;text-align:left;border-bottom:1px solid #ddd}}pre{{overflow:auto}}code{{overflow-wrap:anywhere}}li{{margin:.6rem 0}}img{{max-width:100%;height:auto}}</style></head>
<body><main><header class="topbar"><a href="./index.html#methods">← Methods &amp; evidence</a></header><section class="page">
<div class="eyebrow">READ-ONLY BENCHMARK SNAPSHOT</div><h1>TMD2: exact calculation inputs.</h1>
<p class="page-lead">A qualified published-model reconstruction. Independent scientific review remains pending.</p>
<p>This archived VW96 + IGS definition and its inputs generated the saved benchmark curves. Laboratory defaults and later catalogue revisions are separate. The snapshot preserves its historical schema; it is not a new v0.3 model record.</p>
<figure><a href="./benchmark-tmd2/reproduction.png"><img src="./benchmark-tmd2/reproduction.png" alt="Atlas paths at 400, 800 and 1600 increments compared with published model curves and frozen precision envelopes"></a><figcaption>Model curves only. Original measurements are not included.</figcaption></figure>
<h2>Formulation and material</h2><p>Karlsruhe fine sand; model definition SHA-256 {code(model_hash)}. Thirteen material constants plus the project stress scale p_ref. Values below use SI units; phi is in radians.</p>
<table><caption>Published-case values, not illustrative defaults</caption><thead><tr><th scope="col">Parameter</th><th scope="col">Value</th><th scope="col">Unit</th></tr></thead><tbody>{rows}</tbody></table>
<h2>Initial state and loading</h2><p>Published nominal initial state, not measured first-row values. Compression-positive stress/strain/history; symmetric tensors use Mandel order xx, yy, zz, √2xy, √2yz, √2xz. Stress is in Pa; void ratio and history strain are dimensionless. The history is initialized directly; no preparation replay is inferred.</p><pre>{initial}</pre>
<p>Drained axisymmetric compression at 100 kPa radial effective stress, zero spin. Three native paths use 400, 800 and 1600 increments from 0 to 0.25 direct accumulated axial strain; volume is the trace of accumulated normal strain. Physical time is not inferred for this rate-independent case. Exact controls and settings are in requests.json.</p>
<details><summary>Project numerical settings</summary><pre>{settings}</pre></details>
<h2>What the result establishes</h2><p>All three paths pass the frozen publication-precision and adjacent-refinement gates. The downloadable summary retains every gate and aggregate experimental error. These are calibration-campaign comparisons, not held-out validation. Historical strain conversion, original-code equivalence, finite-deformation validity and scientific admission remain open. This native research calculation does not extend the interactive laboratory's 10% limit.</p>
<h2>Inspect the snapshot</h2><p>Files are copied from the recorded study after hash checks. Packaging does not rerun or independently verify the constitutive calculation. Original measurements, PDFs and author implementation code are excluded.</p><ul>{downloads}</ul>
<h2>Reproduce locally</h2><p>From a checkout of Constitutive Atlas, choose a fresh writable output directory. Python, CMake, a C++20 compiler and Matplotlib are required. This command downloads original data locally, performs one serial native build and runs the three paths.</p><pre>python3 tools/benchmark_tmd2.py --output /tmp/tmd2-local-reproduction</pre>
<p><a href="https://github.com/benjym/constitutive-atlas/tree/main/docs/benchmarks/kfs-tmd2-portable-v1">Reproduction guide</a> · <a href="https://github.com/benjym/constitutive-atlas/tree/main/docs/benchmarks/kfs-tmd2-appendix-law-v1">Source/input review and unsigned scientific checklist</a></p>
<p><a href="https://doi.org/10.1007/s11440-015-0402-z">Wichtmann &amp; Triantafyllidis (2016), Tables 2–3 and Figure 4</a> · <a href="https://doi.org/10.1016/j.soildyn.2019.05.001">Wichtmann et al. (2019), Table 1 and Figure 3</a></p>
</section></main></body></html>'''
    # Only this owned asset directory is replaced, removing stale previous files.
    target = destination / 'benchmark-tmd2'
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True)
    for name, data in assets.items():
        (target / name).write_bytes(data)
    (destination / 'tmd2.html').write_text(page, encoding='utf-8')
    return {name: digest(data) for name, data in assets.items()}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    bundle(args.output)
