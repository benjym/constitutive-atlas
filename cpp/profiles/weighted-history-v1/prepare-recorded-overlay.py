"""Reconstruct the reviewed controller only inside the weighted build."""
import hashlib
from pathlib import Path
import subprocess
import sys

root=Path(__file__).resolve().parents[3]
baseline=root/'cpp/include/atlas/recorded.hpp'
patched=Path(sys.argv[1]).resolve()/'overlay/atlas/recorded.hpp'
sha=lambda path:hashlib.sha256(path.read_bytes()).hexdigest()
if sha(baseline)!="e6c17c848a3b89ab0fee43160320f5c6f1160f146be5a74c72c8ddb5c6c43b01":
    raise ValueError("Weighted profile needs the reviewed baseline controller.")
patched.parent.mkdir(parents=True,exist_ok=True)
subprocess.run(["patch","--silent","-o",str(patched),str(baseline),str(Path(__file__).with_name("recorded-controls.patch"))],check=True)
if sha(patched)!="d0cfa06dd89152db25a97e28daa7769d4f21b95d50f6cf918d708a9e22afe989":
    raise ValueError("Reconstructed weighted profile controller differs from the reviewed bytes.")
