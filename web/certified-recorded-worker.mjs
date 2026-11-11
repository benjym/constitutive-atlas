import createAtlas from './engine-certified-return/certified-return.mjs';
import {replayRecorded} from './recorded-worker.mjs';

let ready;
const printErr = line => {
  // The reviewed build emits per-attempt tracing on stderr. Keep other
  // diagnostics visible, including unexpected runtime errors.
  if(!/^local=\d+ fraction=0x[0-9a-f.]+p[+-]\d+ phase=[a-z-]+ outcome=-?\d+ remaining=\d+$/.test(line))
    console.error(line);
};
const normalized = value => Array.isArray(value) ? value.map(normalized)
  : value && typeof value === 'object' ? Object.fromEntries(Object.keys(value).sort().map(key=>[key,normalized(value[key])]))
  : value;
self.onmessage = async ({data}) => {
  try {
    ready ??= Promise.all([createAtlas({printErr}),fetch('./engine-certified-return/recorded.json').then(r=>{
      if(!r.ok)throw Error('Certified example could not load.');
      return r.json();
    })]);
    const [engine,{catalogue,preset}]=await ready;
    if(data.kind!=='recorded'||JSON.stringify(normalized(data.specification))!==JSON.stringify(normalized(preset)))
      throw Error('Only the verified six-component example is supported.');
    const result=replayRecorded(engine,preset,catalogue);
    self.postMessage({id:data.id,result});
  }catch(error){self.postMessage({id:data.id,error:String(error)});}
};
