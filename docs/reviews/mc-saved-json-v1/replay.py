"""Replay synthetic assessor witnesses only. No solver, build or material calls."""
import copy
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
PROGRAM = '''import sys,json
sys.path.insert(0,sys.argv[1])
import assess_replays
from pathlib import Path
assess_replays.s=Path(sys.argv[2])
print(json.dumps(assess_replays.assess(sys.argv[2])))
'''


def check():
    fixture = json.loads(gzip.decompress((HERE/'fixture.json.gz').read_bytes()))
    pins = json.loads((HERE/'fixture-pins.json').read_text())
    for name, text in fixture.items():
        assert hashlib.sha256(text.encode()).hexdigest() == pins[name]
    original = {name: json.loads(text) for name,text in fixture.items()}
    results = []

    def change_raw(data, place, transform):
        if place == 'replay':
            row, key, call = data['replays.json'][0], 'raw', 2
        elif place == 'failure':
            row, key, call = data['rejections.json'][0], 'raw', 29
        elif place == 'recovery':
            row, key, call = data['rejections.json'][0], 'recovery_raw', 30
        elif place == 'describe':
            row, key, call = data['journal.json'][0], 'raw', 0
        else:
            raise ValueError(place)
        raw = transform(row[key]);row[key] = raw;data['calls.json'][call]['raw'] = raw

    cases = [('valid-source-ideal', None, True, True)]
    cases += [
        ('duplicate_replay_ok_raw', lambda d: change_raw(d,'replay',lambda raw:'{"ok":false,'+raw[1:]), True, False),
        ('duplicate_failure_ok_raw', lambda d: change_raw(d,'failure',lambda raw:'{"ok":true,'+raw[1:]), True, False),
        ('failure_raw_nonfinite_exponent', lambda d: change_raw(d,'failure',lambda raw:'{"extra":1e999,'+raw[1:]), True, False),
    ]
    # The existing eighteen replay/call/export/recovery corruption recipes.
    cases += [(name, mutate, False, False) for name, mutate in [
        ('missing call',lambda d:d['calls.json'].pop()),
        ('wrong API name',lambda d:d['calls.json'][1].update(name='atlas_run_with_settings')),
        ('wrong model argument',lambda d:d['calls.json'][1]['args'].__setitem__(0,'linear-elastic')),
        ('boolean protocol argument',lambda d:d['calls.json'][1]['args'].__setitem__(3,False)),
        ('wrong control bits argument',lambda d:d['calls.json'][1]['args'].__setitem__(4,'0000000000000000')),
        ('wrong settings argument',lambda d:d['calls.json'][1]['args'].__setitem__(5,'1,1,1,1,1,1')),
        ('wrong raw binding',lambda d:d['calls.json'][1].update(raw='{}')),
        ('boolean process status',lambda d:d['calls.json'][1]['process'].update(status=False)),
        ('wrong imported target',lambda d:d['replays.json'][0]['imported'].update(target=.02)),
        ('wrong export version',lambda d:d['replays.json'][0]['exported'].update(schema_version='0.1')),
        ('wrong export catalogue',lambda d:d['replays.json'][0]['exported'].update(catalogue_hash='wrong')),
        ('truncated exported result',lambda d:d['replays.json'][0]['exported'].update(result={'model':'mohr-coulomb','api_version':'experimental-laboratory-controls-0.1','catalogue_hash':original['generated/models.json']['sha256']})),
        ('fabricated exported stress',lambda d:d['replays.json'][0]['exported']['result']['points'][1]['state'].__setitem__(0,1e9)),
        ('wrong export model',lambda d:d['replays.json'][0]['exported']['result'].update(model='wrong')),
        ('changed export producer',lambda d:d['replays.json'][0]['exported']['specification']['loading']['producer'].update(algorithm='wrong')),
        ('missing recovery',lambda d:d['rejections.json'][0].pop('recovery_raw')),
        ('wrong rejection request',lambda d:d['rejections.json'][0]['request'].update(initial='')),
        ('wrong replay ID',lambda d:d['replays.json'][0].update(id='wrong')),
    ]]
    # Further raw-only cases exercise previously unparsed or unused regions.
    cases += [(name, mutate, None, False) for name, mutate in [
        ('duplicate describe key',lambda d:change_raw(d,'describe',lambda raw:'{"sha256":"discarded",'+raw[1:])),
        ('duplicate recovery key',lambda d:change_raw(d,'recovery',lambda raw:'{"ok":false,'+raw[1:])),
        ('nested duplicate rejection extra',lambda d:change_raw(d,'failure',lambda raw:'{"extra":{"x":0,"x":1},'+raw[1:])),
        ('nonfinite rejection constant',lambda d:change_raw(d,'failure',lambda raw:'{"extra":NaN,'+raw[1:])),
        ('huge rejection integer',lambda d:change_raw(d,'failure',lambda raw:'{"extra":'+('9'*400)+','+raw[1:])),
    ]]
    with tempfile.TemporaryDirectory(prefix='atlas-mc-saved-json-') as temporary:
        target = Path(temporary)
        for name, mutate, old_expected, new_expected in cases:
            data = copy.deepcopy(original)
            if mutate:mutate(data)
            for path,value in data.items():
                dest=target/path;dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_text(json.dumps(value,allow_nan=False)+'\n')
            row={'case':name,'backends':{}}
            for revision, expected in [('original',old_expected),('revised',new_expected)]:
                proc=subprocess.run([sys.executable,'-B','-c',PROGRAM,str(HERE/revision),str(target)],capture_output=True,text=True,timeout=30)
                accepted=proc.returncode==0
                row['backends'][revision]={'accepted':accepted,'expected_accepted':expected,'returncode':proc.returncode,'stdout':proc.stdout,'stderr':proc.stderr}
                if expected is not None and accepted != expected:
                    results.append(row)
                    (HERE/'results.json').write_text(json.dumps({'passed':False,'cases':results},indent=2)+'\n')
                    raise AssertionError((name,revision,accepted,expected,proc.stderr))
            results.append(row)
    report={'passed':True,'scope':'source-only synthetic saved-observation assessment; no numerical or scientific admission','cases':results,'valid_frame':{'export_import_replays':14,'rejection_recovery_pairs':12,'raw_calls_bound':53},'known_false_passes_reproduced':3,'existing_corruption_recipes_retained':18,'additional_raw_corruptions_rejected':5,'compiled_calls':0}
    (HERE/'results.json').write_text(json.dumps(report,indent=2)+'\n')
    return report


if __name__ == '__main__':
    report=check()
    print(json.dumps({key:value for key,value in report.items() if key!='cases'},indent=2))
