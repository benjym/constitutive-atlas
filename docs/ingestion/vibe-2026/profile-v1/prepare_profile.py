"""Coordinator mapping of the source-backed public draft; no web installation."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[4]
source=Path('/Users/bmar5496/code/constitutive-atlas/docs/ingestion/vibe-2026/source-v2/public-profile-draft.json')
p=json.loads(source.read_text());m=json.loads((ROOT/'models/research/vibe/vibe-2026-explicit-appendix-a.json').read_text())
p.pop('draftMetadata');p['title']='Viscohypoplastic bentonite (VIBE, Mašín 2026)';p['behaviours']=[[x['title'],x['explanation']] for x in p['behaviours']]
aliases={'lambda':'lambda_ref','N':'Nref','m':'coupling_m','em0':'em_ref','se0':'se_ref','eM0':'eM_ref','a':'thermal_a','b':'thermal_b'}
for f in p['parameters']:
 f['name']=aliases.get(f['name'],f['name']);u=m['parameters'][f['name']]['unit'];f['unit']='rad' if f['name']=='phi' else u if isinstance(u,str) else {'alpha_s':'K⁻¹','Dr':'s⁻¹','thermal_b':'K⁻¹'}[f['name']]
 if f['name']=='phi':f['help']+=' Enter radians: the published 25° example is about 0.436332 rad.'
 if f['name']=='IvT':f['help']='Controls the cubic change in the viscosity factor with temperature relative to 294 K. Setting it to zero keeps the baseline viscosity factor 0.004; it does not remove viscosity.'
for n,symbol,meaning,help in [
 ('Tr','Tr','reference temperature','Reference temperature for the published compression, swelling and viscosity expressions; fixed at 294 K.'),
 ('vf','vf','viscous contribution fraction','Default 0.1 enables stress relaxation. The published special case 0 removes the explicit viscous term; intermediate values are numerical sensitivity studies.'),
 ('pr','pr','reference pressure','Fixed at 1000 Pa. Changing pressure units or the compression intercept without the matching reference changes the material.'),
 ('Oc','Oc','reference overconsolidation constant','Fixed source constant 1.4 in the asymptotic-state shape expression.'),
 ('xi','ξ','direction-shape exponent','Fixed source constant 0.2 governing the approach to the asymptotic strain direction.'),
 ('frm','frm','internal swelling reduction factor','Fixed source factor 0.5 reducing internal swelling/shrinkage effects.'),
 ('alpha_f','αf','overconsolidation exponent','Fixed source exponent 1 in the constitutive interpolation factors.'),
 ('one_kelvin','1 K','temperature normalization','Fixed 1 K unit conversion makes the printed empirical viscosity coefficient explicit in SI; it is not a material fitting parameter.')]:
 u=m['parameters'][n]['unit'];p['parameters'].append(dict(name=n,symbol=symbol,meaning=meaning,help=help,unit=u))
p['parameterNote']='The published BCV material values are illustrative defaults. Several source constants are fixed; vf also admits its published rate-independent special case. Editable intervals are bounds for numerical studies, not experimental confidence ranges. Fit compression, retention, swelling and thermal parameters together for a particular material.'
p['stateLabels']={'sigma_net':'Initial net Cauchy stress','e':'Global void ratio','a_scan':'Hydraulic scanning memory'}
p['preparation']='Enter all six initial net-stress components, global void ratio, hydraulic scanning memory, suction, absolute temperature and incoming imposed rates. Micro- and macrovoid ratios and saturation are calculated from that complete context. Memory 0 is the wetting branch, 1 the drying branch and intermediate values describe scanning. The default relaxation example uses e = 0.725, memory 0.35, suction 10 MPa and 294 K, with isotropic net pressure about 5.116 MPa chosen near the asymptotic state boundary. This is a numerical starting state, not a reconstructed specimen history.'
p['scope']='The selected formulation is the complete published explicit Appendix A law, with physical seconds and prescribed mechanical strain, suction and temperature histories. Stress is net Cauchy stress: total stress minus pore-air pressure times the identity in the compression-positive convention. The interface uses infinitesimal Mandel strain, fixed spatial axes and zero spin, within and on the asymptotic state boundary (OA ≥ 1).'
p['limits']='Strictly positive suction and admissible positive micro- and macrostructure pressures, void ratios and viscosity are required. A saturated starting point is excluded by the hydraulic-memory boundary. Examples cover bounded relaxation, heating/drying, hydraulic reversal and small fixed-direction mixed mechanical loading and reversal. Arbitrarily rotating load paths, finite rotations, coupled heat/water transport and a general finite-element tangent are outside this support. Numerical checks do not calibrate a particular bentonite or validate experiments.'
p['explorationTitle']='Explore relaxation and hydraulic memory';p['exploration']='Start with the 1000-second near-boundary relaxation example and compare it with the one-hour hold and the dry-state hold. Then use drying followed by wetting to see the evolving scanning memory. The combined examples add heating or small six-component mechanical loading. Keep the complete starting state when comparing histories.'
p['comparison']='The curves show calculated model responses. No experimental overlay or material calibration is supplied.'
p['equationIntro']='Eight persistent components evolve: six net stresses, global void ratio and hydraulic scanning memory. Other pore-structure quantities are computed from the current context.'
p['equations']=[['Global void ratio','ė = −(1 + e) tr(D), with compression-positive infinitesimal strain rate D.'],['Combined saturation','Sr = SM + (em/e)(1 − SM).']]
p['equationNote']='The explicit Appendix A formulation uses separate absolute hydraulic and thermal contributions. The combined absolute-value expression in the main text differs for opposing contributions; these are not treated as equivalent. Tensor identities missing from printed A7 and A9 are uniquely completed using the main-text derivation.'
p['references'][0]['label']='Mašín (2026), Viscohypoplastic bentonite (VIBE) model, Engineering Geology 370, 108827'
p['contentSources']+=['models/research/vibe/vibe-2026-explicit-appendix-a.json','docs/ingestion/vibe-2026/public-examples-v1/examples.json','docs/ingestion/vibe-2026/profile-v1/provenance.json']
assert set(f['name'] for f in p['parameters'])==set(m['parameters'])
(Path(__file__).parent/'profile-data.json').write_text(json.dumps(p,indent=2,ensure_ascii=False)+'\n')
