"""Portable arithmetic acceptance matrix from the independent Python history evaluator."""
import argparse
import json
from pathlib import Path

from atlas.history import MAX_COUNTER, advance, make_snapshot
from atlas.model import ROOT


def flatten(values, declarations):
    result = []
    for name, declaration in sorted(declarations.items()):
        result.extend(values[name] if declaration['shape'] == 'sym' else [values[name]])
    return result


def cases():
    programs = {p['id']: p for path in sorted((ROOT/'fixtures/history').glob('*.json'))
                for p in [json.loads(path.read_text())]}
    matrix = []

    def add(label, identity, values, inputs, generation=0, epoch=0):
        program = programs[identity]
        parent = make_snapshot(program, values, generation, epoch)
        result = advance(program, parent, inputs)
        snapshot = result['snapshot']
        phase_names = [p['name'] for p in program['phases']]
        expected = {'valid': True, 'ok': result['ok'], 'program_sha256': parent['program_sha256'],
                    'generation': snapshot['generation'], 'preparation_epoch': snapshot['preparation_epoch'],
                    'values': flatten(snapshot['values'], program['fields']),
                    'events': [phase_names.index(e['phase']) for e in result['events']],
                    'diagnostics': dict(result['diagnostics'], failed_phase=(
                        phase_names.index(result['diagnostics']['failed_phase']) if result['diagnostics']['failed_phase'] else -1))}
        wire = [identity, parent['program_sha256'],
                ','.join(map(str, flatten(values, program['fields']))),
                ','.join(map(str, flatten(inputs, program['inputs']))), str(generation), str(epoch)]
        matrix.append({'label': label, 'wire': wire, 'expected': expected})
        return snapshot['values']

    ordered = 'synthetic-ordered-history'
    values = dict(x=2., y=5., lag=11., seed=7., mode=0., clock=3., stress=[10.,20.,30.,0.,0.,0.])
    inputs = dict(delta=4., dt=.5, prepare=0., load=[1.,2.,3.,0.,0.,0.])
    add('ordered copy', ordered, values, inputs)
    prepared = add('simultaneous prepare and advance', ordered, values, dict(inputs, prepare=1.), 6, 3)
    add('restart from accepted prepared snapshot', ordered, prepared, inputs, 7, 4)
    add('prepare strict positive guard skipped', ordered, values, dict(inputs, prepare=-1.))
    add('failure after preparation', ordered, values, dict(inputs, prepare=1., delta=-100.), 6, 3)
    add('generation exhaustion', ordered, values, inputs, MAX_COUNTER, 3)
    add('preparation epoch exhaustion', ordered, values, dict(inputs, prepare=1.), 6, MAX_COUNTER)
    add('epoch limit with skipped prepare', ordered, values, inputs, 6, MAX_COUNTER)
    probe = 'synthetic-guarded-history'
    values = dict(x=2., mode=0., s=[1.,2.,3.,0.,0.,0.])
    inputs = dict(command=1., bad=4., branch=0., modevalue=1.)
    for label, changes in [
        ('sqrt selected', {}), ('lazy unused negative sqrt', dict(branch=1., bad=-1.)),
        ('hidden exponential overflow', dict(branch=1., bad=1000.)),
        ('selected invalid sqrt', dict(bad=-1.)),
        ('tensor norm intermediate overflow', dict(branch=2., bad=1e308)),
        ('tensor norm selected', dict(branch=2., bad=1.)),
        ('invalid written mode', dict(modevalue=2.)),
        ('late failure discards earlier writes', dict(bad=100.)),
        ('strict zero guard and inactive invalid writes', dict(command=0., bad=-1., modevalue=2.)),
        ('positive guard and inactive invalid writes', dict(command=-1., bad=-1., modevalue=2.)),
    ]:
        add(label, probe, values, dict(inputs, **changes))
    add('inactive output checks still run', probe, dict(values, x=-1.), dict(inputs, command=0.))
    add('tensor write overflow', probe, dict(values, s=[1e308]*6), inputs)
    validation = 'synthetic-validation-history'
    for label, gate, value in [('finite validation expressions', 0., 2.),
                               ('overflow hidden in guard', 1000., 2.),
                               ('overflow hidden in comparison check', 0., 1000.)]:
        add(label, validation, {'x': 1.}, {'gate': gate, 'value': value})
    return matrix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.write_text(json.dumps(cases(), indent=2, allow_nan=False)+'\n')


if __name__ == '__main__':
    main()
