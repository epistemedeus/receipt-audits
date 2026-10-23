#!/usr/bin/env python3
"""Bounded public Q33 capture; standard library only, no signer or account state."""
import datetime as dt
import json
from pathlib import Path
import sys
import time
import urllib.request
import urllib.error
sys.path.insert(0,str(Path(__file__).resolve().parent/'q35-reuse'))
from evidence import PRIMARY, SECONDARY, FJ, POOL, TREASURY, TRANSFER, timestamp

HERE=Path(__file__).resolve().parent
class PublicRPC:
    ALLOWED={'eth_chainId','eth_getBlockByNumber','eth_call','eth_getCode','eth_getLogs','eth_getTransactionReceipt','eth_getTransactionByHash','nr_getTokenHolders','nr_getTokenHolderCount'}
    def __init__(self,directory):
        self.path=directory/'rpc.jsonl';self.cache={}
        if self.path.exists():
            for line in self.path.read_text().splitlines():
                r=json.loads(line)
                if r['status']==200 and 'result' in r['response']:
                    self.cache[self.key(r['url'],r['request']['method'],r['request']['params'])]=r['response']['result']
    @staticmethod
    def key(url,method,params):return json.dumps([url,method,params],sort_keys=True)
    def __call__(self,method,params,url=PRIMARY):
        if method not in self.ALLOWED or url not in (PRIMARY,SECONDARY):raise ValueError('read-only route refused')
        key=self.key(url,method,params)
        if key in self.cache:return self.cache[key]
        for attempt in range(4):
            req={'jsonrpc':'2.0','id':1,'method':method,'params':params};at=dt.datetime.now(dt.timezone.utc).isoformat()
            try:
                with urllib.request.urlopen(urllib.request.Request(url,data=json.dumps(req).encode(),headers={'Content-Type':'application/json','User-Agent':'Pilot-Q33-readonly'}),timeout=15) as f:status=f.status;body=f.read().decode()
            except urllib.error.HTTPError as e:status=e.code;body=e.read().decode()
            except OSError as e:status=0;body=str(e)
            try:response=json.loads(body)
            except ValueError:response={'transportError':body[:2000]}
            with self.path.open('a') as f:f.write(json.dumps({'at':at,'url':url,'request':req,'status':status,'response':response},separators=(',',':'))+'\n')
            if status==200 and 'result' in response:
                self.cache[key]=response['result'];time.sleep(.10);return response['result']
            if status in (0,429,502,503,504) or 'rate' in str(response).lower():time.sleep(min(2**attempt,8));continue
            raise RuntimeError(f'{method}: {status} {str(response)[:300]}')
        raise RuntimeError(f'{method}: exhausted bounded retries')

