"""Independent Decimal algebraic starting-context check, no constitutive integration."""
from decimal import Decimal as D, localcontext
import json

def check():
 with localcontext() as c:
  c.prec=70
  pnet=D(1000);s=D(100000000);T=Tr=D(294);e=D('0.725');aH=D(0)
  pm=pnet+s;em=D('.55')*(-(D('.9')*(pm/D(150000000)).ln()).exp()).exp()
  eM=(e-em)/(1+em);sen=D(2000000)*D('.2')/eM;se=sen*D('.9')
  S=1-(-(D('1.1')*(se/s).ln()).exp()).exp();Sr=S+em/e*(1-S)
  pM=pnet+S*s;lam=D('.10');pe=D(1000)*((D('1.43')-(1+e).ln())/lam).exp()
  OA=OI=pe/pM; eA=((1+e).ln()+lam*OA.ln()).exp()-1; re=(e-em)/(eA-em);fm=1-re**5
  Dp=-em*D('.9')/pm*(D('.9')*(pm/D(150000000)).ln()).exp()
  Dse=-(1-S)*D('1.1')*(1-S).ln()/se;Demse=-se/eM
  fs=3*pM/2*(lam+D('.02'))/(lam*D('.02'))*(1-2*D('.24'))/(1+D('.24'))
  bB=-Dse*Demse*s*(1+eM)*Dp/(3*(1+em));cB=-fs*fm*Dp/(9*(1+em));dB=D('.24')/(1-2*D('.24'));q=bB+cB+3*cB*dB
  values=locals().copy()
  assert pm>0 and em>0 and eM>0 and S>0 and S<1 and Sr>0 and Sr<1 and OA>1 and eA>em and re>0 and re<1 and fm>0 and 1+3*q>0
  names=['pm','em','eM','sen','se','S','Sr','pM','pe','OI','OA','eA','re','fm','Dp','Dse','fs','bB','cB','q']
  out={k:str(values[k]) for k in names};out['Binverse_denominator']=str(1+3*q)
  return {'status':'pass','identity':'prospective unsaturated hydrostatic initial algebra only; not prepared specimen or model integration','source':'source-v2/parameters.json proposed_explicit_example; AppendixA14–35; Fm0 and OA=OI at hydrostatic stress','decimal_precision':70,'values':out}
if __name__=='__main__':print(json.dumps(check(),indent=2))
