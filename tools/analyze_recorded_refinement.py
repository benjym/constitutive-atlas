"""Verify retained ordered-path evidence, summarize it and optionally plot it."""
import argparse
import copy
import gzip
import hashlib
import json
import math
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from atlas.refinement import VERSION,validate_study,refine_recorded,difference
from atlas.recorded import recorded_wire,MATERIAL_DEFAULTS,CONTROL_DEFAULTS


def canonical(value):return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def summarize(report,settings_pairs=()):
    if report.get('version')!=VERSION or report.get('execution_complete') is not True:raise ValueError('incomplete or unsupported refinement report')
    config=validate_study(report['study'])
    if hashlib.sha256(canonical(config)).hexdigest()!=report['study_sha256']:raise ValueError('study hash mismatch')
    if [c['id'] for c in report['cases']]!=[c['id'] for c in config['cases']]:raise ValueError('case matrix mismatch')
    summary=dict(study_id=config['id'],comparator='requested finest; not an exact solution',successful=0,failed=0,cases=[],settings_comparisons=[])
    for case,source in zip(report['cases'],config['cases']):
        if [l['factor'] for l in case['levels']]!=config['factors']:raise ValueError('factor matrix mismatch')
        observations=[];first=None
        for level in case['levels']:
            spec,indices=refine_recorded(source['specification'],level['factor'])
            if indices!=level['original_indices']:raise ValueError('original-record mapping changed')
            r=level.get('response')
            if r is None:
                if not level.get('transport_error'):raise ValueError('missing response and transport status')
                observations.append(None);summary['failed']+=1;continue
            if r.get('specification')!=spec or r.get('request_sha256')!=hashlib.sha256(canonical(spec)).hexdigest():raise ValueError('request changed')
            c,k=recorded_wire(spec)
            if r.get('controls_wire')!=c or r.get('knots_wire')!=k or r.get('catalogue_hash')!=report['catalogue_hash']:raise ValueError('wire/catalogue changed')
            if r['initial_strain']!=spec['path']['initial_strain']:raise ValueError('strain origin changed')
            expected_material=MATERIAL_DEFAULTS|spec.get('integration_settings',{})
            if any(r['integration_settings'][key]!=v for key,v in expected_material.items()):raise ValueError('material settings changed')
            if r['control_settings']!=CONTROL_DEFAULTS|spec.get('control_settings',{}):raise ValueError('control settings changed')
            for field in ('parameters','initial'):
                if field in spec and spec[field]!=r[field]:raise ValueError('explicit material/state inputs changed')
            if first is None:first=r
            if r['parameters']!=first['parameters'] or r['initial']!=first['initial']:raise ValueError('initial conditions changed')
            points=r['points']
            if points and (r['state']!=points[-1]['state'] or r['strain']!=points[-1]['strain']):raise ValueError('committed prefix lost')
            if r['ok']:
                if len(points)!=len(spec['path']['knots']) or r['failed_knot']!=-1:raise ValueError('incomplete successful path')
                summary['successful']+=1;observations.append([points[i] for i in indices])
            else:
                if r['failed_knot']>=0 and len(points)!=r['failed_knot']:raise ValueError('failure knot mismatch')
                summary['failed']+=1;observations.append(None)
            fields=case['fields']
            if fields:
                stress_scale=max(1.,max(map(abs,r['initial'][:6])),fields[0]['scale'])
                for pt,knot in zip(points,spec['path']['knots']):
                    if pt['coordinate']!=knot['coordinate']:raise ValueError('observation order changed')
                    for row,target in zip(spec['path']['controls'],knot['targets']):
                        scale=max(map(abs,row['coefficients']));v=pt['state'][:6] if row['kind']=='stress' else pt['strain']
                        residual=(sum(a/scale*b for a,b in zip(row['coefficients'],v))-target/scale)/(stress_scale if row['kind']=='stress' else 1.)
                        if not math.isfinite(residual) or abs(residual)>r['control_settings']['control_tolerance']+1e-14:raise ValueError('accepted control endpoint violated')
        finest=observations[-1]
        if case['finest_complete']!=(finest is not None):raise ValueError('finest completion changed')
        previous=None;rows=[]
        for level,points in zip(case['levels'],observations):
            final_error=difference(points,finest,case['fields']) if points is not None and finest is not None else None
            previous_error=difference(points,previous,case['fields']) if points is not None and previous is not None else None
            if level['comparison_to_finest']!=final_error or level['comparison_to_previous']!=previous_error:raise ValueError('stored metrics differ from accepted observations')
            rows.append(dict(factor=level['factor'],ok=points is not None,comparison_to_finest=final_error,comparison_to_previous=previous_error,
                             message=level.get('transport_error',level.get('response',{}).get('message',''))))
            previous=points
        summary['cases'].append(dict(id=case['id'],model=case['model'],finest_complete=case['finest_complete'],fields=case['fields'],levels=rows))
    by_id={c['id']:c for c in report['cases']};configs={c['id']:c['specification'] for c in config['cases']}
    for left,right in settings_pairs:
        a,b=by_id[left],by_id[right];sa,sb=copy.deepcopy(configs[left]),copy.deepcopy(configs[right])
        sa.pop('integration_settings',None);sb.pop('integration_settings',None)
        if sa!=sb or a['fields']!=b['fields']:raise ValueError('settings comparison changes more than material integration settings')
        values=[]
        for x,y in zip(a['levels'],b['levels']):
            rx,ry=x.get('response',{}),y.get('response',{})
            error=None
            if rx.get('ok') and ry.get('ok'):
                px=[rx['points'][i] for i in x['original_indices']];py=[ry['points'][i] for i in y['original_indices']]
                error=difference(px,py,a['fields'])
            values.append(dict(factor=x['factor'],difference=error))
        summary['settings_comparisons'].append(dict(left=left,right=right,levels=values))
    return summary


