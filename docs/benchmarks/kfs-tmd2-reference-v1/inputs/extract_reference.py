"""Extract two selected published model curves; no solver or fit calls."""
import argparse,bisect,hashlib,json,math,re,xml.etree.ElementTree as ET
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--svg',type=Path,required=True);parser.add_argument('--output',type=Path,required=True);args=parser.parse_args()
root=ET.parse(args.svg).getroot();number=r'[-+]?(?:\d*\.\d+|\d+)(?:[eE][-+]?\d+)?'
runs=[];widths=set()
for node in root.iter():
 if node.get('stroke')!='rgb(0%, 0%, 100%)' or node.get('stroke-width')!='5.35603':continue
 assert re.fullmatch(r'[ML\s\d.+eE-]+',node.get('d',''))
 values=list(map(float,re.findall(number,node.get('d'))));t=list(map(float,re.findall(number,node.get('transform',''))))
 assert len(values)==4 and t==[.12,0,0,-.12,0,842]
 a,b,c,d,e,f=t;points=[(a*x+c*y+e,b*x+d*y+f) for x,y in zip(values[::2],values[1::2])]
 if not all(60<x<215 and 450<y<720 for x,y in points):continue
 widths.add(float(node.get('stroke-width'))*.12)
 if runs and max(abs(x-y) for x,y in zip(runs[-1][-1],points[0]))<1e-7:runs[-1].append(points[1])
 else:runs.append(points)
assert len(runs)==6 and all(len(v)==2001 for v in runs) and len(widths)==1
stroke=next(iter(widths));frames={'q':(65.8398438,204.67968744,478.90625,580.48828124),'volumetric_strain':(65.5117188,204.41015628,611.04296876,712.625)}
selected={'q':max(runs[3:],key=lambda p:p[-1][1]),'volumetric_strain':min(runs[:3],key=lambda p:p[-1][1])}
def interpolate(points,x):
 xs=[p[0] for p in points];i=bisect.bisect_right(xs,x)
 if i==0:return points[0][1]
 if i==len(points):return points[-1][1]
 a,b=points[i-1:i+1];return a[1]+(x-a[0])*(b[1]-a[1])/(b[0]-a[0])
channels={}
for channel,points in selected.items():
 left,right,top,bottom=frames[channel]
 assert abs(points[0][0]-left)<1e-7 and abs(points[-1][0]-right)<1e-7
 assert all(a[0]<b[0] for a,b in zip(points,points[1:]))
 physical=[(.25*(x-left)/(right-left),500000*(bottom-y)/(bottom-top) if channel=='q' else .02-.14*(y-top)/(bottom-top)) for x,y in points]
 physical[0]=(0.0,physical[0][1]);physical[-1]=(.25,physical[-1][1])
 dx=2*stroke*.25/(right-left);dy=2*stroke*(500000 if channel=='q' else .14)/(bottom-top)
 rows=[]
 for i in range(101):
  x=.25*i/100;lo=max(0.0,x-dx);hi=min(.25,x+dx)
  ys=[interpolate(physical,lo),interpolate(physical,hi)]+[y for a,y in physical if lo<a<hi]
  rows.append(dict(axial_coordinate=x,value=interpolate(physical,x),lower=min(ys)-dy,upper=max(ys)+dy))
 channels[channel]={'source_chain_index':runs.index(points),'source_vertices':len(points),'source_vertices_sha256':hashlib.sha256(json.dumps(points,separators=(',',':')).encode()).hexdigest(),'frame_pdf_points':list(frames[channel]),'ordinate_units':'Pa' if channel=='q' else '1','horizontal_half_width':dx,'vertical_half_width':dy,'refinement_limit':dy/10,'rows':rows}
report={'id':'kfs-tmd2-2019-vector-reference-v1','source_svg_sha256':hashlib.sha256(args.svg.read_bytes()).hexdigest(),'source':'2019Figure3a,b, blue model curves, loose21% case','method':'Two connected2000-segment model chains; lowest-stress/highest-volume loose curves selected from figure labels and axis regions, before runtime observations. No measured/black curves extracted.','stroke_width_pdf_points':stroke,'bounds_policy':'At each of101uniform0..0.25samples, envelope all source polyline values over x±two full stroke widths; expand y by two full widths. Clip only x window to published domain. Adjacent refinement paths must differ by <=one tenth of the vertical half width.','calibration_note':'Frames are direct black-axis vector coordinates. Volume frames span+2to−12percentage points; source centerline origin differs slightly from exactly zero within the plotted stroke. No translation or source-value adjustment is made.','operational_coordinate':'Source driver cumulative axial strain and trace of accumulated normal strains. Exact historical figure conversion remains unverified; this is an explicitly scoped reconstruction, not historical code equivalence.','channels':channels}
args.output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
print(json.dumps({k:{x:v[x] for x in ['source_chain_index','source_vertices','horizontal_half_width','vertical_half_width','refinement_limit']} for k,v in channels.items()},indent=2))
