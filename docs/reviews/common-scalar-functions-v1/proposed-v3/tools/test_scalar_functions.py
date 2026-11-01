"""Run the frozen391case independent scalar/Jet qualification against a native library."""
from pathlib import Path
import subprocess,sys,tempfile
p=Path(__file__).resolve().parent
with tempfile.TemporaryDirectory(prefix='atlas-scalar-functions-') as directory:
 d=Path(directory)
 subprocess.run([sys.executable,str(p/'collect_scalar_functions.py'),sys.argv[1],str(d/'raw.json')],check=True)
 subprocess.run([sys.executable,str(p/'check_scalar_functions.py'),str(d/'raw.json'),str(d/'assessment.json')],check=True)
