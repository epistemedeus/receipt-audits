#!/usr/bin/env python3
"""Verify the delivered file allowlist/checksums and optional cold output bytes."""
import argparse
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent
def main():
 p=argparse.ArgumentParser();p.add_argument('--replayed',type=Path);a=p.parse_args()
 files=(HERE/'FILES.txt').read_text().splitlines()
 assert files==sorted(set(files)),'duplicate or unordered allowlist'
 for name in files:
  path=Path(name);assert not path.is_absolute() and '..' not in path.parts,'unsafe manifest path'
  assert (HERE/path).is_file() and not (HERE/path).is_symlink(),'missing delivered file'
 checks={}
 for line in (HERE/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split('  ',1);assert name not in checks,'duplicate checksum';checks[name]=digest
 assert set(checks)==set(files)-{'SHA256SUMS'},'checksum/allowlist mismatch'
 for name,digest in checks.items():assert hashlib.sha256((HERE/name).read_bytes()).hexdigest()==digest,'checksum mismatch: '+name
 print('PASS:',len(files),'delivered paths and SHA-256 checksums')
 if a.replayed:
  names=['PUBLIC-AUDIT.md']+[str(x.relative_to(HERE)) for x in sorted((HERE/'derived').glob('*')) if x.is_file()]
  for name in names:
   target=a.replayed/name.removeprefix('derived/')
   assert target.read_bytes()==(HERE/name).read_bytes(),'cold bytes differ: '+name
   print('BYTE_IDENTICAL',name)
if __name__=='__main__':main()