def plot(summary,output):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    plt.rcParams.update({'font.size':10,'svg.hashsalt':'recorded-refinement-v1'})
    fig,ax=plt.subplots(figsize=(7.5,4.6));colors={'modified-cam-clay':'#64538a','hypoplastic-sand-vw96':'#21765b','hypoplastic-sand-igs97':'#b75a2a'}
    names={'modified-cam-clay':'Cam-Clay','hypoplastic-sand-vw96':'VW96','hypoplastic-sand-igs97':'IGS97'}
    for case in summary['cases']:
        if case['model'] not in colors or not case['id'].endswith(('-default','-tight')):continue
        rows=[l for l in case['levels'][:-1] if l['comparison_to_finest'] is not None]
        tight=case['id'].endswith('-tight')
        ax.loglog([r['factor'] for r in rows],[r['comparison_to_finest']['max_persistent_state_scaled'] for r in rows],
                  's--' if tight else 'o-',color=colors[case['model']],markersize=4,label=names[case['model']]+(' tight material settings' if tight else ' default material settings'))
    factors=[1,2,4,8,16];ax.set_xticks(factors,[str(x) for x in factors]);ax.grid(True,which='both',alpha=.2)
    ax.set_xlabel('Subdivisions per original interval')
    ax.set_ylabel('Max scaled persistent-state difference\nat original records versus factor 32')
    ax.legend(fontsize=8,loc='lower left')
    ax.set_title('Mixed-control path resolution; illustrative parameters',fontsize=11)
    fig.text(.14,.015,'IGS97 failed at factor 1 (default) and factors 1, 2 (tight); failed runs are not plotted.',fontsize=8)
    fig.tight_layout(rect=(0,.045,1,1))
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    fig.savefig(output/'path-resolution.svg',metadata={'Date':None});fig.savefig(output/'path-resolution.png',dpi=160);plt.close(fig)


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);p.add_argument('--output',type=Path,required=True)
    p.add_argument('--pair',action='append',default=[],help='case-ID=case-ID with only material settings changed');p.add_argument('--figures',type=Path)
    args=p.parse_args();raw=args.report.read_bytes();report=json.loads(gzip.decompress(raw) if args.report.suffix=='.gz' else raw)
    pairs=[tuple(v.split('=')) for v in args.pair]
    if any(len(v)!=2 for v in pairs):p.error('--pair requires two case IDs separated by =')
    summary=summarize(report,pairs);args.output.write_text(json.dumps(summary,indent=2,allow_nan=False)+'\n')
    if args.figures:plot(summary,args.figures)
    print(f"Verified {summary['successful']} successful and {summary['failed']} failed recorded-path runs.")


if __name__=='__main__':main()
