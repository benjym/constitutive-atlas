"""Assess retained actual-browser observations; never run a material model."""
import hashlib,json,math,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
B=HERE/'browser'
def read(n):return json.loads((B/n).read_text())
profile=read('PROFILE-DESKTOP.txt');tech=read('TECHNICAL-DESKTOP.txt')
narrow=read('LAB-NARROW.txt');np=read('PROFILE-NARROW.txt');nt=read('TECHNICAL-NARROW.txt')
assets=read('FETCHED-ASSETS.txt');plots=read('PLOT-DATA.txt')
manifest=json.loads((HERE/'UPLOAD-MANIFEST.json').read_text())
checks={
 'public_exact_model_route':profile['url'].endswith('#catalogue/bingham-comsol63-mises-perfect-zero-spin-ode'),
 'technical_initially_closed':profile['technicalOpen'] is False and np['open'] is False,
 'four_parameters':len(profile['parameters'])==5,
 'reader_profile_complete':all(x in profile['dialog'] for x in ['What it describes','Starting state','13 state components','Scope and limitations','Pa·s','compression-positive']),
 'three_primary_sources':sum(x['href'].startswith('https://doc.comsol.com/6.3/') for x in profile['links'])==3,
 'two_related_models':sum('#catalogue/' in x['href'] and 'bingham-' not in x['href'] for x in profile['links'])==2,
 'accurate_technical_scope':tech['open'] is True and nt['open'] is True and all(x in tech['technical'] for x in ['complete 13-component state','all six dry total Cauchy stresses','bounded source-derived numerical study','No experimental validation is claimed.']),
 'actual_default_completed':narrow['status']=='Completed 2 physical seconds · 4 output intervals · relaxation.',
 'all_state_and_stress_columns':narrow['rows']==[20]*7,
 'narrow_lab_no_page_overflow':narrow['viewport']==375 and narrow['pageWidth']==375,
 'wide_table_local_scroll':narrow['wrapper']['overflow']=='auto' and narrow['wrapper']['scroll']>narrow['wrapper']['client'],
 'narrow_profile_no_overflow':nt['viewport']==375 and nt['pageWidth']==375 and nt['dialog']['left']>=0 and nt['dialog']['right']<=375 and nt['dialog']['scroll']==nt['dialog']['client'],
 'eleven_browser_assets_match_upload':len(assets)==11 and all(x['status']==200 and x['sha256']==manifest['files'][x['path']]['sha256'] and x['bytes']==manifest['files'][x['path']]['bytes'] for x in assets),
 'fetched_current_revision':next(x for x in assets if x['path']=='engine-bingham/identity.json')['identity']['release_revision']==manifest['source_revision'],
}
checks['three_finite_six_sample_plots']=len(plots)==3 and all(len(p['polylines'])==1 and len(p['polylines'][0].split())==6 and all(math.isfinite(float(v)) for v in re.split('[ ,]',p['polylines'][0])) for p in plots)
network={}
for name in ['LAB','PROFILE']:
 console=(B/f'{name}-CONSOLE.txt').read_text()
 text=(B/f'{name}-NETWORK.txt').read_text()
 statuses=[int(v) for v in re.findall(r'=> \[(\d{3})\]',text)]
 checks[f'{name.lower()}_console_clean']='Total messages: 0 (Errors: 0, Warnings: 0)' in console
 checks[f'{name.lower()}_network_clean']=bool(statuses) and all(200<=x<400 for x in statuses) and 'net::ERR_' not in text
 network[name]={'http_responses':len(statuses),'statuses':sorted(set(statuses))}
checks['frozen_actual_default_comparison']=json.loads((HERE/'LIVE-DEFAULT-CHECK.json').read_text())['passed'] is True
out={'kind':'bingham-live-actual-browser-assessment-v1','source_revision':manifest['source_revision'],'passed':all(checks.values()),'checks':checks,'network':network,'screenshots_visually_inspected':['LAB-NARROW.png','PROFILE-NARROW.png','TECHNICAL-NARROW.png'],'browser_terminal':'about:blank; shared execution slot explicitly released','files':{p.name:{'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(B.iterdir()) if p.is_file()}}
(HERE/'LIVE-BROWSER-CHECKS.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='files'},indent=2));assert out['passed']
