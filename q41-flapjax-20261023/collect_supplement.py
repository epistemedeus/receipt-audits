#!/usr/bin/env python3
"""Receive native-flow traces for the 12 discovered swaps, fixed immutable hashes."""
import json,time,resource,urllib.request
from collect import HERE,RPC,PRIMARY,SECONDARY,TREASURY

def run():
 start=time.monotonic();r=RPC();hashes=json.loads((HERE/'evidence/capture-stats.json').read_text())['treasuryPoolTransactions']
 for h in hashes:r('debug_traceTransaction',[h,{'tracer':'callTracer','timeout':'5s'}],optional=True)
 # Secondary availability probe is bounded; archive refusal is preserved.
 h=hashes[0];tx=r('eth_getTransactionByHash',[h]);tag=hex(int(tx['blockNumber'],16)-1)
 r('eth_getBalance',[TREASURY,tag],SECONDARY,optional=True)
 r('debug_traceTransaction',[h,{'tracer':'prestateTracer','timeout':'5s','tracerConfig':{'diffMode':False}}],SECONDARY,optional=True)
 print(json.dumps({'seconds':round(time.monotonic()-start,3),'liveRequests':r.live,'peakRSSKiB':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}))
if __name__=='__main__':
 resource.setrlimit(resource.RLIMIT_AS,(512*1024**2,512*1024**2));run()
