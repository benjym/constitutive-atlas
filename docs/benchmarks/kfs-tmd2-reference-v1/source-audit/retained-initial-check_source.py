"""Independent raster spot checks only; never imports Atlas or parent extractor.
Requires private source render: pdftoppm -f 4 -l 4 -r 300 -png SOURCE private/2019-p4
"""
from pathlib import Path
import hashlib,json
from PIL import Image
ROOT=Path(__file__).resolve().parent
PARENT=Path('/private/tmp/atlas-kfs-reference-preparation-v1')
im=Image.open(ROOT/'private/2019-p4-300.png').convert('RGB')
frames={'q':[65.8398438,204.67968744,478.90625,580.48828124], 'volume':[65.5117188,204.41015628,611.04296876,712.625]}
# Source axes visually checked on rendered PDF. Raster uses these calibration
# coordinates, independently selects blue pixel runs, not vector chain identities.
rows=[]
for channel,f in frames.items():
 for pct in [5,10,20]:
  x=round((f[0]+(f[1]-f[0])*pct/25)*300/72)
  runs=[]
  for y in range(round(f[2]*300/72)+2,round(f[3]*300/72)-2):
   r,g,b=im.getpixel((x,y))
   if b>130 and b>r+60 and b>g+35:
    if not runs or y>runs[-1][-1]+1:runs.append([y])
    else:runs[-1].append(y)
  assert len(runs)==3,(channel,pct,runs)
  selected=runs[-1] if channel=='q' else runs[0]
  yp=sum(selected)/len(selected)*72/300
  value=(f[3]-yp)/(f[3]-f[2])*500 if channel=='q' else 2-(yp-f[2])/(f[3]-f[2])*14
  rows.append({'channel':channel,'axial_percent':pct,'raster_x':x,'blue_runs_y':[[a[0],a[-1]] for a in runs], 'selected_center':value,'units':'kPa' if channel=='q' else 'percentage_points','one_pixel_ordinate':(.24/(f[3]-f[2]))*(500 if channel=='q' else 14)})
# Only after independent spot extraction, compare frozen prospective reference.
ref=json.loads((PARENT/'reference.json').read_text())
for r in rows:
 c=ref['channels'][r['channel']]
 row=min(c['rows'],key=lambda x:abs(x['axial_coordinate']-r['axial_percent']/100))
 scale=1000 if r['channel']=='q' else .01
 r['parent_center_in_same_units']=row['value']/scale
 r['difference']=r['selected_center']-row['value']/scale
 # Pixel-center and rounded horizontal sampling; comfortably under two full strokes.
 assert abs(r['difference'])*scale<c['vertical_half_width']
width=5.35603*.12
bounds={}
for ch,f in frames.items():
 bounds[ch]={'stroke_pdf_points':width,'horizontal_half_width_strain':2*width/(f[1]-f[0])*.25,'vertical_half_width':2*width/(f[3]-f[2])*(500000 if ch=='q' else .14)}
 assert abs(bounds[ch]['horizontal_half_width_strain']-ref['channels'][ch]['horizontal_half_width'])<1e-15
 assert abs(bounds[ch]['vertical_half_width']-ref['channels'][ch]['vertical_half_width'])<1e-10
out={'identity':'kfs-tmd2-reference-independent-raster-audit-v1','source_only':True,'spots':rows,'bounds':bounds,'checks_passed':10,'note':'Six independently selected raster spots, two horizontal and two vertical width recalculations. Axis coordinates shared; curve extraction independent. Not independent scientific authorship.'}
(ROOT/'checks.json').write_text(json.dumps(out,indent=2)+'\n')
print('PASS: 6 independent raster spots and 4 bound recalculations')
