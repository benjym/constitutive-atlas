"""Bounded source/contracts gate; no compiler, material studies or network access."""
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main():
    def run(*args):
        started = time.monotonic()
        print('+', *args, flush=True)
        subprocess.run(args, cwd=ROOT, check=True)
        print(f'Completed in {time.monotonic()-started:.1f}s', flush=True)

    # Use the canonical exporter: it verifies approval/model/review/supporting-byte
    # bindings, including archive mappings, instead of maintaining another gate.
    with tempfile.TemporaryDirectory(prefix='atlas-ci-integrity-') as temporary:
        run(sys.executable, '-B', '-m', 'atlas.cli', 'database', str(Path(temporary)/'atlas.sqlite'))
    run(sys.executable, '-B', '-m', 'atlas.cli', 'validate')
    run(sys.executable, '-B', '-m', 'unittest',
        'tests.test_atlas.LanguageTests', 'tests.test_agent_review',
        'tests.test_database_approval_integrity',
        'tests.test_state_contract.StateContractTests', 'tests.test_laboratory_view',
        'tests.test_ci_profiles',
        'tests.test_ci_changes', '-q')
    run('node', 'tools/check_model_profiles.mjs')
    run('node', '--test', 'tests/test_chart_axis.mjs', 'tests/test_model_profiles.mjs',
        'tests/test_guided_experiments.mjs', 'tests/test_ensemble.mjs', 'tests/test_ensemble_outcomes.mjs',
        'tests/test_laboratory_controller_router.mjs', 'tests/test_state_contract_browser.mjs',
        'tests/test_kelvin_voigt_contract.mjs', 'tests/test_sls_laboratory_contract.mjs',
        'tests/test_j2_contract.mjs', 'tests/test_burgers_web_contract.mjs',
        'tests/test_orthotropic_contract.mjs', 'tests/test_hill_contract.mjs',
        'tests/test_bingham_laboratory_contract.mjs')


if __name__ == '__main__':
    main()
