"""Run exact copied mocked harness, retaining production read-only roots."""
import pathlib,sys,importlib.util,runpy
P=pathlib.Path(__file__).parent;R=pathlib.Path('/Users/bmar5496/code/constitutive-atlas');C=R/'docs/reviews/mc-current-collector-freeze-v3'
sys.path.insert(0,str(C))
def load(name):
 s=importlib.util.spec_from_file_location(name,P/'reviewed'/f'{name}.py');m=importlib.util.module_from_spec(s);sys.modules[name]=m;s.loader.exec_module(m);return m
# Imports define functions only; actual subprocess.run is patched by the harness.
driver=load('execute');driver.R=R;driver.C=C
compat=load('assess_compatibility');compat.R=R;compat.C=C;compat.P=P
runpy.run_path(str(P/'reviewed/check_driver.py'),run_name='__audit_mocked_harness__')
