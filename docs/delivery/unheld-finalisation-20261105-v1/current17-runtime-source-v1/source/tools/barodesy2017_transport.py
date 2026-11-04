"""Bind retained opaque transport rows to complete finite-study transcripts."""
import json
from pathlib import Path
from tools import barodesy2017_integration_study as s

def audit(report_path,transport_path=None):
 report=s.read(report_path)
 path=Path(transport_path) if transport_path else Path(report_path).with_suffix('.transport.jsonl')
 rows=[json.loads(x,parse_constant=lambda _:(_ for _ in ()).throw(ValueError('nonfinite JSON')))for x in path.read_text().splitlines()]
 calls=[call for group in report['records']for call in group['calls']]
 for probe in report['failure_probes']:calls.extend([{'request':probe['request'],'response':probe['response']},probe['recovery']])
 s.require(len(rows)==len(calls)+1==466,'transport row coverage')
 desc=rows[0];s.require(desc['request']=={'mode':'describe'},'describe request')
 native=report['backend']=='native'; rawkey='stdout' if native else 'raw'
 s.require(s.digest(json.loads(desc[rawkey]))==s.digest(report['runtime_descriptor']),'raw descriptor mismatch')
 s.require(desc['backend']==report['backend'] and not desc.get('exception'),'describe backend/status')
 if native:s.require(type(desc['returncode'])is int and desc['returncode']==0 and desc['args'][1:]==['--describe'],'describe native status/args')
 else:s.require(desc['name']=='atlas_describe' and desc['types']==[] and desc['args']==[],'describe Wasm ABI')
 for row,call in zip(rows[1:],calls):
  s.require(s.digest(row['request'])==s.digest(call['request']),'raw request mismatch')
  s.require(s.digest(json.loads(row[rawkey]))==s.digest(call['response']),'raw response mismatch')
  s.require(row['backend']==report['backend'] and not row.get('exception'),'raw backend/status')
  if native:
   s.require(type(row['returncode'])is int and row['returncode']==(0 if call['response']['ok'] else 1),'raw native exit status')
   r=call['request'];s.require(row['args'][1:]==['--mode','integrate','--model',r['model'],'--parameters',s.csv(r['parameters']),'--initial',s.csv(r['initial']),'--strain',s.csv(r['strain']),'--integration-settings',s.csv(r['settings'])],'raw native arguments')
  else:
   s.require(row['name']=='atlas_integrate_with_settings' and row['types']==['string']*5 and len(row['args'])==5,'raw Wasm ABI')
   r=call['request'];s.require(row['args'][0]==r['model'],'raw Wasm model')
   for text,key in zip(row['args'][1:],['parameters','initial','strain','settings']):
    values=[float(v)for v in text.split(',')];s.require(all(s.finite(v)for v in values) and values==r[key],'raw Wasm arguments')
 return {'backend':report['backend'],'raw_rows':len(rows),'all_requests_responses_bound':True}
