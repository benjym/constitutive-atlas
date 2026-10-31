"""Separate algebraically equivalent research candidate; no material evaluation."""
from pathlib import Path
import json,hashlib
P=Path(__file__).parent;ROOT=P.parents[2]
def proposal(root=ROOT):
    m=json.loads((root/'docs/reviews/tresca-declarative-v1/model.json').read_text())
    m['id']='tresca-associated-perfect-bk2022v1-be-pressure-split-research'
    m['name']='Tresca — BK2022v1 project BE, pressure/deviator split'
    m['description']='Algebraically equivalent pressure/deviator implementation of the named BK2022v1 associated isotropic elastic-perfect plastic total-stress law with project-derived BE metric projection. New residual row conditioning preserves sigma6 and ep6; this is an algorithm variant, not a new constitutive family. Projection and plastic flow are computed before recombining mean stress. Compression-positive infinitesimal stress/strain, fixed spatial zero spin, orthonormal Mandel order xx,yy,zz,sqrt2xy,sqrt2yz,sqrt2xz. No pore-pressure law, drainage, finite-spin, hardening, smoothing, cap or experimental calibration. Same illustrative constants, full state and compatible initial total strain as the original draft; plotted strains remain increments. Strict source-ideal initial yield condition is unchanged; its rounded-root membership discrepancy remains unresolved. This source-only proposal is not an installed, compiled-qualified or scientifically admitted model.'
    m['derived']=[dict(name=n,expr=e)for n,e in [
        ('width','2*k'),
        ('trial_dev','dev(sigma_n)+2*mu*dev(de)'),
        ('mean_trial','trace(sigma_n)/3+(lame_lambda+2*mu/3)*trace(de)'),
        ('trace_trial','trace(trial_dev)'),
        ('vmax','principal_max_value(trial_dev)'),
        ('vmid','principal_mid_value(trial_dev)'),
        ('vmin','principal_min_value(trial_dev)'),
        ('branch','select(vmax-vmin<=width,0,select(3*vmid>trace_trial+width,1,select(3*vmid<trace_trial-width,2,3)))'),
        ('returned_dev','select(branch<0.5,trial_dev,select(branch<1.5,((trace_trial+width)/3)*I-width*projector_min(trial_dev),select(branch<2.5,((trace_trial-width)/3)*I+width*projector_max(trial_dev),trial_dev-((principal_max(trial_dev)-principal_min(trial_dev)-width)/2)*(projector_max(trial_dev)-projector_min(trial_dev)))))'),
        ('returned','mean_trial*I+returned_dev')]]
    m['equations']={'sigma':'sigma-returned','ep':'ep-ep_n-(trial_dev-returned_dev)/(2*mu)'}
    return m
if __name__=='__main__':
    target=P/'model.json';assert not target.exists();target.write_text(json.dumps(proposal(),indent=2)+'\n');print(hashlib.sha256(target.read_bytes()).hexdigest())
