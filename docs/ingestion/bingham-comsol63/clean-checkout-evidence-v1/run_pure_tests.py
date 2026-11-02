"""Named catalogue/export tests; child/tool/material processes prohibited."""
from pathlib import Path
import json,os,subprocess,sys,unittest
from unittest.mock import patch
root=Path(sys.argv[1]).resolve();sys.path.insert(0,str(root));modules=['tests.test_catalogue','tests.test_agent_review','tests.test_agent_review_export','tests.test_approved_export','tests.test_build_evidence','tests.test_screening_export','tests.test_research_evidence','tests.test_agent_review_archives'];calls=[]
def blocked(*a,**kw):calls.append(1);raise AssertionError('Child/tool/material execution forbidden')
patches=[patch.object(owner,name,blocked) for owner,name in [(subprocess,'Popen'),(subprocess,'run'),(subprocess,'check_call'),(subprocess,'check_output'),(os,'system'),(os,'posix_spawn')]]
for p in patches:p.start()
try:
 suite=unittest.defaultTestLoader.loadTestsFromNames(modules);result=unittest.TextTestRunner(verbosity=2).run(suite)
finally:
 for p in reversed(patches):p.stop()
report={'passed':result.wasSuccessful() and not calls,'tests':result.testsRun,'modules':modules,'failures':len(result.failures),'errors':len(result.errors),'compiler_material_subprocess_calls':len(calls)};print(json.dumps(report,indent=2));Path(sys.argv[2]).write_text(json.dumps(report,indent=2)+'\n');sys.exit(0 if report['passed'] else 1)
