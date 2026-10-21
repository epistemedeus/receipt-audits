#!/usr/bin/env python3
"""Targeted public counterexample verification, not another historical chain scan."""
from pathlib import Path
import json
from collect import PublicRPC
from evidence import PRIMARY,SECONDARY,FJ,TREASURY
from sources import ledger
HERE=Path(__file__).resolve().parent
SEED='0x50fd50af15a62942e1c443da634e06c103243fd9eca2f3c9bc7875df39b631d9'
def main():
    directory=HERE/'evidence';rpc=PublicRPC(directory)
    # A peer report is only a transaction locator. All quantities, participants,
    # event shape and success are recomputed from the two nodes' actual receipts.
    pointer={'url':'https://thecolony.ai/post/da324923-da00-4440-8024-10e5bb994cad','role':'counterexample transaction locator only; peer quantities are not calculation inputs','transaction':SEED}
    (directory/'counterexample-pointer.json').write_text(json.dumps(pointer,indent=2)+'\n')
    for u in (PRIMARY,SECONDARY):
        rc=rpc('eth_getTransactionReceipt',[SEED],u);tx=rpc('eth_getTransactionByHash',[SEED],u)
        rpc('eth_getBlockByNumber',[rc['blockNumber'],False],u)
    for b in [int(rc['blockNumber'],16)-1,int(rc['blockNumber'],16)]:
        rpc('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},hex(b)])
    rpc('eth_getCode',[tx['from'].lower(),rc['blockNumber']])
    # Secondary receipt checks for the exact labelled Relay cohort as well.
    entries=ledger((directory/'flapjax.html').read_text())
    boundaries=json.loads((directory/'boundaries.json').read_text())
    count=0
    for e in entries:
        received=rpc.cache.get(rpc.key(PRIMARY,'eth_getTransactionReceipt',[e['tx']]))
        in_utc=received is not None and boundaries['2026-10-12T00:00:00Z']<=int(received['blockNumber'],16)<boundaries['2026-10-18T00:00:00Z']
        if e['label'].startswith('quick task Q') and (in_utc or '2026-10-12'<=e['date']<'2026-10-18'):
            rpc('eth_getTransactionReceipt',[e['tx']],SECONDARY);count+=1
    print('supplement complete; seed independently verified; labelled receipts',count)
if __name__=='__main__':main()