def capture(directory):
    directory.mkdir(parents=True,exist_ok=True);rpc=PublicRPC(directory)
    # Preserve the admission's actual finalized observation across resumptions.
    pin=json.loads((directory/'probe-eth_getBlockByNumber.json').read_text())['response']['result'];bn=int(pin['number'],16);tag=hex(bn)
    assert int(rpc('eth_chainId',[]),16)==56
    assert int(rpc('eth_chainId',[],SECONDARY),16)==56
    assert rpc('eth_getBlockByNumber',[tag,False])['hash']==pin['hash']
    assert rpc('eth_getBlockByNumber',[tag,False],SECONDARY)['hash']==pin['hash']
    (directory/'snapshot.json').write_text(json.dumps(pin,indent=2)+'\n')
    pages=[];key='';seen=set()
    for i in range(10):
        assert key not in seen,'index cursor loop';seen.add(key)
        page=rpc('nr_getTokenHolders',[FJ,'0x64',key]);pages.append(page);key=page.get('pageKey','')
        if not key:break
    else:raise ValueError('holder index exceeds bounded ten-page capture')
    holders=sorted({d['accountAddress'].lower() for p in pages for d in p['details']})
    print('index pages',len(pages),'candidates',len(holders),flush=True)
    for selector in ('0x313ce567','0x18160ddd','0x95d89b41','0x06fdde03'):rpc('eth_call',[{'to':FJ,'data':selector},tag])
    for i,a in enumerate(sorted(set(holders+[TREASURY]))):
        rpc('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag])
        if i%50==0:print('balances',i,flush=True)
    def balance(a):return int(rpc('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag]),16)
    top=sorted(holders,key=lambda a:(-balance(a),a))[:10]
    def optional(method,params,url=SECONDARY):
        try:return rpc(method,params,url)
        except RuntimeError as e:print('independent state unavailable',str(e)[:130],flush=True)
    for a in top+[TREASURY]:
        rpc('eth_getCode',[a,tag]);optional('eth_getCode',[a,tag])
        optional('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag])
    optional('eth_call',[{'to':FJ,'data':'0x18160ddd'},tag])
    for a in top:
        if rpc('eth_getCode',[a,tag])=='0x':continue
        # Roles remain unknown when a standard pool interface does not respond.
        pool_interface=True
        for s in ('0x0dfe1681','0xd21220a7','0xddca3f43','0xc45a0155'):
            try:rpc('eth_call',[{'to':a,'data':s},tag])
            except RuntimeError as e:
                pool_interface=False
                print('role probe unavailable',a,s,str(e)[:80],flush=True)
        if not pool_interface:continue
        from audit import address
        t0=address(rpc('eth_call',[{'to':a,'data':'0x0dfe1681'},tag]))
        t1=address(rpc('eth_call',[{'to':a,'data':'0xd21220a7'},tag]))
        fee=int(rpc('eth_call',[{'to':a,'data':'0xddca3f43'},tag]),16)
        factory=address(rpc('eth_call',[{'to':a,'data':'0xc45a0155'},tag]))
        args=t0[2:].rjust(64,'0')+t1[2:].rjust(64,'0')+hex(fee)[2:].rjust(64,'0')
        rpc('eth_call',[{'to':factory,'data':'0x1698ee82'+args},tag])
    blocks={}
    def block(n):
        if n not in blocks:blocks[n]=rpc('eth_getBlockByNumber',[hex(n),False])
        return blocks[n]
    def lower_bound(t):
        lo,hi=bn-6_000_000,bn
        assert int(block(lo)['timestamp'],16)<t<=int(block(hi)['timestamp'],16)
        while lo+1<hi:
            m=(lo+hi)//2
            if int(block(m)['timestamp'],16)<t:lo=m
            else:hi=m
        block(hi-1);block(hi);return hi
    dates=['2026-10-01T00:00:00Z','2026-10-12T00:00:00Z','2026-10-18T00:00:00Z']
    bounds={d:lower_bound(timestamp(d)) for d in dates}
    (directory/'boundaries.json').write_text(json.dumps(bounds,indent=2)+'\n')
    # Reuse the received Q35 partitions. Capture only the two disjoint extensions.
    first,last=bounds[dates[0]],bn
    old_first,old_last=126424183,128550459
    for lo,hi in ((first,old_first-1),(old_last+1,last)):
        for step in (50000,25000):
            total=0
            for a in range(lo,hi+1,step):
                b=min(a+step-1,hi)
                logs=rpc('eth_getLogs',[{'address':FJ,'topics':[TRANSFER],'fromBlock':hex(a),'toBlock':hex(b)}]);assert isinstance(logs,list) and len(logs)<1000,'possible log cap';total+=len(logs)
            print('extension',lo,hi,step,'logs',total,flush=True)
    # Classify using actual transaction/receipt evidence, not amount heuristics.
    from evidence import load_capture
    old=load_capture(HERE/'q35-reuse/evidence/rpc.jsonl')['scans']['token']['50000']['logs']
    logs=list(old)
    for k,v in rpc.cache.items():
        u,m,p=json.loads(k)
        if u==PRIMARY and m=='eth_getLogs':logs.extend(v)
    treasury=[l for l in logs if any(t[-40:].lower()==TREASURY[2:] for t in l['topics'][1:])]
    for a in sorted({'0x'+l['topics'][2][-40:] for l in treasury}):
        rpc('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag])
    rpc('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},hex(first-1)])
    hashes=sorted({l['transactionHash'] for l in treasury})
    for i,h in enumerate(hashes):
        tx=rpc('eth_getTransactionByHash',[h]);rc=rpc('eth_getTransactionReceipt',[h]);block(int(rc['blockNumber'],16))
        # Secondary receipts for every treasury inflow and labelled Relay payout.
        incoming=any(l['transactionHash']==h and l['topics'][2][-40:].lower()==TREASURY[2:] for l in treasury)
        if incoming:rpc('eth_getTransactionReceipt',[h],SECONDARY)
        if i%50==0:print('treasury receipts',i,'/',len(hashes),flush=True)
    print('capture complete',len(hashes),'treasury transactions',flush=True)
if __name__=='__main__':capture(HERE/'evidence')
