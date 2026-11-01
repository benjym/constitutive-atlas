"""Restore the single exact public JSON witness required by frozen interface guards."""
from pathlib import Path
import hashlib

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[4]
RELATIVE = '.local/lade-outer-predictor-v1/native-fixed-requests/dense-0.005-400.json'
EXPECTED = 'ee7e4ad4b34c14843c6f7d0b2d66a936d8c8409fa1e2dc2c493949a9411589f9'
data = (HERE / 'interface-request.json').read_bytes()
if hashlib.sha256(data).hexdigest() != EXPECTED:
    raise ValueError('Changed frozen interface witness')
target = ROOT / RELATIVE
if target.resolve().is_relative_to(ROOT.resolve()) is False:
    raise ValueError('Unsafe interface witness destination')
if target.exists() and target.read_bytes() != data:
    raise ValueError('Existing interface witness differs')
target.parent.mkdir(parents=True, exist_ok=True)
target.write_bytes(data)
print('Restored exact frozen interface JSON witness')
