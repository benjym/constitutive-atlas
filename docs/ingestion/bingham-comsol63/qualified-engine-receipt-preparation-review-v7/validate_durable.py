"""Exact production validate path; actual saved inputs; writes and processes blocked."""
from pathlib import Path
import importlib.util,json,subprocess
from unittest.mock import patch,DEFAULT
P=Path('/private/tmp/atlas-time-profile-v2/docs/ingestion/bingham-comsol63/qualified-engine-receipt-preparation-v7');ROOT=P.parents[3];RELEASE=Path('/private/tmp/atlas-bingham-release-v2')
spec=importlib.util.spec_from_file_location('reviewed_v7',P/'compose.py');c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
S=ROOT/'docs/ingestion/bingham-comsol63/execution-v5/qualified-engine-input-spec-v2-durable.json'
assert c.sha(S.read_bytes())=='01c42780cd1f2ee08b28dd007375ec2c32772bf6de2b2d70796a57ee0385c06c'
with patch.multiple(subprocess,run=DEFAULT,Popen=DEFAULT,check_call=DEFAULT,check_output=DEFAULT,call=DEFAULT) as mocks,patch.object(Path,'mkdir',side_effect=AssertionError('Unexpected output directory write')),patch.object(Path,'write_bytes',side_effect=AssertionError('Unexpected asset write')),patch.object(Path,'write_text',side_effect=AssertionError('Unexpected text write')):
 for v in mocks.values():v.side_effect=AssertionError('No process/material execution')
 result=c.compose(json.loads(S.read_text()),ROOT,RELEASE,None)
 for v in mocks.values():v.assert_not_called()
assert result['validated'] and result['files_written']==0 and result['input_roles']==53 and not result['E5_acceptance_claimed']
Path(__file__).with_name('DURABLE-VALIDATE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
