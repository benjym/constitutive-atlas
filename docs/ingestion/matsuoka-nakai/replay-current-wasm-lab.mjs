import {readFileSync, writeFileSync} from 'node:fs';
import {gunzipSync} from 'node:zlib';
import {pathToFileURL} from 'node:url';
import {resolve} from 'node:path';
const directory = resolve(process.argv[2]);
const {default: create} = await import(pathToFileURL(resolve(directory, 'wasm/nh2004.mjs')));
const runtime = await create();
const frozen = JSON.parse(gunzipSync(readFileSync('docs/ingestion/matsuoka-nakai/working-v1/laboratory-responses.json.gz')));
const names = ['oedometric','drained','undrained','stress-controlled','isotropic'];
for (const x of frozen) {
 const v = x.integration_settings;
 const settings = [v.residual_tolerance,v.rate_tolerance,v.max_iterations,v.max_depth,v.max_substeps,v.max_backtracks].join(',');
 const raw = runtime.ccall('atlas_run_scope_with_settings','string',['string','string','string','number','number','number','number','string'], [x.model,x.parameters.join(','),x.initial.join(','),x.protocol,x.target,x.steps,x.cycles,settings]);
 writeFileSync(resolve(directory, 'wasm-'+names[x.protocol]+'.json'),raw);
}
