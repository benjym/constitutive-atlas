"""Run the separately frozen tighter-settings study; preserve original v1 gates."""
import hashlib
from pathlib import Path
import power_creep_study as study

study.PACKET = study.PACKET / 'refinement-v2'

if __name__ == '__main__':
    freeze = study.read(study.PACKET / 'freeze.json')
    key = 'frozen/source/tools/power_creep_refined_study.py'
    if hashlib.sha256(Path(__file__).read_bytes()).hexdigest() != freeze['files'][key]:
        raise ValueError('Refined study wrapper differs from its frozen copy')
    study.main()
