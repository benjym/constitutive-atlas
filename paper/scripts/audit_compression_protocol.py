"""Quantify data-only compression initialization and strain-coordinate choices."""
import argparse
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.common import ROOT, digest, read_json, write_json
from analysis.compression_protocol import first_loading_diagnostics
from analysis.reservations import assert_development_ids
from audit_compression import audit


def run(config_path):
    config = read_json(config_path)
    if config['phase'] != 'development_only_not_calibration_admission':
        raise ValueError('unsupported compression protocol phase')
    assert_development_ids(config['experiment_ids'])
    for source in config['source_evidence']:
        if digest(ROOT/source['local_copy']) != source['sha256']:
            raise ValueError('compression source differs from reviewed copy')
    directory = ROOT/config['data_directory']
    checked = audit(directory, ROOT/config['source_manifest'])
    if sorted(config['experiment_ids']) != sorted(checked['read_member_ids']):
        raise ValueError('protocol experiment coverage differs from extraction audit')
    results = [first_loading_diagnostics(read_json(directory/'normalized'/f'{identifier}.json'),
               config['minimum_axial_stresses_Pa']) for identifier in config['experiment_ids']]
    return dict(paper_record_version=1, protocol_id=config['id'], phase=config['phase'],
                protocol_sha256=digest(config_path), extraction_sha256=checked['extraction_sha256'],
                source_manifest_sha256=checked['manifest_sha256'], reservation_sha256=checked['reservation_sha256'],
                script_sha256=digest(__file__),
                analysis_sha256=digest(ROOT/'paper/analysis/compression_protocol.py'),
                data_audit_analysis_sha256=checked['analysis_sha256'],
                experiments=results, open_decisions=config['open_decisions'],
                interpretation='Exact void-ratio continuity diagnostic, not a stress simulation, calibration, uncertainty estimate or finite-strain verification.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config', type=Path, default=ROOT/'paper/study/compression_protocol.json')
    parser.add_argument('--output', type=Path, default=ROOT/'paper/results/compression-protocol')
    args = parser.parse_args()
    result = run(args.config)
    write_json(args.output/'report.json', result)
    lines = ['# Compression initialization feasibility', '', result['interpretation'], '',
             '| Test | Requested start (kPa) | Actual start (kPa) | First-loading strain increment | Log height increment | Engineering-driven end e residual | Geometry end e residual |',
             '| --- | ---: | ---: | ---: | ---: | ---: | ---: |']
    for experiment in result['experiments']:
        for scenario in experiment['scenarios']:
            if scenario['status'] == 'no_nonzero_first_loading_interval':
                lines.append(f"| {experiment['id']} | {scenario['requested_minimum_axial_stress_Pa']/1000:g} | unavailable | — | — | — | — |")
                continue
            lines.append(f"| {experiment['id']} | {scenario['requested_minimum_axial_stress_Pa']/1000:g} | {scenario['start_axial_stress_Pa']/1000:g} | {scenario['engineering_strain_increment']:.6g} | {scenario['logarithmic_height_strain_increment']:.6g} | {scenario['engineering_driven_end_void_ratio_residual']:.6g} | {scenario['geometry_end_void_ratio_residual']:.6g} |")
    lines += ['', 'Residual = diagnostic minus measured end void ratio. Values are dimensionless. No stress law is simulated, and initial lateral stress and history remain unresolved.', '',
              '1 kPa follows a published simulation start. 5 and 10 kPa are analyst-selected sensitivity thresholds. Starts use observed points without interpolation; no original observations are deleted.', '']
    lines += ['- '+decision for decision in result['open_decisions']]
    (args.output/'report.md').write_text('\n'.join(lines)+'\n')
    print('\n'.join(lines))


if __name__ == '__main__':
    main()
