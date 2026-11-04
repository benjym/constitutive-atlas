import {fetchExperiment} from './experiments.mjs';
const finite=Number.isFinite,hash=value=>typeof value==='string'&&/^[a-f0-9]{64}$/.test(value);
export function replayGap(record){
 if(record?.kind&&record.kind!=='experiment')return 'Source channels or summary only: a material-point loading path and initial effective state have not been established.';
 if(!['drained-triaxial','undrained-triaxial'].includes(record?.protocol))return 'This test needs a reviewed loading and execution contract.';
 const initial=record.initial;
 if(!Array.isArray(initial?.effective_stress)||initial.effective_stress.length!==6||!initial.effective_stress.every(finite))return 'Initial effective stress is unavailable; reported stresses are not assumed to be effective stresses.';
 if(!finite(initial.void_ratio)||initial.void_ratio<=0)return 'Initial void ratio is unavailable.';
 const n=Array.isArray(record.rows)?record.rows.length:record.rows;
 if(!Number.isInteger(n)||n<2||n>5001)return 'Full replay requires 2–5,001 observations; no source observations are discarded.';
 return '';
}
export function validateReplayRecord(record){
 const fail=message=>{throw Error(message);};
 if(record?.version!=='atlas-ensemble-experiment-0.2'||typeof record.id!=='string'||!/^[A-Za-z0-9_-]{1,120}$/.test(record.id))fail('Unsupported ensemble experiment.');
 const gap=replayGap(record);if(gap)fail(gap);
 const c=record.conventions,p=record.provenance,s=record.initial.effective_stress;
 if(c?.stress!=='compression-positive'||c.strain!=='compression-positive'||c.stress_unit!=='Pa'||c.strain_unit!=='1')fail('Experiment conventions differ.');
 if(!hash(record.source_asset_sha256)||!hash(p?.archive_sha256)||!hash(p?.member_sha256))fail('Experiment source identity differs.');
 if(s[0]<=0||s[1]<=0||s[1]!==s[2]||s.slice(3).some(x=>x!==0))fail('Axisymmetric compressive initial effective stress required.');
 if(!Array.isArray(record.rows))fail('Ordered observations required.');
 let previous=-Infinity;
 for(const row of record.rows){
  if(!['axial_strain','radial_effective_stress','q','volumetric_strain'].every(k=>finite(row[k])))fail('Missing finite replay channels.');
  if(record.protocol==='drained-triaxial'&&row.radial_effective_stress<=0)fail('Drained radial effective stress must stay positive.');
  if(record.protocol==='undrained-triaxial'&&!['cell_pressure','pore_pressure','p'].every(k=>finite(row[k])))fail('Undrained comparison channels unavailable.');
  if(row.elapsed_time!==undefined){if(!finite(row.elapsed_time)||row.elapsed_time<previous)fail('Source observations are not in acquisition order.');previous=row.elapsed_time;}
 }
 const first=record.rows[0];
 if(first.radial_effective_stress!==s[1]||Math.abs(first.q-(s[0]-s[1]))>1)fail('Source row zero contradicts initialization.');
 return record;
}
export async function fetchReplayAsset(entry,fetcher=fetch){
 if(!/^(ensemble-experiment\.json|ensemble-tests\/[A-Za-z0-9_-]{1,120}\.json)$/.test(entry?.path)||!hash(entry.sha256)||!Number.isSafeInteger(entry.size_bytes)||entry.size_bytes<1||entry.size_bytes>8*1024*1024)throw Error('Invalid ensemble asset entry.');
 const response=await fetcher('./'+entry.path);if(!response.ok)throw Error('Test loading failed. Select it again to retry.');
 const bytes=await response.arrayBuffer();
 const digest=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)),x=>x.toString(16).padStart(2,'0')).join('');
 if(bytes.byteLength!==entry.size_bytes||digest!==entry.sha256)throw Error('Test checksum differs from the catalogue. Reload a consistent package.');
 return JSON.parse(new TextDecoder().decode(bytes));
}
export async function loadEnsembleCatalogue(fetcher=fetch){
 const responses=await Promise.all([fetcher('./experiments/index.json'),fetcher('./ensemble-tests.json')]);
 if(responses.some(r=>!r.ok))throw Error('Test catalogue unavailable.');
 const [publicIndex,replayIndex]=await Promise.all(responses.map(r=>r.json()));
 if(publicIndex.schema_version!=='0.1'||!Array.isArray(publicIndex.experiments)||replayIndex.version!=='atlas-ensemble-tests-0.1'||!Array.isArray(replayIndex.tests))throw Error('Unsupported test catalogue.');
 const replay=new Map(replayIndex.tests.map(e=>[e.id,e]));
 if(replay.size!==replayIndex.tests.length)throw Error('Duplicate replay test IDs.');
 const entries=publicIndex.experiments.map(e=>({...e,replay:replay.get(e.id)||null}));
 if(new Set(entries.map(e=>e.id)).size!==entries.length||[...replay.keys()].some(id=>!entries.some(e=>e.id===id)))throw Error('Test catalogue identities differ.');
 return entries;
}
export async function fetchEnsembleTest(entry,fetcher=fetch){
 if(!entry.replay)return fetchExperiment(entry,fetcher);
 const record=await fetchReplayAsset(entry.replay,fetcher);
 if(record.id!==entry.id||record.rows.length!==entry.rows)throw Error('Replay test identity differs from selection.');
 return record.version==='atlas-ensemble-experiment-0.2'?validateReplayRecord(record):record;
}
export function filterTests(entries,{search='',protocol='',availability=''}={}){
 const query=search.trim().toLocaleLowerCase();
 return entries.filter(e=>(!protocol||e.protocol===protocol)&&(!availability||(availability==='replay'?!!e.replay:!e.replay))&&(!query||[e.id,e.material,e.protocol].join(' ').toLocaleLowerCase().includes(query)));
}
