"""Read-only JSON diff and parent report consistency; no Atlas imports."""
import json,argparse
from pathlib import Path

def main(v1,v2):
 v1=Path(v1);v2=Path(v2)
 a=json.loads((v1/'model.json').read_text());b=json.loads((v2/'model.json').read_text());ad={x['name']:x['expr']for x in a['derived']};bd={x['name']:x['expr']for x in b['derived']}
 changes={k:[ad.get(k),bd.get(k)]for k in sorted(ad.keys()|bd.keys())if ad.get(k)!=bd.get(k)}
 assert set(changes)=={'gap12','gap23','gla','gra','class_ga'}
 assert {k for k in a.keys()|b.keys()if k!='derived'and a.get(k)!=b.get(k)}=={'id'}
 old=json.loads((v1/'diagnostic-results.json').read_text());new=json.loads((v2/'check.stdout').read_text())
 assert old['passed']is False and len(old['retained_failed_hold_cases'])==4
 assert new['validated']is True and new['certificate_source_exact']is True and len(new['rows'])==25
 assert all(0<=r['error']<=r['bound']and 0<=r['hold_error']<=r['bound']for r in new['rows'])
 assert len(new['invalid_parameter_rejections'])==9 and new['compiled_observations']==0
 print(json.dumps({'identity':'mc-v1-v2-read-only-source-review-v1','v1_passed':False,'v1_failed_holds':old['retained_failed_hold_cases'],'v2_parent_report_consistent':True,'v2_parent_value_and_hold_rows':len(new['rows']),'v2_parent_invalid_parameters':len(new['invalid_parameter_rejections']),'only_other_json_change':'id','derived_changes':changes,'compiled_observations_by_auditor':0,'atlas_imports_by_auditor':0},indent=2,sort_keys=True))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('v1');p.add_argument('v2');a=p.parse_args();main(a.v1,a.v2)
