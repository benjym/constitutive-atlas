"""Materialize a prospective declarative contract; no material-update execution."""
from pathlib import Path
import json,math,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from atlas.model import validate
P=Path(__file__).parent

def extreme(side,tensor):
 pair='upper' if side=='max' else 'lower'
 return f'select(principal_range_le({tensor},0*p_ref),trace({tensor}/3),select(principal_{side}_repeated({tensor}),principal_{pair}_sum({tensor})/2,principal_{side}({tensor})))'

def main():
 old=json.loads((P.parent/'supplied-original-v2/crosswalk.json').read_text())
 m={'schema_version':'0.3','id':'duncan-chang-1970-endpoint-average','name':'Duncan–Chang1970 constant-nu, project endpoint-average residual (prospective)','family':'nonlinear-elasticity','status':'draft','description':'Original1970 effective-stress constant-nu incremental3D closure; project endpoint-principal average, max-D history and declared10psf numerical failure modulus. Exact-tie lazy spectral expressions select scalar cluster-average branch rows, not a unique classical or proven whole-residual Clarke tangent. No numerical qualification, scientific approval, calibration or finite-rotation claim.','sources':[{'url':'https://doi.org/10.1061/JSFEAQ.0001458','locator':'Original1970 pp1631–1648 Eqs3–15, constant nu1642, average stress1642/1646–47, max-D memory1645; complete retained source receipts under ingestion/duncan-chang-1970/v2/v4','role':'Original complete material law; finite implicit averaging/equality/failure coefficient are disclosed project choices'}],'parameters':{},'state':[],'derived':[],'equations':{},'domain':[],'formulation':old['formulation_proposal'],'initialization':old['initialization_proposal']}
 vals={'p_ref':(100000.,'Pa',0.,sys.float_info.max,'Numerical residual scale'), 'pa':(101325.,'Pa',0.,sys.float_info.max,'Atmospheric reference; explicit SI example'), 'K':(2000.,'1',0.,sys.float_info.max,'Primary modulus number'), 'Kur':(2120.,'1',0.,sys.float_info.max,'Unloading modulus number'), 'n':(.54,'1',-sys.float_info.max,sys.float_info.max,'Stress exponent'), 'Rf':(.91,'1',0.,1.,'Failure ratio'), 'c_cohesion':(0.,'Pa',0.,sys.float_info.max,'Cohesion'), 'phi':(math.radians(36.5),'1',0.,math.pi/2,'Friction angle in radians'), 'nu':(.3,'1',-1.,.5,'Constant Poisson coefficient'), 'E_failure':(10*4.4482216152605/.3048**2,'Pa',0.,sys.float_info.max,'Numerical postfailure modulus; arbitrary source-example coefficient')}
 for k,(v,u,lo,hi,label) in vals.items():m['parameters'][k]={'default':v,'unit':u,'min':lo,'max':hi,'label':label}
 for s,initial in zip(old['state_proposal'],([100000.,100000.,100000.,0.,0.,0.],0.)):
  m['state'].append({k:v for k,v in s.items() if k!='source'}|{'initial':initial,'scale':'p_ref'})
 derived=[('a',extreme('max','sigma')),('least',extreme('min','sigma')),('a_old',extreme('max','sigma_n')),('least_old',extreme('min','sigma_n')),('D','a-least'),('D_old','a_old-least_old'),('cbar','(least+least_old)/2'),('Dbar','(D+D_old)/2'),('F','2*(c_cohesion*cos(phi)+least*sin(phi))/(1-sin(phi))'),('F_old','2*(c_cohesion*cos(phi)+least_old*sin(phi))/(1-sin(phi))'),('Fbar','2*(c_cohesion*cos(phi)+cbar*sin(phi))/(1-sin(phi))'),('Sbar','Dbar/Fbar'),('modulus','select(D<h_n,Kur*pa*(cbar/pa)**n,select(Sbar<1,K*pa*(cbar/pa)**n*(1-Rf*Sbar)**2,E_failure))')]
 m['derived']=[{'name':k,'expr':v} for k,v in derived]
 m['equations']={'sigma':'sigma-sigma_n-modulus/(1+nu)*dev(de)-modulus/(3*(1-2*nu))*trace(de)*I','h':'h-select(D<h_n,h_n,D)'}
 m['domain']=['p_ref>0*p_ref','pa>0*pa','K>0','Kur>=K','Rf>0','Rf<1','c_cohesion>=0*p_ref','phi>=0','phi<1.5707963267948966','nu>-1','nu<0.5','E_failure>0*p_ref','least>0*p_ref','least_old>0*p_ref','cbar>0*p_ref','F>0*p_ref','F_old>0*p_ref','Fbar>0*p_ref','modulus>0*p_ref','h_n>=D_old']
 m['initial_checks']=['h>=D','h>=0*p_ref']
 m['solution_constraints']=['h>=0*p_ref','h>=principal_max_value(sigma)-principal_min_value(sigma)','principal_min_value(sigma)>0*p_ref']
 validate(m)
 (P/'model-contract.json').write_text(json.dumps(m,indent=2,ensure_ascii=False)+'\n')
 print('v0.3 prospective contract validates;7persistent components,10parameters; no material update')
if __name__=='__main__':main()
