"""Prepare VIBE plot-defined axes and BCV property cells for private review.

Read plot scripts as evidence only. Never execute bundled scripts or binaries.
Outputs remain permission-held and are not normalized model experiments.
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
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.measurement_units import UNITS


def read_private(directory, entry):
    path = directory/entry['path']
    if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
        raise ValueError('Private source checksum mismatch')
    with gzip.open(path, 'rt') as stream:
        metadata = json.loads(next(stream))['metadata']
        rows = [json.loads(line) for line in stream]
    return metadata, rows


def write_private(path, record):
    with gzip.open(path, 'wt') as stream:
        json.dump(record, stream, ensure_ascii=False, allow_nan=False, separators=(',', ':'))
    return hashlib.sha256(path.read_bytes()).hexdigest()


def column(index, quantity, unit):
    conversion = UNITS.get(unit)
    return dict(index=index, quantity=quantity, source_unit=unit,
                unit=conversion[0] if conversion else None,
                conversion=dict(scale=conversion[1],offset=conversion[2]) if conversion else None)


def vibe_spec(name):
    if name in ['oed1.txt','oed2.txt','oed-20C.txt','oed-100C.txt']:
        return 'oedometer_history', [('vertical_stress','MPa'),('void_ratio','1')], 'gpoed-temper.gp' if 'C.' in name else 'gpoed.gp'
    if re.fullmatch(r'WRC(?:1270|1600|1900)cv.txt',name):
        return 'constant_volume_retention', [('suction','MPa'),('water_content','1'),('saturation','1')], 'gpWRCwc-cv.gp'
    if re.fullmatch(r'WRC(?:1270|1600|1900).txt',name) or name == 'WRC1600wett.txt':
        return 'retention_history', [('suction','MPa'),('water_content','1'),('unmapped_source_column',None),('saturation','1')], 'gpWRC-wcM.gp'
    if re.fullmatch(r'WRC1600-(?:40|60|80)C.txt',name):
        return 'heated_retention', [('suction','MPa'),('water_content','%')], 'gpWRCwc-temper.gp'
    if name.startswith('swellconstload'):
        return 'constant_load_swelling', [('vertical_stress','MPa'),('source_void_ratio','1')], 'gpswellconstload-rhod.gp'
    if name == 'swellpres.txt':
        return 'swelling_pressure_summary', [('source_void_ratio','1'),('swelling_pressure','MPa')], 'gpswellpres-rhod.gp'
    if name == 'bentstrength.csv':
        return 'uniaxial_strength_summary', [('dry_density','g/cm^3'),('uniaxial_strength','MPa')], 'gpuniax.gp'
    if name in ['st036.txt','st040.txt']:
        return 'loading_segments', [('start_stress_uncorrected','kPa'),('start_dry_density','kg/m3'),('end_stress_uncorrected','kPa'),('end_dry_density','kg/m3')], 'gpoedswell.gp'
    return 'unresolved_source_table', [], None


def convert_vibe(row, columns, kind):
    native = row['native']
    if columns and len(native) != len(columns):
        raise ValueError('VIBE channel width mismatch')
    values = {str(c['index']):native[c['index']]*c['conversion']['scale']+c['conversion']['offset']
              for c in columns if c['conversion']}
    result = dict(source_line=row['source_line'],native=native,values=values)
    if kind in ['constant_load_swelling','swelling_pressure_summary']:
        index = 1 if kind == 'constant_load_swelling' else 0
        if native[index] <= -1:raise ValueError('Invalid source density denominator')
        result['source_plot_derived'] = dict(dry_density_kg_m3=2760/(native[index]+1))
    if kind == 'loading_segments':
        # The active gnuplot vector uses +5.12 kPa at its start, and an
        # unshifted stress difference. Preserve both corrected endpoints.
        result['source_plot_derived'] = dict(start_stress_Pa=(native[0]+5.12)*1000,
                                            end_stress_Pa=(native[2]+5.12)*1000)
    if not all(math.isfinite(v) for v in native+list(values.values())+list(result.get('source_plot_derived',{}).values())):
        raise ValueError('Nonfinite VIBE observation')
    return result


def plot_evidence(archive, script, source_name):
    member = 'VIBEPaperDataset/resultsAndGraphs/'+script
    raw = archive.read(member)
    lines = raw.decode('utf-8').splitlines()
    # Store active axis labels and active experimental uses with source lines.
    relevant = [dict(line=i,text=line) for i,line in enumerate(lines,1)
                if not line.lstrip().startswith('#') and
                (re.match(r'\s*set (?:x|y)label',line) or
                 re.match(r'\s*(?:rhos|logkorekce)\s*=',line) or '../data/'+source_name in line)]
    return dict(member=member,sha256=hashlib.sha256(raw).hexdigest(),lines=relevant)


PROPERTY_SHEETS = {'PROP,SWEP,RC','SI,WL,WP,SpD','THC,HEC'}


def property_unit(label):
    if not isinstance(label,str):return None
    compact = ' '.join(label.split())
    # Only an explicit trailing unit is accepted. Do not infer shared units
    # from neighbouring columns or translate arbitrary Czech descriptions.
    match = re.search(r',\s*(kPa|kg/m3|m/s|%|-|°C|W/m·K|J/kg·K|J/m3·K|dny|ml/2 g)$',compact)
    return match.group(1) if match else None


def bcv_properties(rows):
    by_row = {r['excel_row']:r['cells'] for r in rows}
    header = by_row.get(2,[]); groups = by_row.get(1,[])
    properties = []
    for row in rows:
        if row['excel_row'] <= 2:continue
        cells = row['cells']
        # Source header labels repeated properties by index; never key by name.
        for index, value in enumerate(cells):
            if index < 4 or not isinstance(value,(int,float)) or isinstance(value,bool):continue
            label = header[index] if index < len(header) else None
            if not label:continue
            unit = property_unit(label); conversion = UNITS.get(unit)
            uncertainty = label.lstrip().startswith('nejistota')
            if conversion and uncertainty:
                conversion = (conversion[0],conversion[1],0)
            if not math.isfinite(value):raise ValueError('Nonfinite BCV property')
            prior_groups = [v for v in groups[:index+1] if isinstance(v,str)]
            properties.append(dict(excel_row=row['excel_row'],column=index+1,
                reference_code=cells[1] if len(cells)>1 else None,
                sample_in_reference=cells[2] if len(cells)>2 else None,
                sample_in_compilation=cells[3] if len(cells)>3 else None,
                group=prior_groups[-1] if prior_groups else None,label=label,is_uncertainty=uncertainty,
                native=value,source_unit=unit,unit=conversion[0] if conversion else None,
                value=value*conversion[1]+conversion[2] if conversion else None,
                conversion=dict(scale=conversion[1],offset=conversion[2]) if conversion else None,
                source_context=cells))
    return properties


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,default=ROOT/'tmp/private-measurements')
    parser.add_argument('--raw-dir',type=Path,default=ROOT/'tmp/dataset-survey/user-downloads')
    parser.add_argument('--output',type=Path,default=ROOT/'tmp/private-bentonite-mappings')
    args=parser.parse_args();output=args.output.resolve()
    if not output.is_relative_to((ROOT/'tmp').resolve()):parser.error('Private output must remain under ignored tmp')
    output.mkdir(parents=True,exist_ok=True)
    source=json.loads((args.input/'index.json').read_text())['entries']
    package_review=json.loads((ROOT/'docs/data-license-evidence/soilmodels-package-review.json').read_text())
    pin=next(p for p in package_review['packages'] if p['source_id']=='soilmodels-vibe')
    archive_path=args.raw_dir/pin['filename']
    if hashlib.sha256(archive_path.read_bytes()).hexdigest()!=pin['sha256']:raise ValueError('VIBE archive checksum mismatch')
    entries=[];vibe_records={}
    with zipfile.ZipFile(archive_path) as archive:
        for e in source:
            if e['source_id']!='soilmodels-vibe':continue
            metadata,rows=read_private(args.input,e);name=Path(e['member']).name
            kind,spec,script=vibe_spec(name)
            columns=[column(i,q,u) for i,(q,u) in enumerate(spec)]
            evidence=[]
            if script:
                # The wetting-only file is checked against its parent below.
                plot_name='WRC1600.txt' if name=='WRC1600wett.txt' else name
                evidence.append(plot_evidence(archive,script,plot_name))
                if kind=='retention_history':evidence.append(plot_evidence(archive,'gpWRC-SrM.gp',plot_name))
                if kind=='constant_volume_retention':evidence.append(plot_evidence(archive,'gpWRC-cv.gp',plot_name))
            numeric=[convert_vibe(r,columns,kind) for r in rows if 'native' in r]
            if len(numeric)!=e['rows']:raise ValueError('VIBE row count mismatch')
            record=dict(source_id=e['source_id'],member=e['member'],source_table=e['path'],source_table_sha256=e['sha256'],
                        public_hosting=False,model_overlay_eligible=False,kind=kind,columns=columns,
                        rows=numeric,source_comments=[r for r in rows if 'source_text'in r],plot_evidence=evidence,
                        warnings=['Dataset permission and physical admission remain open. Source comments are not experimental observations.'])
            if kind=='loading_segments':record['source_plot_transform']=dict(stress_offset_kPa=5.12,note='Separate vector segments; endpoints are not concatenated into a new test history.')
            if kind in ['constant_load_swelling','swelling_pressure_summary']:record['source_plot_transform']=dict(density='2760 / (source_void_ratio + 1) kg/m³',note='Author plot transformation; not an independently measured density or inferred initial state.')
            vibe_records[name]=record
        subset=vibe_records['WRC1600wett.txt'];parent=vibe_records['WRC1600.txt']
        if [r['native'] for r in subset['rows']] != [r['native'] for r in parent['rows'][:len(subset['rows'])]]:raise ValueError('Wetting subset differs from parent history')
        subset['subset_of']=dict(member=parent['member'],parent_numeric_row_start=1,parent_numeric_row_end=len(subset['rows']))
        for name,record in vibe_records.items():
            path='vibe-'+name+'.json.gz';digest=write_private(output/path,record)
            entries.append(dict(source_id='soilmodels-vibe',member=record['member'],path=path,sha256=digest,kind=record['kind'],rows=len(record['rows']),mapped=bool(record['columns']),subset='subset_of'in record))
    bcv=[e for e in source if e['source_id']=='soilmodels-bcv']
    references={}
    for e in bcv:
        if e['sheet']=='reference':
            _,rows=read_private(args.input,e)
            references[e['member']]=[r for r in rows if r['excel_row']>2]
    for e in bcv:
        metadata,rows=read_private(args.input,e)
        properties=bcv_properties(rows) if e['sheet']in PROPERTY_SHEETS else []
        record=dict(source_id=e['source_id'],member=e['member'],sheet=e['sheet'],
                    source_table=e['path'],source_table_sha256=e['sha256'],public_hosting=False,
                    model_overlay_eligible=False,kind='property_summary' if e['sheet']in PROPERTY_SHEETS else 'source_context',
                    properties=properties,source_rows=rows,
                    workbook_references=references.get(e['member'],[]) if properties else [],
                    warnings=['Property/reference compilation, not a loading history.','References remain a list: no row-position joins or assumed unique reference codes.','Dataset hosting permission unresolved.'])
        path=e['path'].replace('.jsonl.gz','.json.gz');digest=write_private(output/path,record)
        entries.append(dict(source_id=e['source_id'],member=e['member'],sheet=e['sheet'],path=path,sha256=digest,
                            kind=record['kind'],property_cells=len(properties),converted_property_cells=sum(p['conversion']is not None for p in properties),retained_source_rows=len(rows)))
    index=dict(format='atlas-private-bentonite-mappings-v1',public_hosting=False,model_overlay_eligible=False,entries=entries)
    (output/'index.json').write_text(json.dumps(index,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps(dict(tables=len(entries),roles=dict(Counter(e['kind'] for e in entries)),
                          vibe_rows=sum(e.get('rows',0)for e in entries),
                          bcv_property_cells=sum(e.get('property_cells',0)for e in entries),
                          bcv_converted_cells=sum(e.get('converted_property_cells',0)for e in entries))))


if __name__=='__main__':main()
