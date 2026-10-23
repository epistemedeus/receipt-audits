#!/usr/bin/env python3
"""Q41 serial public reads. Fixed pin, cached inherited captures, bounded ranges/retries."""
import datetime as dt
import json
from pathlib import Path
import sys,time,urllib.request,urllib.error,resource
HERE=Path(__file__).resolve().parent
OLD=HERE/'inherited/q33-flapjax-20261021'
sys.path.insert(0,str(OLD/'q35-reuse'))
from evidence import PRIMARY,SECONDARY,FJ,POOL,WBNB,TREASURY,TRANSFER,SWAP,timestamp
from audit import n,address
ALLOWED={'eth_chainId','eth_getBlockByNumber','eth_call','eth_getLogs','eth_getBalance','eth_getTransactionReceipt','eth_getTransactionByHash','debug_traceTransaction'}
class RPC:
 def __init__(self):
  self.cache={};self.inherited=set();self.used=set();self.live=0
  for p in [OLD/'q35-reuse/evidence/rpc.jsonl',OLD/'evidence/rpc.jsonl',HERE/'evidence/rpc.jsonl']:
   if not p.exists():continue
   for s in p.read_text().splitlines():
    r=json.loads(s)
    if r['status']==200 and 'result' in r['response']:
     k=self.key(r['url'],r['request']['method'],r['request']['params']);self.cache[k]=r['response']['result']
     if p.parent!=HERE/'evidence':self.inherited.add(k)
 @staticmethod
 def key(u,m,p):return json.dumps([u,m,p],sort_keys=True)
 def __call__(self,m,p,u=PRIMARY,optional=False):
  assert m in ALLOWED and u in (PRIMARY,SECONDARY)
  k=self.key(u,m,p)
  # Never inherit a moving-tag observation into the new admission.
  if k in self.cache and not (m=='eth_getBlockByNumber' and p[0]=='finalized'):
   if k in self.inherited:self.used.add(k)
   return self.cache[k]
  for attempt in range(3):
   assert self.live<900,'bounded request budget exhausted'
   req={'jsonrpc':'2.0','id':1,'method':m,'params':p};at=dt.datetime.now(dt.timezone.utc).isoformat();start=time.monotonic()
   try:
    with urllib.request.urlopen(urllib.request.Request(u,data=json.dumps(req).encode(),headers={'Content-Type':'application/json','User-Agent':'Pilot-Q41-readonly'}),timeout=15) as f:status=f.status;body=f.read(16000000).decode()
   except urllib.error.HTTPError as e:status=e.code;body=e.read().decode()
   except OSError as e:status=0;body=str(e)
   try:resp=json.loads(body)
   except ValueError:resp={'transportError':body[:2000]}
   row={'at':at,'seconds':round(time.monotonic()-start,4),'url':u,'request':req,'status':status,'response':resp}
   with (HERE/'evidence/rpc.jsonl').open('a') as f:f.write(json.dumps(row,separators=(',',':'))+'\n')
   self.live+=1
   if status==200 and 'result' in resp:self.cache[k]=resp['result'];time.sleep(.08);return resp['result']
   if status in (0,429,502,503,504) or 'rate' in str(resp).lower():time.sleep(2**attempt);continue
   if optional:return None
   raise RuntimeError(str(row)[:700])
  if optional:return None
  raise RuntimeError('bounded retries exhausted: '+m)

