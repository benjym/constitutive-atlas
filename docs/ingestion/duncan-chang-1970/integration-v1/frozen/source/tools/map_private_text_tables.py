"""Map reviewed text headers to private streaming channels without public admission.

Mappings reference checksum-pinned local tables rather than copying millions of
rows. Exact source-byte aliases share one canonical table. Quantities named p
remain unspecified as to total/effective stress. Numerical identities are review
evidence, not automatic permission or model-compatibility decisions.
"""
import argparse
from collections import Counter
import gzip
import hashlib
import json
import math
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.measurement_units import UNITS


def compact(text):
    return ' '.join(text.split())


def fields(spec):
    return [part.split('|') for part in spec.split(';')]


SCHEMAS = {}


def schema(header, spec, units=None):
    SCHEMAS[(header, units)] = fields(spec)


schema("eps1 u sigma3 sigma3' sigma1 sigma1' p q",
       "eps1|%|axial_strain;u|kPa|pore_pressure;sigma3|kPa|radial_stress;sigma3'|kPa|effective_radial_stress;sigma1|kPa|axial_stress;sigma1'|kPa|effective_axial_stress;p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress",
       '[%] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa]')
schema("Time sigma1 sigma3 u sigma1' sigma3' p q eps1",
       "Time|s|time;sigma1|kPa|axial_stress;sigma3|kPa|radial_stress;u|kPa|pore_pressure;sigma1'|kPa|effective_axial_stress;sigma3'|kPa|effective_radial_stress;p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress;eps1|%|axial_strain",
       '[s] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [kPa] [%]')
schema('N uav pav qav eps1av eps1ampl',
       'N|-|cycle;uav|kPa|mean_pore_pressure;pav|kPa|mean_stress_cycle_average;qav|kPa|deviatoric_stress_cycle_average;eps1av|%|mean_axial_strain;eps1ampl|-|source_strain_amplitude',
       '[-] [kPa] [kPa] [kPa] [%] [-]')
schema('Axial stress [kPa] Void ratio [-]', 'Axial stress|kPa|axial_stress;Void ratio|-|void_ratio')
schema('N [-] p [kPa] q [kPa] eps_1 [%]', 'N|-|cycle;p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress;eps_1|%|axial_strain')
schema('N p [kPa] q [kPa] eps_1 [%]', 'N||cycle;p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress;eps_1|%|axial_strain')
schema('U [kPa] εA [%] q [kPa] p [kPa] σR [kPa] σA [kPa]', 'U|kPa|pore_pressure;εA|%|axial_strain;q|kPa|deviatoric_stress;p|kPa|mean_stress_unspecified;σR|kPa|radial_stress;σA|kPa|axial_stress')
schema('e [-] σ1 [kPa] ε1 [-] ε1 [%]', 'e|-|void_ratio;σ1|kPa|axial_stress;ε1|-|axial_strain;ε1|%|axial_strain')
tensor = "Sigma 3|kPa|radial_stress;Sigma 1|kPa|axial_stress;u_w|kPa|pore_pressure;Sigma3'|kPa|effective_radial_stress;Sigma'1|kPa|effective_axial_stress;p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress;eps_1|%|axial_strain"
schema("N [-] Sigma 3 [kPa] Sigma 1 [kPa] u_w [kPa] Sigma3' [kPa] Sigma'1 [kPa] p [kPa] q [kPa] eps_1 [%] uacc/p0 [-]", 'N|-|cycle;'+tensor+';uacc/p0|-|normalized_accumulated_pore_pressure')
schema("Sigma 3 [kPa] Sigma 1 [kPa] u_w [kPa] Sigma3' [kPa] Sigma'1 [kPa] p [kPa] q [kPa] eps_1 [%]", tensor)
schema('p (kPa) q (kPa) eps1 (%)', 'p|kPa|mean_stress_unspecified;q|kPa|deviatoric_stress;eps1|%|axial_strain')
schema('N uacc/p0 p q eps_1 [%]', 'N||cycle;uacc/p0||normalized_accumulated_pore_pressure;p||mean_stress_unspecified;q||deviatoric_stress;eps_1|%|axial_strain')


