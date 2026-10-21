#!/usr/bin/env python3
"""Offline view of the recorded public RPC journal; no network/umbrella imports."""
import datetime as dt
import json
from pathlib import Path

PRIMARY = 'https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3'
SECONDARY = 'https://bsc-dataseed.bnbchain.org'
FJ = '0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df'
POOL = '0xca93ec685b8623688e6b236f9068034b298c2150'
WBNB = '0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c'
TREASURY = '0x7c34e9e21ee28a49ff0b84b61774119e6633359f'
TRANSFER = '0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef'
SWAP = '0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83'
# Original capture completion time, not the time of an offline replay.
CAPTURED_AT = '2026-10-20T13:20:33.138866+00:00'
BOUNDARY_DATES = (
    '2026-10-08T10:00:00Z', '2026-10-09T00:00:00Z',
    '2026-10-09T04:00:00Z', '2026-10-09T05:00:00Z',
    '2026-10-19T00:00:00Z', '2026-10-19T04:00:00Z',
    '2026-10-19T05:00:00Z', '2026-10-19T12:00:00Z',
)

def timestamp(s):
    return int(dt.datetime.fromisoformat(s.replace('Z', '+00:00')).timestamp())

def load_capture(journal):
    """Reconstruct the received aggregate solely from successful saved requests.

    No expected transaction list or total selects results. Missing queries and
    contradictory repeat responses fail; the original validator checks coverage,
    header adjacency, receipts and both providers after reconstruction.
    """
    records = [json.loads(line) for line in Path(journal).read_text().splitlines()]
    good = {}
    for r in records:
        if r['status'] != 200 or 'result' not in r['response']:
            continue  # Failed/rate-limited requests are retained, never zero logs.
        key = (r['url'], r['request']['method'], json.dumps(r['request']['params'], sort_keys=True))
        result = r['response']['result']
        if key in good and good[key] != result:
            raise ValueError('contradictory saved RPC responses')
        good[key] = result
    def get(method, params, url=PRIMARY):
        key = (url, method, json.dumps(params, sort_keys=True))
        if key not in good:
            raise ValueError('absent saved RPC evidence: ' + method)
        return good[key]
    chain_id = int(get('eth_chainId', []), 16)
    if chain_id != 56 or int(get('eth_chainId', [], SECONDARY), 16) != 56:
        raise ValueError('wrong network in saved RPC evidence')
    blocks = {}
    for (url, method, encoded), value in good.items():
        params = json.loads(encoded)
        if url == PRIMARY and method == 'eth_getBlockByNumber' and params[0].startswith('0x'):
            blocks[str(int(params[0], 16))] = value
    boundaries = {}
    for date in BOUNDARY_DATES:
        eligible = [int(k) for k,v in blocks.items() if int(v['timestamp'],16) >= timestamp(date)]
        if not eligible:
            raise ValueError('absent boundary header')
        boundaries[date] = min(eligible)
    first = boundaries[BOUNDARY_DATES[0]]
    last = boundaries[BOUNDARY_DATES[-1]] - 1
    scans = {}
    for name, filt in [('token', {'address':FJ,'topics':[TRANSFER]}), ('pool', {'address':POOL})]:
        scans[name] = {}
        for step in (50000,25000):
            logs, ranges = [], []
            for a in range(first,last+1,step):
                b = min(a+step-1,last)
                found = get('eth_getLogs', [{**filt,'fromBlock':hex(a),'toBlock':hex(b)}])
                if not isinstance(found,list):
                    raise ValueError('invalid saved log response')
                logs.extend(found)
                ranges.append([a,b,len(found)])
            scans[name][str(step)] = {'ranges':ranges,'logs':logs}
    txhashes = sorted({x['transactionHash'] for x in scans['pool']['50000']['logs'] if x['topics'][0] == SWAP})
    transactions, receipts, secondary, balances = {}, {}, {}, {}
    for h in txhashes:
        tx = get('eth_getTransactionByHash',[h])
        rc = get('eth_getTransactionReceipt',[h])
        transactions[h], receipts[h] = tx, rc
        secondary[h] = {'transaction':get('eth_getTransactionByHash',[h],SECONDARY),
                        'receipt':get('eth_getTransactionReceipt',[h],SECONDARY),
                        'block':get('eth_getBlockByNumber',[rc['blockNumber'],False],SECONDARY)}
        if tx['from'].lower() == TREASURY:
            n = int(tx['blockNumber'],16)
            balances[h] = {str(b):get('eth_getBalance',[TREASURY,hex(b)]) for b in (n-1,n)}
    pinned = boundaries['2026-10-19T00:00:00Z']-1
    def call(to, data):
        return get('eth_call',[{'to':to,'data':data},hex(pinned)])
    meta = {k:call(POOL,s) for k,s in [('token0','0x0dfe1681'),('token1','0xd21220a7'),('fee','0xddca3f43'),('factory','0xc45a0155')]}
    for token in (FJ,WBNB):
        meta[token] = {k:call(token,s) for k,s in [('decimals','0x313ce567'),('symbol','0x95d89b41'),('name','0x06fdde03')]}
    args = FJ[2:].rjust(64,'0')+WBNB[2:].rjust(64,'0')+hex(10000)[2:].rjust(64,'0')
    meta['factoryPool'] = call('0x'+meta['factory'][-40:],'0x1698ee82'+args)
    signatures = {'Transfer':'Transfer(address,address,uint256)','Swap':'Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)'}
    meta['eventTopics'] = {k:get('web3_sha3',['0x'+s.encode().hex()]) for k,s in signatures.items()}
    return {'capturedAt':CAPTURED_AT,'primary':PRIMARY,'secondary':SECONDARY,'chainId':chain_id,
            'finalized':get('eth_getBlockByNumber',['finalized',False]),'boundaries':boundaries,
            'blocks':blocks,'scans':scans,'transactions':transactions,'receipts':receipts,
            'secondaryReads':secondary,'metadataBlock':pinned,'metadata':meta,
            'treasuryNativeBalances':balances}
