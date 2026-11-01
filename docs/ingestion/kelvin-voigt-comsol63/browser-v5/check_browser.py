"""Independent analytical and visible-interface checks of saved actual DOM evidence."""
import argparse,json,math
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('evidence',type=Path);p.add_argument('package',type=Path);a=p.parse_args()
read=lambda n:json.loads((a.evidence/n).read_text())
x=read('default-ui.json');assert x['panelVisible'] and x['exportEnabled'] and 'Completed 8 physical seconds' in x['status']
assert x['provenance']==json.loads((a.package/'engine-kelvin-voigt/identity.json').read_text())
assert x['model']=='kelvin-voigt-comsol63-deviatoric-zero-spin-ode'
assert x['profileLink'].endswith('#catalogue/'+x['model'])
c=x['controls'];K,G,tau=json.loads(c['parameters']);eps0=json.loads(c['initial']);D=json.loads(c['initialRates']);assert eps0==[0]*6 and abs(sum(D[:3]))<1e-15 and c['mode']=='creep'
assert len(x['rows'])==11 and all(len(r)==14 for r in x['rows'])
state_error=stress_error=0
for row in x['rows'][1:]:
 t=float(row[0])-float(c['start']);state=[float(v) for v in row[2:8]];stress=[float(v) for v in row[8:14]]
 for i in range(6):
  state_error=max(state_error,abs(state[i]-tau*D[i]*(1-math.exp(-t/tau))))
  stress_error=max(stress_error,abs(stress[i]-2*G*tau*D[i]))
assert state_error<3e-8 and stress_error<1
ys=lambda plot:[float(p.split(',')[1]) for p in plot['points'].split()]
span=lambda vals:max(vals)-min(vals)
assert span(ys(x['plots'][0]))<1e-8 and span(ys(x['plots'][1]))>100
for name in ['profile-desktop.json','profile-mobile.json']:
 q=read(name);assert q['technicalClosed'] and q['bodyScrollWidth']<=q['bodyWidth'];assert q['documentWidth']==q['width']
q=read('profile-desktop.json');assert q['profileFirst']=='model-profile' and len(q['parameterRows'])==4
assert q['parameterRows'][1].endswith('Pa') and q['parameterRows'][2].endswith('Pa') and q['parameterRows'][3].endswith('s')
assert 'all six initial total-strain components' in q['body'] and 'halve every incoming' in q['body']
m=read('laboratory-mobile.json');assert m['width']==m['documentWidth']==390
assert len(m['plots'])==2 and all(0<w<=390 for w in m['plots'])
assert read('related-navigation.json')['heading']=='Maxwell viscoelasticity'
assert read('laboratory-profile-return.json')['technicalClosed']
assert read('technical-details.json')['open'] and any('review.json' in l['href'] for l in read('technical-details.json')['links'])
assert read('console.json')==[]
result={'passed':True,'full_state_stress_comparisons':120,'max_strain_error':state_error,'max_stress_error_Pa':stress_error,'provenance_exact_package':True,'stress_plot_pixel_span':span(ys(x['plots'][0])),'profile_first_technical_closed':True,'mobile_overflow':False,'parameters_and_units_readable':True,'related_navigation_and_lab_profile_links':True,'console_warnings_errors':0}
(a.evidence/'check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