def columns_for(headers):
    if not headers:
        return []
    first = compact(headers[0])
    second = compact(headers[1]) if len(headers) > 1 else None
    specs = SCHEMAS.get((first, second), SCHEMAS.get((first, None)))
    if specs is None:
        raise ValueError('Unreviewed source header: '+first)
    result = []
    for index, (label, unit, quantity) in enumerate(specs):
        conversion = UNITS.get(unit)
        result.append(dict(key='c'+str(index), index=index, label=label, quantity=quantity,
                           source_unit=unit or None, unit=conversion[0] if conversion else None,
                           conversion=dict(scale=conversion[1], offset=conversion[2]) if conversion else None))
    return result


def role(member):
    lower = member.lower()
    if '-vs-n.dat' in lower:
        return 'cycle_summary'
    if '_preloading.dat' in lower:
        return 'preloading_stage'
    if '_shearing.dat' in lower:
        return 'shearing_stage'
    if 'oedometer' in lower:
        return 'oedometer_history'
    if 'monotonic' in lower:
        return 'monotonic_history'
    return 'cyclic_history'


def family(source_id, member):
    # Source family hints only, never proof of independent specimen identity.
    stem = re.sub(r'-test-data-vs-(?:N|time)$|_(?:Preloading|Shearing)$', '', Path(member).stem)
    if source_id == 'soilmodels-karlsruhe-kaolin':
        return source_id+'/'+stem  # Same C-number occurs in several parameter folders.
    return source_id+'/'+str(Path(member).parent/stem)


def iter_mapped_rows(path, columns):
    """Yield every numeric source row and only explicitly established SI values."""
    with gzip.open(path, 'rt') as stream:
        next(stream)
        for line in stream:
            row = json.loads(line)
            if 'native' not in row:
                continue
            native = row['native']
            if len(native) != len(columns):
                raise ValueError('Source row/channel width mismatch')
            values = {c['key']: native[c['index']]*c['conversion']['scale']+c['conversion']['offset']
                      for c in columns if c['conversion']}
            if not all(math.isfinite(v) for v in native+list(values.values())):
                raise ValueError('Nonfinite source or converted value')
            yield dict(source_line=row['source_line'], native=native, values=values)


def residual_checks(columns):
    index = {c['quantity']: c['index'] for c in columns if c['source_unit'] == 'kPa'}
    checks = {}
    def add(name, required, function):
        if all(q in index for q in required):
            checks[name] = function
    add('q_equals_axial_minus_radial', ['deviatoric_stress','axial_stress','radial_stress'],
        lambda r:r[index['deviatoric_stress']]-(r[index['axial_stress']]-r[index['radial_stress']]))
    add('p_equals_total_mean', ['mean_stress_unspecified','axial_stress','radial_stress'],
        lambda r:r[index['mean_stress_unspecified']]-(r[index['axial_stress']]+2*r[index['radial_stress']])/3)
    add('p_equals_total_mean_minus_pore_pressure', ['mean_stress_unspecified','axial_stress','radial_stress','pore_pressure'],
        lambda r:r[index['mean_stress_unspecified']]-(r[index['axial_stress']]+2*r[index['radial_stress']])/3+r[index['pore_pressure']])
    add('q_equals_effective_axial_minus_radial', ['deviatoric_stress','effective_axial_stress','effective_radial_stress'],
        lambda r:r[index['deviatoric_stress']]-(r[index['effective_axial_stress']]-r[index['effective_radial_stress']]))
    add('p_equals_effective_mean', ['mean_stress_unspecified','effective_axial_stress','effective_radial_stress'],
        lambda r:r[index['mean_stress_unspecified']]-(r[index['effective_axial_stress']]+2*r[index['effective_radial_stress']])/3)
    for axis in ['axial','radial']:
        add(axis+'_effective_equals_total_minus_pore_pressure', ['effective_'+axis+'_stress',axis+'_stress','pore_pressure'],
            lambda r,a=axis:r[index['effective_'+a+'_stress']]-r[index[a+'_stress']]+r[index['pore_pressure']])
    return checks


