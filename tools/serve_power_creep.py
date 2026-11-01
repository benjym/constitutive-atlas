"""Serve the isolated power-creep research demo on loopback; never publishes.

Build atlas_power_creep_solver with Emscripten first. No automatic compilation.
Only the demo page and explicitly named engine files are served.
"""
import argparse
import hashlib
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODEL_ID = 'power-creep-itasca900-both-active-ode'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--build', type=Path, required=True, help='Directory containing power-creep.js and power-creep.wasm')
    parser.add_argument('--catalogue', type=Path, help='Matching generated models.json; defaults to BUILD/power-creep-generated/models.json')
    parser.add_argument('--port', type=int, default=8768)
    args = parser.parse_args()
    build = args.build.resolve()
    catalogue_path = args.catalogue or build/'power-creep-generated/models.json'
    catalogue = json.loads(catalogue_path.read_text())
    current_path = ROOT/'models/research/power-creep'/f'{MODEL_ID}.json'
    current = json.loads(current_path.read_text())
    if catalogue['models'] != [current]:
        raise ValueError('Generated catalogue does not match the current isolated model; rebuild before serving.')
    files = {'/': (ROOT/'web/power-creep.html', 'text/html; charset=utf-8'),
             '/engine/power-creep.js': (build/'power-creep.js', 'text/javascript'),
             '/engine/power-creep.wasm': (build/'power-creep.wasm', 'application/wasm')}
    for path, _ in files.values():
        if not path.is_file():raise FileNotFoundError(path)
    sha = lambda path: hashlib.sha256(path.read_bytes()).hexdigest()
    identity = json.dumps({'model':MODEL_ID, 'catalogue_hash':catalogue['sha256'],
                           'model_sha256':sha(current_path), 'module_sha256':sha(build/'power-creep.js'),
                           'wasm_sha256':sha(build/'power-creep.wasm')}).encode()

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/engine/identity.json':
                data, mime = identity, 'application/json'
            elif self.path in files:
                path, mime = files[self.path]
                data = path.read_bytes()
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header('Content-Type',mime)
            self.send_header('Content-Length',str(len(data)))
            self.send_header('Cache-Control','no-store')
            self.end_headers()
            self.wfile.write(data)

    server = ThreadingHTTPServer(('127.0.0.1', args.port), Handler)
    print(f'Power-creep draft: http://127.0.0.1:{args.port}/', flush=True)
    server.serve_forever()


if __name__ == '__main__':main()
