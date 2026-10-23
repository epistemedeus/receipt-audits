#!/usr/bin/env python3
"""One serial, no-network receiver for the exact public evidence package."""
import argparse,datetime as dt,json,os,resource,subprocess,sys,time
from pathlib import Path
from verify import HERE,verify

def main():
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE/'replayed');a=p.parse_args();out=a.out.resolve();out.mkdir(parents=True,exist_ok=True)
 assert out!=HERE and out not in HERE.parents,'output must not replace the package or an ancestor'
 start=time.monotonic();verify();old=HERE/'inherited/q33-flapjax-20261021';q35=old/'q35-reuse';steps=[]
 def run(args,cwd=HERE,save=None):
  t=time.monotonic()
  def bounds():
   if args[0]!='node':resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,)*2)
  env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
  # V8 reserves virtual arenas larger than its resident heap. A virtual-address
  # cap rejected the unchanged Q33 decoder despite low actual memory use.
  # This finite receiver bounds child RSS, with no resident background monitor.
  proc=subprocess.Popen(args,cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,preexec_fn=bounds)
  peak=0
  try:
   while True:
    try:
     status=Path(f'/proc/{proc.pid}/status').read_text()
     rss=next((int(line.split()[1]) for line in status.splitlines() if line.startswith('VmRSS:')),0)
     peak=max(peak,rss)
     if rss>768*1024:raise RuntimeError('child exceeds finite 768 MiB RSS budget')
    except FileNotFoundError:pass
    if time.monotonic()-t>45:raise TimeoutError('bounded child exceeded 45 seconds')
    try:stdout,_=proc.communicate(timeout=.05);break
    except subprocess.TimeoutExpired:continue
  except BaseException:
   proc.kill();proc.communicate();raise
  name=f'{len(steps)+1:02}.log';(out/name).write_text(stdout)
  steps.append({'argv':[str(x) for x in args],'cwd':str(cwd.relative_to(HERE)) if cwd!=HERE else '.','seconds':round(time.monotonic()-t,4),'exit':proc.returncode,'sampledPeakRSSKiB':peak,'log':name})
  if proc.returncode:print(stdout);raise RuntimeError('serial verification failed: '+str(args))
  if save:save.write_text(stdout)
  print('PASS',len(steps),Path(str(args[1])).name if len(args)>1 else str(args),flush=True)
 # Retained exact packages, including their independent decoders and original report/table equality.
 py=sys.executable
 run([py,'verify.py'],old)
 run([py,'audit.py','--out',str(out/'q35')],q35)
 run(['node','--max-old-space-size=128','cold-independent.mjs','evidence',str(out/'q35')],q35)
 run([py,'render.py','--derived',str(out/'q35'),'--out',str(out/'q35/PUBLIC-AUDIT.md')],q35)
 run([py,'verify.py','--replayed',str(out/'q35')],q35)
 run([py,'-m','unittest','discover','-s','.','-p','test_audit.py','-v'],q35)
 run([py,'q33.py','--out',str(out/'q33')],old)
 run([py,'render.py','--out',str(out/'q33/PUBLIC-AUDIT.md')],old)
 run(['node','--max-old-space-size=128','independent.mjs','evidence',str(out/'q33/summary.json')],old)
 run([py,'verify.py','--replayed',str(out/'q33')],old)
 run([py,'-m','unittest','discover','-s','.','-p','test_q33.py','-v'],old)
 run([py,'q41.py','--out',str(out)])
 run([py,'render.py','--summary',str(out/'summary.json'),'--out',str(out/'PUBLIC-AUDIT.md')])
 run(['node','--max-old-space-size=128','independent.mjs',str(out/'summary.json')],save=out/'independent.json')
 run([py,'-m','unittest','discover','-s','.','-p','test_q41.py','-v'])
 compared=[]
 for f in sorted((HERE/'derived').glob('*')):
  assert f.read_bytes()==(out/f.name).read_bytes(),'cold bytes differ: '+f.name;compared.append('derived/'+f.name)
 assert (HERE/'PUBLIC-AUDIT.md').read_bytes()==(out/'PUBLIC-AUDIT.md').read_bytes();compared.append('PUBLIC-AUDIT.md')
 receipt={'at':dt.datetime.now(dt.timezone.utc).isoformat(),'seconds':round(time.monotonic()-start,4),'steps':steps,'serial':True,'modelChildren':0,'tests':{'Q35':11,'Q33':21,'Q41':22},'byteIdentical':compared,'childPeakRSSKiB':resource.getrusage(resource.RUSAGE_CHILDREN).ru_maxrss,'parentPeakRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'networkCommands':0}
 (out/'verification.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:v for k,v in receipt.items() if k!='steps'},indent=2))
if __name__=='__main__':main()