def run():
 start=time.monotonic();rpc=RPC();pinfile=HERE/'evidence/snapshot.json'
 if pinfile.exists():pin=json.loads(pinfile.read_text())
 else:pin=rpc('eth_getBlockByNumber',['finalized',False]);pinfile.write_text(json.dumps(pin,indent=2)+'\n')
 pn=n(pin['number'])
 for u in (PRIMARY,SECONDARY):
  assert n(rpc('eth_chainId',[],u))==56
  assert rpc('eth_getBlockByNumber',[hex(pn),False],u)['hash']==pin['hash']
 def block(b,full=False):return rpc('eth_getBlockByNumber',[hex(b),full])
 def bound(date):
  t=timestamp(date);lo,hi=126000000,pn
  assert n(block(lo)['timestamp'])<t<=n(block(hi)['timestamp'])
  while lo+1<hi:
   m=(lo+hi)//2
   if n(block(m)['timestamp'])<t:lo=m
   else:hi=m
  block(hi-1);block(hi);return hi
 bounds={d:bound(d) for d in ('2026-10-09T05:00:00Z','2026-10-22T05:00:00Z')}
 (HERE/'evidence/boundaries.json').write_text(json.dumps(bounds,indent=2)+'\n');first,last=list(bounds.values());last-=1
 print('pin',pn,'window',first,last,flush=True)
 # Receive the actual historical contract configuration; preserve inherited metadata too.
 for to,selectors in [(POOL,['0x0dfe1681','0xd21220a7','0xddca3f43','0xc45a0155']),(FJ,['0x313ce567']),(WBNB,['0x313ce567'])]:
  for sel in selectors:rpc('eth_call',[{'to':to,'data':sel},hex(last)])
 # Inherited Q35 covers both token and pool to 128550459; Q33 token extension to 128867609.
 for kind,lo in [('token',128867610),('pool',128550460)]:
  for step in (50000,25000):
   count=0
   for a in range(lo,last+1,step):
    q={'address':FJ if kind=='token' else POOL,'fromBlock':hex(a),'toBlock':hex(min(a+step-1,last))}
    if kind=='token':q['topics']=[TRANSFER]
    logs=rpc('eth_getLogs',[q]);assert isinstance(logs,list) and len(logs)<1000;count+=len(logs)
   print(kind,step,count,flush=True)
 # Union old + new, keep window and canonical dedup; every partition is validated offline.
 all_logs={}
 for k,v in list(rpc.cache.items()):
  u,m,p=json.loads(k)
  if u==PRIMARY and m=='eth_getLogs':
   for l in v:
    if first<=n(l['blockNumber'])<=last:all_logs[(l['blockHash'],l['transactionHash'],l['logIndex'])]=l
 pool=[l for l in all_logs.values() if l['address'].lower()==POOL and l['topics'][0]==SWAP]
 treasury=[l for l in all_logs.values() if l['address'].lower()==FJ and any(t[-40:].lower()==TREASURY[2:] for t in l['topics'][1:])]
 hashes=sorted({l['transactionHash'] for l in pool+treasury});buys=[]
 for h in hashes:
  tx=rpc('eth_getTransactionByHash',[h]);rc=rpc('eth_getTransactionReceipt',[h]);bn=n(tx['blockNumber']);block(bn)
  relevant=[l for l in pool if l['transactionHash']==h]
  if relevant:
   for u in (SECONDARY,):
    rpc('eth_getTransactionReceipt',[h],u);rpc('eth_getTransactionByHash',[h],u);rpc('eth_getBlockByNumber',[hex(bn),False],u)
  if relevant and tx['from'].lower()==TREASURY:
   buys.append(h)
   for b in (bn-1,bn):rpc('eth_getBalance',[TREASURY,hex(b)],optional=True)
   rpc('eth_call',[{'to':POOL,'data':'0x3850c7bd'},hex(bn-1)],optional=True)
   # Full ordered block is evidence about earlier direct transactions; it is not an internal trace.
   block(bn,True)
 print('window transactions',len(hashes),'treasury pool swaps',len(buys),flush=True)
 # Probe prestate support once. A refused method is not retried at each transaction.
 trace=rpc('debug_traceTransaction',[buys[0],{'tracer':'prestateTracer','timeout':'5s','tracerConfig':{'diffMode':False}}],optional=True) if buys else None
 if trace is not None:
  for h in buys[1:]:rpc('debug_traceTransaction',[h,{'tracer':'prestateTracer','timeout':'5s','tracerConfig':{'diffMode':False}}],optional=True)
 stats={'seconds':round(time.monotonic()-start,3),'newRequestsThisInvocation':rpc.live,'inheritedCacheKeysUsed':len(rpc.used),'inheritedKeysUsed':sorted(rpc.used),'transactions':len(hashes),'treasuryPoolTransactions':buys}
 (HERE/'evidence/capture-stats.json').write_text(json.dumps(stats,indent=2)+'\n');print({k:v for k,v in stats.items() if k!='inheritedKeysUsed'})
if __name__=='__main__':
 resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));run()
