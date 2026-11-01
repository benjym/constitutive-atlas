"""Independent saved DOM audit; no browser or production imports."""
from pathlib import Path
import json,math,urllib.parse,hashlib
B=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/release-source/docs/ingestion/kelvin-voigt-comsol63/browser-v5');P=Path('/private/tmp/atlas-kelvin-voigt-delivery-v1/package-v7');O=Path(__file__).parent/'browser-v5-independent-check-v1.json';assert not O.exists()
read=lambda n:json.loads((B/n).read_text())
x=read('default-ui.json');assert x['provenance']==json.loads((P/'engine-kelvin-voigt/identity.json').read_text());assert x['panelVisible'] and x['exportEnabled'];assert len(x['rows'])==11
c=x['controls'];assert c['mode']=='creep';K,G,tau=json.loads(c['parameters']);D=json.loads(c['initialRates']);assert json.loads(c['initial'])==[0]*6 and abs(sum(D[:3]))<1e-15
me=ms=0
for row in x['rows'][1:]:
 assert len(row)==14;t=float(row[0])-float(c['start']);e=[tau*v*(-math.expm1(-t/tau)) for v in D];s=[2*G*tau*v for v in D];me=max(me,max(abs(float(v)-r)for v,r in zip(row[2:8],e)));ms=max(ms,max(abs(float(v)-r)for v,r in zip(row[8:14],s)))
assert me<3e-8 and ms<1
ys=lambda p:[float(q.split(',')[1])for q in p['points'].split()]
span=lambda a:max(a)-min(a)
assert span(ys(x['plots'][0]))<1e-8 and span(ys(x['plots'][1]))>100
for name in ['profile-desktop.json','profile-mobile.json']:
 d=read(name);assert d['technicalClosed'] and d['bodyScrollWidth']<=d['bodyWidth'] and d['documentWidth']==d['width']
d=read('profile-desktop.json');assert d['profileFirst']=='model-profile' and len(d['parameterRows'])==4
assert [row.split('\t')[-1] for row in d['parameterRows'][1:]]==['Pa','Pa','s'];assert 'all six initial total-strain components' in d['body'] and 'halve every incoming' in d['body']
assert read('related-navigation.json')['heading']=='Maxwell viscoelasticity';assert read('laboratory-profile-return.json')['technicalClosed'];assert x['profileLink'].endswith('#catalogue/'+x['model'])
links=d['links']+read('technical-details.json')['links'];assert read('technical-details.json')['open']
for l in links:
 u=urllib.parse.urlparse(l['href'])
 if u.hostname in ['127.0.0.1','localhost']:assert (P/u.path.lstrip('/')).is_file(),l
m=read('laboratory-mobile.json');assert m['width']==m['documentWidth']==390 and len(m['plots'])==2 and all(0<v<=390 for v in m['plots']);assert read('console.json')==[]
result=dict(identity='independent-normal-v7-browser-v5-saved-audit-v1',passed=True,comparisons=120,max_strain_error=me,max_stress_error_Pa=ms,exact_provenance=True,stress_plot_pixel_span=span(ys(x['plots'][0])),profile_first_technical_closed=True,mobile_no_overflow=True,units=['Pa','Pa','s'],linked_local_files_checked=len(links),browser_or_compiled_calls=0)
O.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
