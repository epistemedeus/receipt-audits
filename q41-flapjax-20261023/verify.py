#!/usr/bin/env python3
import hashlib
from pathlib import Path
HERE=Path(__file__).resolve().parent

def verify():
 names=(HERE/'PUBLIC-FILES.txt').read_text().splitlines();assert names==sorted(set(names))
 checks={}
 for line in (HERE/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split('  ',1);assert name not in checks;checks[name]=digest
 assert set(checks)==set(names)-{'SHA256SUMS'}
 for name in names:
  p=Path(name);assert not p.is_absolute() and '..' not in p.parts and (HERE/p).is_file() and not (HERE/p).is_symlink()
  if name!='SHA256SUMS':assert hashlib.sha256((HERE/p).read_bytes()).hexdigest()==checks[name],name
 print('PASS',len(names),'public-package members and SHA-256 checksums')
if __name__=='__main__':verify()
