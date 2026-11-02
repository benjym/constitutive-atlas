#!/usr/bin/env python3
"""Generate a dedicated physical-time controlled-field catalogue."""
from pathlib import Path
import argparse,sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from atlas.controlled_time_compiler import generate
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('models',nargs='+',type=Path);a=p.parse_args();generate(a.output,a.models)
