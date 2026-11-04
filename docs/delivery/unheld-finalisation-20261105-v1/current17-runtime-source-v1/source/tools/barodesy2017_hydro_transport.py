"""Audit opaque hydro-probe transport independently from numerical acceptance."""
import json
from pathlib import Path
from tools import barodesy2017_hydro_ad as h

def audit(report_path,transport_path=None):
 report=h.rate.read(report_path);native=report['backend']=='native'
 path=Path(transport_path)if transport_path else Path(str(report_path)+'.transport.json')
 t=h.rate.read(path);require=h.rate.require
 require(t.get('version')==h.VERSION+'-transport'and t.get('backend')==report['backend']and t.get('complete')is True and 'error'not in t,'complete transport identity')
 pairs=[(row['request'],row['response'])for row in report['records']]
 for row in report['invalid_records']:pairs.extend([(row['request'],row['response']),(report['records'][0]['request'],row['recovery'])])
 require(len(pairs)==36+2*48,'full hydro transport matrix')
 if native:
  require(t['mode']=='single-process-batch'and type(t['returncode'])is int and t['returncode']==0,'persistent native transport status')
  require(h.rate.exact(t['artifact'],report['artifacts'][0]),'native transport artifact')
  lines=t['request_lines'];raw=t['stdout'].splitlines();require(len(lines)==len(raw)==len(pairs)+1 and lines[0]=='--describe','native transport row count')
  desc=json.loads(raw[0]);records=zip(lines[1:],raw[1:])
 else:
  require(h.rate.exact(t['artifacts'],report['artifacts']),'Wasm transport artifacts')
  calls=t['calls'];require(len(calls)==len(pairs)+1,'Wasm transport row count')
  require(calls[0]['name']=='atlas_describe'and calls[0]['arguments']==[]and not calls[0].get('error'),'Wasm describe ABI')
  desc=json.loads(calls[0]['raw']);records=((call,call['raw'])for call in calls[1:])
 require(desc['sha256']==report['catalogue_hash']and h.rate.exact(desc['models'],[report['model_definition']]),'raw compiled descriptor')
 for (request,answer),(call,raw)in zip(pairs,records):
  if native:
   fields=call.split('\t');require(len(fields)==4,'native request fields')
  else:
   require(call['name']=='atlas_barodesy_hydro_ad'and not call.get('error'),'Wasm function/status');fields=call['arguments'];require(len(fields)==4,'Wasm request fields')
  require(fields[0]==request['model'],'raw model argument')
  for text,key in zip(fields[1:],('parameters','state','increment')):
   values=[float(x)for x in text.split(',')]
   require(all(h.rate.numeric(x)for x in values)and h.rate.exact(values,request[key]),'raw argument:'+key)
  parsed=json.loads(raw,parse_constant=lambda _:(_ for _ in()).throw(ValueError('nonfinite raw response')))
  require(h.rate.exact(parsed,answer),'raw response differs from report')
 return {'backend':report['backend'],'raw_calls':len(pairs)+1,'all_arguments_responses_bound':True,'persistent_instance':True}
