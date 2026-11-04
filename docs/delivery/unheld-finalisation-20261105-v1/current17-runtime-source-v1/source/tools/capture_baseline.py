"""Build/check a fresh committed-source export and retain its baseline record."""
import argparse
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from atlas.baseline import capture, verify


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref',default='HEAD',help='Committed revision to export; uncommitted files are excluded')
    parser.add_argument('--output',type=Path,help='New output directory; an existing baseline is never overwritten')
    parser.add_argument('--verify',type=Path,help='Check an existing manifest and retained artifact hashes without executing commands')
    args=parser.parse_args()
    if args.verify:
        if args.output: parser.error('--verify and --output are mutually exclusive')
        record=verify(args.verify)
        print(f"{record['id']}: integrity verified; recorded outcome {record['outcome']}; no scientific review claim")
    else:
        if not args.output: parser.error('--output is required when capturing a baseline')
        print(capture(args.ref,args.output))


if __name__=='__main__':main()
