"""Prepare unlicensed source tables locally without admitting public assets.

This output is a review interchange, not a normalized material-test contract.
Every numeric source row and its native values are retained, including cycle
summary and full-time representations. Sample counts are not specimen counts.
"""
import argparse
from contextlib import contextmanager
from datetime import date, datetime, time
import gzip
import hashlib
import io
import json
from pathlib import Path
import re
import subprocess
import sys
import zipfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from atlas.measurement_units import UNITS


def dump(value):
    return json.dumps(value, ensure_ascii=False, separators=(',', ':'), allow_nan=False)+'\n'


def number(token):
    import math
    value = float(token.replace('D','E').replace('d','e').replace(',','.'))
    if not math.isfinite(value):
        raise ValueError('Nonfinite source value')
    return value


@contextmanager
def member_stream(path, member):
    if path.suffix.lower() == '.zip':
        with zipfile.ZipFile(path) as archive, archive.open(member) as stream:
            yield stream
    else:
        # Read only the named DAT; never unpack or run a bundled executable.
        proc = subprocess.Popen(['bsdtar','-xOf',str(path),member], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            yield proc.stdout
            error = proc.stderr.read()
            if proc.wait() != 0:
                raise ValueError('RAR member read failed: '+error.decode(errors='replace'))
        finally:
            proc.stdout.close()
            proc.stderr.close()
            if proc.poll() is None:
                proc.terminate(); proc.wait()


def prepare_table(package, table, raw_dir, output):
    name = package['source_id']+'-'+hashlib.sha256(table['member'].encode()).hexdigest()[:16]+'.jsonl.gz'
    expected_widths = {int(k) for k in table['numeric_column_counts']}
    # Only matching explicit unit counts establish an ordered column-unit map.
    # Labels, sign conventions and total/effective meaning are not inferred.
    headers = table['header_lines']
    units = []
    if len(expected_widths) == 1:
        width = next(iter(expected_widths))
        candidates = [re.findall(r'\[([^\]]+)\]', line) for line in headers]
        matches = [u for u in candidates if len(u) == width]
        if matches and all(u == matches[0] for u in matches):
            units = matches[0]
    conversions = [UNITS.get(u) for u in units]
    metadata = dict(format='atlas-private-source-table-v1', public_hosting=False,
                    source_id=package['source_id'], archive=package['filename'],
                    archive_sha256=package['sha256'], member=table['member'],
                    member_sha256=table['sha256'], headers=headers,
                    source_units=units, units=[c[0] if c else u for u,c in zip(units,conversions)],
                    conversions=[dict(scale=c[1],offset=c[2]) if c else None for c in conversions],
                    warnings=['Local review only: dataset redistribution permission unresolved.',
                              'No quantity/sign/initial-state inference; no interpolation or downsampling.',
                              'Commented numeric lines stay source comments and are not promoted to measurements.'])
    digest=hashlib.sha256();rows=0;first=last=None
    with member_stream(raw_dir/package['filename'],table['member']) as source, gzip.open(output/name,'wt',encoding='utf-8',compresslevel=1) as dest:
        dest.write(dump(dict(metadata=metadata)))
        for line_number,raw in enumerate(source,1):
            digest.update(raw)
            try:text=raw.decode('utf-8-sig').strip()
            except UnicodeDecodeError:text=raw.decode('cp1252').strip()
            if not text:continue
            try:values=[number(v) for v in text.split()]
            except ValueError:
                dest.write(dump(dict(source_line=line_number,source_text=text)));continue
            row=dict(source_line=line_number,native=values)
            if units:
                if len(values)!=len(units):raise ValueError('Source unit/channel mismatch')
                row['values']=[v*c[1]+c[2] if c else v for v,c in zip(values,conversions)]
            dest.write(dump(row));rows+=1
            if first is None:first=row
            last=row
    if rows!=table['numeric_rows'] or digest.hexdigest()!=table['sha256']:
        raise ValueError('Private table differs from reviewed source')
    return dict(path=name,source_id=package['source_id'],member=table['member'],rows=rows,
                source_sha256=digest.hexdigest(),sha256=hashlib.sha256((output/name).read_bytes()).hexdigest(),
                source_units=units,first=first,last=last)


def prepare_workbook(package, table, raw_dir, output):
    import openpyxl
    path=raw_dir/package['filename']
    if path.suffix.lower()=='.xlsx':raw=path.read_bytes()
    else:
        with zipfile.ZipFile(path) as archive:raw=archive.read(table['member'])
    if hashlib.sha256(raw).hexdigest()!=table['sha256']:raise ValueError('Workbook differs from reviewed source')
    workbook=openpyxl.load_workbook(io.BytesIO(raw),read_only=True,data_only=True)
    entries=[]
    try:
        for sheet in workbook:
            name=package['source_id']+'-'+hashlib.sha256((table['member']+'!'+sheet.title).encode()).hexdigest()[:16]+'.jsonl.gz'
            count=0
            with gzip.open(output/name,'wt',encoding='utf-8',compresslevel=1) as dest:
                dest.write(dump(dict(metadata=dict(format='atlas-private-workbook-table-v1',public_hosting=False,
                    archive=package['filename'],archive_sha256=package['sha256'],member=table['member'],
                    member_sha256=table['sha256'],sheet=sheet.title,
                    warnings=['Local review only: dataset redistribution permission unresolved.',
                              'Cached source cells preserved; formulas not recalculated and units not inferred.']))))
                for i,row in enumerate(sheet.values,1):
                    if any(v is not None for v in row):
                        values=[v.isoformat() if isinstance(v,(date,datetime,time)) else v for v in row]
                        dest.write(dump(dict(excel_row=i,cells=values)));count+=1
            entries.append(dict(path=name,source_id=package['source_id'],member=table['member'],sheet=sheet.title,
                                retained_source_rows=count,sha256=hashlib.sha256((output/name).read_bytes()).hexdigest()))
    finally:workbook.close()
    return entries


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir',type=Path,required=True)
    parser.add_argument('--review',type=Path,default=ROOT/'docs/data-license-evidence/soilmodels-package-review.json')
    parser.add_argument('--output',type=Path,default=ROOT/'tmp/private-measurements')
    parser.add_argument('--standard-only',action='store_true',help='Prepare the already-reviewed 33 standard workbooks, retaining existing private package entries')
    args=parser.parse_args();output=args.output.resolve()
    # Prevent a permission-held dataset from entering a website/public source tree.
    if not output.is_relative_to((ROOT/'tmp').resolve()):
        parser.error('Private review output must remain under the ignored repository tmp directory')
    output.mkdir(parents=True,exist_ok=True)
    review=json.loads(args.review.read_text());entries=[]
    if args.standard_only and (output/'index.json').exists():
        entries=[e for e in json.loads((output/'index.json').read_text())['entries'] if e['source_id']!='soilmodels-standard']
    for package in ([] if args.standard_only else review['packages']):
        path=args.raw_dir/package['filename']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=package['sha256']:raise ValueError('Source archive checksum mismatch')
        print('Processing',package['source_id'],flush=True)
        for table in package['measurements']:
            if 'worksheets' in table:entries.extend(prepare_workbook(package,table,args.raw_dir,output))
            else:entries.append(prepare_table(package,table,args.raw_dir,output))
        print('Prepared',len([e for e in entries if e['source_id']==package['source_id']]),'source tables',flush=True)
    if args.standard_only:
        standard=json.loads((ROOT/'docs/data-license-evidence/excalibre-workbook-review.json').read_text())
        for file in standard['files']:
            if file.get('status')!='downloaded':raise ValueError('Standard workbook unavailable')
            package=dict(source_id='soilmodels-standard',filename=file['filename'],sha256=file['sha256'])
            table=dict(member=Path(file['filename']).name,sha256=file['sha256'])
            entries.extend(prepare_workbook(package,table,ROOT,output))
        print('Prepared 33 standard workbooks',flush=True)
    (output/'index.json').write_text(json.dumps(dict(format='atlas-private-review-v1',public_hosting=False,
        entries=entries),ensure_ascii=False,indent=2)+'\n')
    print('Prepared',len(entries),'local tables;',sum(e.get('rows',0) for e in entries),'numeric rows',flush=True)


if __name__=='__main__':main()
