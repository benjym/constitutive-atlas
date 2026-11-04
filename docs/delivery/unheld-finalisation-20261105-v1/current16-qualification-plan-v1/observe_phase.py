"""Thin existing-observer adapter. Import is inert; coordinator owns handoff and explicit calls."""
from pathlib import Path
import hashlib,importlib.util,sys
sys.dont_write_bytecode=True
import commands as C
OBSERVER=C.P.parents[1]/'unheld-finalisation-20261102-v1/baseline-five-host-context-dispatch-v3/proposed/tools/baseline_observe_child_v3.py'
OBSERVER_SHA='7328ba854ba75a85dc66fd29aa65c4166d252a5361886920fb67a5c6d788e60e'

def closed_environment():
 temp=C.WORK
 return {'PATH':'/opt/homebrew/bin:/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin','HOME':str(temp/'env-home'),'XDG_CONFIG_HOME':str(temp/'env-xdg'),'TMPDIR':str(temp/'env-tmp'),'LC_ALL':'C','TZ':'UTC','PYTHONDONTWRITEBYTECODE':'1','PYTHONNOUSERSITE':'1','PYTHONHASHSEED':'0','GIT_CONFIG_NOSYSTEM':'1','GIT_CONFIG_SYSTEM':'/dev/null','GIT_CONFIG_GLOBAL':'/dev/null','GIT_CONFIG_COUNT':'0','GIT_ATTR_NOSYSTEM':'1','GIT_NO_REPLACE_OBJECTS':'1','GIT_OPTIONAL_LOCKS':'0','GIT_TERMINAL_PROMPT':'0'}

def observe_phase(pre,phase):
 """Call only under independent accepted plan + fresh parent serial claim; first failure raises."""
 argv=C.phase_argv(pre)[phase]
 assert hashlib.sha256(OBSERVER.read_bytes()).hexdigest()==OBSERVER_SHA
 spec=importlib.util.spec_from_file_location('unchanged_current16_observer',OBSERVER);observer=importlib.util.module_from_spec(spec);spec.loader.exec_module(observer)
 result=observer.observe(argv,str(C.SOURCE),C.P/('outer-'+phase+'-v1'),env=closed_environment(),timeout=1800)
 assert result.returncode==0,'first failure retained; no later phase authorized'
 return result
