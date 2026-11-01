from pathlib import Path
import json,hashlib,subprocess
R=Path(__file__).resolve().parents[4];P=R/'docs/reviews/chart-axis-labels-v1';O=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest();read=lambda p:json.loads(Path(p).read_text())
for p,h in read(O/'inputs.json').items():assert sha(R/p)==h,p
r=subprocess.run(['python3','-B',str(P/'check_saved.py')],cwd=R,text=True,capture_output=True);assert r.returncode==0,r.stderr
samples=read(P/'saved-points.json');counts={}
for p,h in read(P/'saved-inputs.json').items():
 original=read(R/p);k=Path(p).stem;assert samples[k]==original['result']['points'];counts[k]=len(samples[k])
a=(P/'prior-app.js').read_text();b=(P/'candidate-app.js').read_text()
old="function numberLabel(v){if(Math.abs(v)<1e-10)return '0';return Number(v.toPrecision(3)).toString();}"
new="function numberLabel(v){if(v===0)return '0';const rounded=Number(v.toPrecision(3)),label=rounded.toString();return label.length<=7?label:rounded.toExponential(2).replace(/\\.?0+(?=e)/,'');}"
assert old in a
# Exact isolated source changes: formatter, class attachment and horizontal margins only.
assert b==a.replace(old,new).replace("const svg=$(id);svg.replaceChildren();", "const svg=$(id);svg.classList.add('atlas-chart');svg.replaceChildren();").replace('const left=62,top=27,w=392,h=211','const left=82,top=27,w=354,h=211')
css=(P/'prior-style.css').read_text();assert(P/'candidate-style.css').read_text().startswith(css)
js="""import fs from 'node:fs';import vm from 'node:vm';import assert from 'node:assert/strict';const p=process.argv[1];const get=n=>vm.runInNewContext(fs.readFileSync(p+'/'+n+'-chart.js','utf8')+';numberLabel');const a=get('prior'),b=get('candidate');for(const v of [Number.MAX_VALUE,-Number.MAX_VALUE])assert.equal(a(v),b(v));for(const v of [Number.MIN_VALUE,-Number.MIN_VALUE]){assert.equal(Math.sign(Number(b(v))),Math.sign(v));assert.notEqual(Number(b(v)),0);}console.log(JSON.stringify({inherited_max_finite_rounding_overflow:true,subnormal_sign_retained:true}));"""
z=subprocess.run(['node','--input-type=module','-e',js,str(P)],text=True,capture_output=True);assert z.returncode==0,z.stderr
print(json.dumps({'passed':True,'saved_parent_checks':json.loads(r.stdout),'full_saved_points_equal_original_exports':counts,'exact_app_delta_only_formatter_class_margins':True,'prior_stylesheet_preserved_as_prefix':True,'boundary_probe':json.loads(z.stdout),'reviewer_builds':0,'reviewer_compiled_calls':0,'reviewer_browser_actions':0},indent=2))
