#!/usr/bin/env python3
"""Extend the original audit without rewriting its packet bytes."""
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
import audit
if __name__=='__main__':
 audit.TARGETS.append('catalogue/laboratory-control-support.json')
 audit.run(Path(__file__).parent)
