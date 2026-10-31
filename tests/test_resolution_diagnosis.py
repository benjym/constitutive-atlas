import gzip
import hashlib
import json
import math
from pathlib import Path
import unittest
import tempfile
from tests.historical_sources import pinned_source
from tools.diagnose_dp_recorded_apex import analyse
ROOT=Path(__file__).resolve().parents[1]
EVIDENCE=ROOT/'catalogue/investigations/recorded-resolution-diagnosis-v1'

class ResolutionDiagnosisTests(unittest.TestCase):
    def test_igs_error_barriers_are_admissible_history_rejections(self):
        with gzip.open(EVIDENCE/'igs-depth.json.gz','rt') as f:report=json.load(f)
        for path,key in [('models/hypoplastic-sand-igs97.json','model_sha256'),('cpp/include/atlas/solver.hpp','solver_sha256'),('tools/diagnose_igs_recorded_depth.py','script_sha256')]:
            self.assertEqual(hashlib.sha256(pinned_source(ROOT,path,report[key]).read_bytes()).hexdigest(),report[key])
        for case,expected in zip(report['cases'],[15,20,19]):
            end=case['depths'][case['max_depth']]
            self.assertTrue(end['stages_admissible'])
            self.assertEqual(end['worst_component'],'h_xx')
            self.assertGreater(end['max_scaled_error'],case['rate_tolerance'])
            self.assertTrue(all(stage['admissible'] and stage['finite_rate'] for stage in end['stages']))
            self.assertEqual(next(row['depth'] for row in case['depths'] if row.get('passes_local_error')),expected)
            errors=end['component_errors']
            self.assertEqual(end['max_scaled_error'],max(row['scaled_max'] for row in errors))

    def test_native_material_depth_probes_change_only_depth(self):
        before=json.loads((EVIDENCE/'original-igs-material-probes.json').read_text())
        after=json.loads((EVIDENCE/'igs-native-depth-probes.json').read_text())
        for old,new,expected in zip(before,after['runs'],[15,20,19],strict=True):
            self.assertFalse(old['response']['ok']);self.assertTrue(new['response']['ok'])
            self.assertEqual(old['case'],new['case']);self.assertEqual(old['factor'],new['factor'])
            args=old['argv'].copy();index=args.index('--integration-settings')+1
            settings=args[index].split(',');settings[3]=str(expected);args[index]=','.join(settings)
            self.assertEqual(args,new['argv'])
            response=new['response'];d=response['diagnostics'];self.assertEqual(new['returncode'],0)
            self.assertEqual(response['integration_settings']['max_depth'],expected)
            self.assertEqual(d['substeps'],len(d['increment_fractions']))
            self.assertAlmostEqual(sum(d['increment_fractions']),1,places=14)
            self.assertLessEqual(d['substeps'],response['integration_settings']['max_substeps'])
            self.assertTrue(all(math.isfinite(x) for x in response['state']))
            self.assertNotEqual(response['state'],old['response']['state'])

    def test_dp_independent_apex_reconstruction(self):
        retained=json.loads((EVIDENCE/'dp-apex.json').read_text())
        # Reconstruct the historical diagnostic from its original model/report.
        # The current DP domain revision is tested separately.
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name, pin in [(retained['model_path'],retained['model_sha256']),
                              (retained['report_path'],retained['report_sha256'])]:
                target=root/name;target.parent.mkdir(parents=True,exist_ok=True)
                target.write_bytes(pinned_source(ROOT,name,pin).read_bytes())
            result=analyse(root)
        self.assertEqual(result,retained)
        self.assertEqual([row['factor'] for row in result['cases']],[1,2,4])
        for row in result['cases']:
            self.assertEqual(row['independent_scalar_return']['branch'],'apex')
            self.assertEqual(row['analytical_apex_jacobian'],[[0,0],[0,0]])
            self.assertNotEqual(row['elastic_seed_scalar_return']['branch'],'apex')
            target=row['target_record'][2]
            self.assertAlmostEqual(row['independently_bracketed_radial_root']['scalar_return']['stress'][1],target,places=6)

if __name__=='__main__':unittest.main()
