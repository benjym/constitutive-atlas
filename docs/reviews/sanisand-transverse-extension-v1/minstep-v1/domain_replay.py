"""Observe domain margins during the exact saved rejected-trial replay."""
from decimal import Decimal as D
import json
from pathlib import Path
import sys
import replay_failure as replay


def audit(directory):
 original=replay.study.law.rates;records=[]
 def observed(*args,**kwargs):
  value=original(*args,**kwargs)
  if isinstance(value,dict):records.append({key:str(value[key]) for key in ['p','distance','Hbar','denominator','dilatancy']})
  return value
 replay.study.law.rates=observed
 try:result=replay.replay(directory)
 finally:replay.study.law.rates=original
 assert records and all(D(r['p'])>0 and D(r['distance'])>0 and D(r['denominator'])>0 for r in records)
 return {'exact_trial_replay_preserved':result['last_rejected_trial_exactly_reproduced'],'observations':records,'minimum_pressure':str(min(D(r['p']) for r in records)),
         'minimum_distance':str(min(D(r['distance']) for r in records)),'minimum_loading_denominator':str(min(D(r['denominator']) for r in records)),
         'scope':'Observed stages of the single saved rejected trial only; no path-wide singularity exclusion or new integration commits.'}


if __name__=='__main__':print(json.dumps(audit(Path(sys.argv[1])),indent=2))
