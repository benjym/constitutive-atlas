"""Build CI targets serially, with one explicit target per CMake invocation."""
import argparse
import subprocess

ENGINES = (
    'atlas_power_creep_solver', 'atlas_solver', 'atlas_time_solver', 'atlas_research_solver',
    'atlas_history_solver', 'atlas_clay2013_solver', 'atlas_gis2024_solver',
    'atlas_expm_probe', 'atlas_log1p_probe', 'atlas_barodesy_rate_probe',
    'atlas_barodesy_material_ad_probe', 'atlas_barodesy_solver',
    'atlas_barodesy_hydro_ad_probe', 'atlas_clay2014_rate_probe',
)
NATIVE_TESTS = (
    'atlas_numerical_tests', 'atlas_recorded_tests', 'atlas_tensor_square_tests',
    'atlas_time_tests', 'atlas_capacity_tests', 'atlas_recorded_fixture_tests',
)


def commands(directory, wasm=False):
    return [['cmake', '--build', str(directory), '--target', target, '--parallel', '1']
            for target in ENGINES + (() if wasm else NATIVE_TESTS)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    parser.add_argument('--wasm', action='store_true')
    args = parser.parse_args()
    for command in commands(args.directory, args.wasm):
        subprocess.run(command, check=True)


if __name__ == '__main__':
    main()