def review_issues(mapping):
    issues = []
    if mapping['zero_only_columns']:
        issues.append('Some source channels are zero in every row; review their availability before using them.')
    # This descriptive threshold flags conflicts; it never certifies admission.
    stats = mapping['checks']['stress_identities']
    if any(s['above_0_02_kPa'] for k,s in stats.items()
           if k.startswith('q_equals_') or '_effective_equals_' in k):
        issues.append('Source stress channels disagree beyond the 0.02 kPa diagnostic threshold; preserve the supplied curves and review reconstruction separately.')
    return issues


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, default=ROOT/'tmp/private-measurements')
    parser.add_argument('--output', type=Path, default=ROOT/'tmp/private-text-mappings')
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to((ROOT/'tmp').resolve()):
        parser.error('Permission-held mappings must remain under ignored tmp')
    output.mkdir(parents=True, exist_ok=True)
    review = json.loads((ROOT/'docs/data-license-evidence/soilmodels-package-review.json').read_text())
    tables = {(p['source_id'], t['member']):t for p in review['packages'] for t in p['measurements']}
    sources = [e for e in json.loads((args.input/'index.json').read_text())['entries']
               if e['source_id'] in ['soilmodels-karlsruhe-kaolin','soilmodels-malaysian','soilmodels-zbraslav']]
    canonical = {}; entries = []
    for e in sources:
        t = tables[(e['source_id'],e['member'])]
        columns = columns_for(t['header_lines'])
        if set(t['numeric_column_counts']) != {str(len(columns))}:
            raise ValueError('Reviewed column count mismatch')
        identity = (e['source_id'], t['sha256'])
        mapping = dict(source_id=e['source_id'], member=e['member'], source_table=e['path'],
                       source_table_sha256=e['sha256'], member_sha256=t['sha256'],
                       columns=columns, role=role(e['member']), family_hint=family(e['source_id'],e['member']),
                       public_hosting=False, model_overlay_eligible=False, rows=e['rows'],
                       warnings=['Permission and physical admission review remain open.',
                                 'Source p remains unspecified; stress identities do not infer initial state or compression sign.'])
        path = args.input/e['path']
        if hashlib.sha256(path.read_bytes()).hexdigest() != e['sha256']:
            raise ValueError('Private input checksum mismatch')
        if identity in canonical:
            mapping['alias_of'] = canonical[identity]['source_table']
            mapping['checks'] = canonical[identity]['checks']
            mapping['zero_only_columns'] = canonical[identity]['zero_only_columns']
        else:
            checks = residual_checks(columns)
            stats = {k:dict(rows=0,max_abs_residual_kPa=0,above_0_02_kPa=0) for k in checks}
            count = 0; values = 0; previous = 0; nonzero = set()
            for row in iter_mapped_rows(path, columns):
                if row['source_line'] <= previous:raise ValueError('Source coordinate disorder')
                previous = row['source_line']; count += 1; values += len(row['values'])
                nonzero.update(i for i,v in enumerate(row['native']) if v != 0)
                for name, function in checks.items():
                    residual = abs(function(row['native']))
                    s = stats[name];s['rows'] += 1
                    s['max_abs_residual_kPa'] = max(s['max_abs_residual_kPa'], residual)
                    s['above_0_02_kPa'] += residual > .02
            if count != e['rows']:raise ValueError('Private row count mismatch')
            mapping['checks'] = dict(rows_checked=count,converted_values=values,stress_identities=stats)
            mapping['zero_only_columns'] = [c['key'] for c in columns if c['index'] not in nonzero]
            canonical[identity] = mapping
        mapping['review_issues'] = review_issues(mapping)
        entries.append(mapping)
        if len(entries)%10 == 0:print('Reviewed',len(entries),'of',len(sources),'tables',flush=True)
    result = dict(format='atlas-private-text-mappings-v1', public_hosting=False,
                  model_overlay_eligible=False, entries=entries)
    (output/'index.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    summary = dict(tables=len(entries),unique_source_tables=len(canonical),
                   exact_aliases=sum('alias_of' in e for e in entries),
                   unique_rows_checked=sum(e['rows'] for e in canonical.values()),
                   converted_values_checked=sum(e['checks']['converted_values'] for e in canonical.values()),
                   roles=dict(Counter(e['role'] for e in canonical.values())))
    (output/'verification.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary),flush=True)


if __name__ == '__main__':
    main()
