"""Source-distinguishing scalar algebra only; no constitutive implementation."""
import argparse
import json
import math
from pathlib import Path

rows=[]
for name,phi,N,la,ka in [('London clay',22.6,1.375,.11,.016),('Dresden clay',35,.622,.038,.008),('Weald clay',24,.8,.059,.018)]:
 s=math.sin(math.radians(phi)); c2=-(3*math.sqrt(2)+3)/2;c1=(1-s)/(2*c2*c2*s);c5=(1+s)/(1-s);t=c5*la
 c3=(-math.sqrt(3)/la+math.sqrt(3)/ka)/(2**t+(1/500)**t-2)
 c6=1/(2*(-math.sqrt(3)/(c3*ka)+2**t-1));beta=-1/(c3*la)+(2**t-1)/math.sqrt(3)
 # Per unit positive compressive volumetric strain, on NCL, p'=p/lambda.
 body=c3/math.sqrt(3)*(2**t-1-math.sqrt(3)*beta)
 appendix=c3/math.sqrt(3)*(6**t-1-math.sqrt(3)*beta)
 rows.append(dict(material=name,phi_deg=phi,N=N,lambda_star=la,kappa_star=ka,c1=c1,c2=c2,c3=c3,c4=1,c5=c5,c6=c6,body_dlogp_dv=body,appendix_dlogp_dv=appendix,expected_ncl_dlogp_dv=1/la,relative_body_defect=body*la-1,relative_appendix_defect=appendix*la-1))
diag={'scope':'Independent scalar algebra only; no Atlas model, author code, tensor exponential or integrator execution. Not scientific admission.','definitions':{'v':'compression-positive volumetric strain','ncl':'1+e=exp(N)*(p/sigma_star)^(-lambda_star)','body_ec':'1+ec=exp(N)*(2p/sigma_star)^(-lambda_star)','appendix_ec':'1+ec=exp(N)*(6p/sigma_star)^(-lambda_star)','dlogp_dv':'c3/sqrt(3)*(A-1-sqrt(3)*beta), beta=-1/(c3*lambda)+(2^(c5*lambda)-1)/sqrt(3)','A_body':'2^(c5*lambda)','A_appendix':'6^(c5*lambda)'},'rows':rows,'m_equals_c2_delta':math.sqrt(6*rows[0]['c2']**2/(9+2*rows[0]['c2']**2))}

if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    args.output.write_text(json.dumps(diag,indent=2)+'\n')
