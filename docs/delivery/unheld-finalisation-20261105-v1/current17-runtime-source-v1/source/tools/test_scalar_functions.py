"""Run the independent391case scalar/Jet qualification, retaining failures."""
from pathlib import Path
import argparse,subprocess,sys,tempfile,shutil
p=Path(__file__).resolve().parent
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('library')
parser.add_argument('--output-dir',type=Path,help='Fresh directory; retains successful and failed evidence')
a=parser.parse_args()
if a.output_dir is None:d=Path(tempfile.mkdtemp(prefix='atlas-scalar-functions-'))
else:
 d=a.output_dir;d.mkdir(parents=True,exist_ok=False)
try:
 subprocess.run([sys.executable,str(p/'collect_scalar_functions.py'),a.library,str(d/'raw.json')],check=True)
 subprocess.run([sys.executable,str(p/'check_scalar_functions.py'),str(d/'raw.json'),str(d/'assessment.json')],check=True)
except BaseException:
 print('Scalar qualification failure evidence retained at '+str(d.resolve()),file=sys.stderr)
 raise
else:
 if a.output_dir is None:shutil.rmtree(d)
 else:print('Scalar qualification evidence retained at '+str(d.resolve()))
