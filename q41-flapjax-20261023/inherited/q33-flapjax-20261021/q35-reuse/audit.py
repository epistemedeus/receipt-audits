#!/usr/bin/env python3
"""Offline receipt audit; integer amounts, exact rational prices, fail-closed coverage."""
import csv
import datetime as dt
from decimal import Decimal, localcontext
from fractions import Fraction
import json
import pathlib
from evidence import FJ, WBNB, POOL, TREASURY, TRANSFER, SWAP, timestamp, load_capture

HERE=pathlib.Path(__file__).resolve().parent
E18=10**18
START='2026-10-09T00:00:00Z'
END='2026-10-19T00:00:00Z'

def need(condition,message):
    if not condition: raise ValueError(message)

def n(h): return int(h,16)
def address(word):
    need(len(word)==66 and word[2:26]=='0'*24,'invalid address word')
    return '0x'+word[-40:].lower()
def words(data):
    need(data.startswith('0x') and (len(data)-2)%64==0,'invalid ABI data')
    return [int(data[i:i+64],16) for i in range(2,len(data),64)]
def signed(v): return v-(1<<256) if v >= (1<<255) else v

def units(value,decimals=18):
    # Integer-only adaptation of kaminariouji/flapjax-probe q21 fmt; see NOTICE.md and LICENSE.
    sign='-' if value<0 else '';value=abs(value)
    whole,part=divmod(value,10**decimals)
    frac=f'{part:0{decimals}d}'.rstrip('0')
    return sign+str(whole)+('.'+frac if frac else '')
def price(bnb,fj):
    f=Fraction(bnb,fj)  # both assets have 18 decimals
    with localcontext() as c:
        c.prec=40; approx=format(Decimal(f.numerator)/Decimal(f.denominator),'.18E')
    return {'numerator':str(f.numerator),'denominator':str(f.denominator),'BNB_per_FLAPJAX':approx}
def log_id(l):return (l['blockHash'].lower(),l['transactionHash'].lower(),n(l['logIndex']))
def canonical_log(l):
    return (l['address'].lower(),tuple(t.lower() for t in l['topics']),l['data'].lower(),n(l['blockNumber']),l['blockHash'].lower(),l['transactionHash'].lower(),n(l['transactionIndex']),n(l['logIndex']),l.get('removed',False))
def transfer(l):
    need(l['address'].lower()==FJ and l['topics'][0]==TRANSFER and len(l['topics'])==3,'wrong token or Transfer')
    w=words(l['data']);need(len(w)==1,'invalid Transfer data')
    return {'from':address(l['topics'][1]),'to':address(l['topics'][2]),'atoms':w[0]}
def block_of(d,num):
    return d['blocks'][str(num)] if str(num) in d['blocks'] else d['blocks'][num]
def iso(t):return dt.datetime.fromtimestamp(t,dt.timezone.utc).isoformat().replace('+00:00','Z')
def decode_string(s):
    b=bytes.fromhex(s[2:]);offset=int.from_bytes(b[:32],'big');length=int.from_bytes(b[offset:offset+32],'big');return b[offset+32:offset+32+length].decode()

def validate_coverage(scan,first,last,issuer,topic=None):
    variants=[]
    for step in ('50000','25000'):
        part=scan[step];cursor=first;seen=set()
        expected=[]
        for a,b,count in part['ranges']:
            need(a==cursor and a<=b<=last and b-a+1<=int(step),'incomplete/truncated range coverage')
            need(0<=count<1000,'possible log cap');cursor=b+1
            got=[l for l in part['logs'] if a<=n(l['blockNumber'])<=b]
            need(len(got)==count,'range/log count mismatch')
            expected.extend(got)
        need(cursor==last+1,'incomplete final range')
        need(len(expected)==len(part['logs']),'log outside range')
        for l in expected:
            need(l['address'].lower()==issuer,'wrong log issuer')
            need(not l.get('removed',False),'removed log')
            if topic:need(l['topics'][0]==topic,'wrong topic')
            ident=log_id(l);need(ident not in seen,'duplicate log');seen.add(ident)
        variants.append(sorted(map(canonical_log,expected)))
    need(variants[0]==variants[1],'partition mismatch/missing logs')
    return scan['50000']['logs']

def analyse(d):
    need(d['chainId']==56,'wrong network')
    meta=d['metadata'];need(address(meta['token0'])==FJ,'wrong pool token0');need(address(meta['token1'])==WBNB,'wrong pool token1')
    need(n(meta['fee'])==10000,'wrong fee')
    need(address(meta['factory'])=='0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865','wrong factory')
    need(address(meta['factoryPool'])==POOL,'wrong factory pool')
    need(meta['eventTopics']=={'Transfer':TRANSFER,'Swap':SWAP},'wrong event topics')
    for token in (FJ,WBNB):need(n(meta[token]['decimals'])==18,'wrong decimals')
    need(decode_string(meta[FJ]['symbol']).upper()=='FLAPJAX','wrong token symbol')
    boundaries=d['boundaries']
    for date,b in boundaries.items():
        prev,cur=block_of(d,b-1),block_of(d,b)
        need(n(prev['number'])==b-1 and n(cur['number'])==b,'wrong boundary block')
        need(n(prev['timestamp'])<timestamp(date)<=n(cur['timestamp']),'bad UTC boundary')
        need(cur['parentHash']==prev['hash'],'boundary parent mismatch')
    first=boundaries['2026-10-08T10:00:00Z'];last=boundaries['2026-10-19T12:00:00Z']-1
    need(n(d['finalized']['number'])>last and n(d['finalized']['timestamp'])>=timestamp('2026-10-19T12:00:00Z'),'insufficient finalized observation')
    tokenlogs=validate_coverage(d['scans']['token'],first,last,FJ,TRANSFER)
    poollogs=validate_coverage(d['scans']['pool'],first,last,POOL)
    swaps=[x for x in poollogs if x['topics'][0]==SWAP]
    all_hashes={l['transactionHash'] for l in swaps}
    need(all_hashes==set(d['transactions'])==set(d['receipts'])==set(d['secondaryReads']),'absent transaction/receipt evidence')
    buys=[];others=[];in_window_swaps=[]
    for swap in sorted(swaps,key=lambda l:(n(l['blockNumber']),n(l['transactionIndex']),n(l['logIndex']))):
        h=swap['transactionHash'];tx=d['transactions'][h];rc=d['receipts'][h];bn=n(swap['blockNumber']);blk=block_of(d,bn);sec=d['secondaryReads'][h]
        need(tx is not None and rc is not None,'absent evidence')
        need(n(rc['status'])==1,'receipt failed')
        need(rc['transactionHash']==tx['hash']==h,'wrong transaction identity')
        need(tx['blockHash']==rc['blockHash']==swap['blockHash']==blk['hash'],'block hash mismatch')
        need(n(tx['blockNumber'])==n(rc['blockNumber'])==n(blk['number'])==bn,'block number mismatch')
        need(any(canonical_log(swap)==canonical_log(l) for l in rc['logs']),'swap absent from receipt')
        need(n(sec['receipt']['status'])==1 and sec['receipt']['blockHash']==blk['hash'] and sec['block']['hash']==blk['hash'] and sec['block']['timestamp']==blk['timestamp'],'independent receipt/header mismatch')
        need(sorted(map(canonical_log,sec['receipt']['logs']))==sorted(map(canonical_log,rc['logs'])),'independent receipt log mismatch')
        need(all(sec['transaction'][k]==tx[k] for k in ['hash','blockHash','blockNumber','from','to','value','input','nonce']),'independent tx mismatch')
        # Every FJ receipt log must appear in the complete token scan, and vice versa.
        rlogs=[l for l in rc['logs'] if l['address'].lower()==FJ and l['topics'][0]==TRANSFER]
        slog=[l for l in tokenlogs if l['transactionHash']==h]
        need(sorted(map(canonical_log,rlogs))==sorted(map(canonical_log,slog)),'missing token log in scan/receipt')
        w=words(swap['data']);need(len(swap['topics'])==3 and len(w)==7,'wrong PancakeSwap event ABI')
        a0,a1=signed(w[0]),signed(w[1]);recipient=address(swap['topics'][2]);when=n(blk['timestamp'])
        if timestamp(START)<=when<timestamp(END):in_window_swaps.append(h)
        if tx['from'].lower()!=TREASURY or not (a0<0<a1):
            others.append({'tx':h,'block':bn,'UTC':iso(when),'signer':tx['from'],'amount0':str(a0),'amount1':str(a1)});continue
        outs=[l for l in rlogs if transfer(l)['from']==POOL]
        need(len(outs)==1,'ambiguous/missing pool output')
        out=transfer(outs[0]);need(out['atoms']==-a0 and out['to']==recipient,'Swap/output mismatch')
        # The actual WBNB pool credit, rather than native tx.value, is the execution input.
        wlogs=[l for l in rc['logs'] if l['address'].lower()==WBNB and l['topics'][0]==TRANSFER and address(l['topics'][2])==POOL]
        need(sum(words(l['data'])[0] for l in wlogs)==a1,'WBNB input mismatch')
        value=n(tx['value']);gas=n(rc['gasUsed'])*n(rc['effectiveGasPrice'])
        balances=d['treasuryNativeBalances'][h];delta=n(balances[str(bn-1)])-n(balances[str(bn)])
        buys.append({'tx':h,'block':bn,'blockHash':blk['hash'],'UTC':iso(when),'timestamp':when,'recipient':out['to'],'signer':tx['from'].lower(),'router':tx['to'].lower(),'FJ_atoms':str(out['atoms']),'FLAPJAX':units(out['atoms']),'WBNB_input_atoms':str(a1),'BNB_input':units(a1),'native_value_atoms':str(value),'native_value_BNB':units(value),'gas_atoms':str(gas),'gas_BNB':units(gas),'treasury_block_native_debit_atoms':str(delta),'native_residual_atoms':str(delta-value-gas),'transferLogIndex':n(outs[0]['logIndex']),'swapLogIndex':n(swap['logIndex']),'price':price(a1,out['atoms'])})
    selected=[b for b in buys if timestamp(START)<=b['timestamp']<timestamp(END)]
    bnb=sum(int(x['WBNB_input_atoms']) for x in selected);fj=sum(int(x['FJ_atoms']) for x in selected)
    gas=sum(int(x['gas_atoms']) for x in selected);value=sum(int(x['native_value_atoms']) for x in selected)
    need(fj>0,'absent buys')
    utc={f'2026-10-{day:02}':0 for day in range(9,19)};cot=dict(utc);edt=dict(utc)
    for b in selected:
        utc[b['UTC'][:10]]+=1
    for b in buys:
        for offset,days in [(-5,cot),(-4,edt)]:
            date=iso(b['timestamp']+offset*3600)[:10]
            if date in days:days[date]+=1
    startblock,endblock=boundaries[START],boundaries[END]-1
    window=[l for l in tokenlogs if startblock<=n(l['blockNumber'])<=endblock]
    outgoing=[l for l in window if transfer(l)['from']==TREASURY]
    to_pool=[l for l in outgoing if transfer(l)['to']==POOL]
    pool_outs=[l for l in window if transfer(l)['from']==POOL]
    other_window=[x for x in others if startblock<=x['block']<=endblock]
    local={}
    for label,offset in [('UTC-5',5),('UTC-4',4)]:
        a=boundaries[f'2026-10-09T0{offset}:00:00Z'];b=boundaries[f'2026-10-19T0{offset}:00:00Z']-1
        local[label]={'startBlock':a,'endBlock':b,'treasury_to_pool':len([l for l in tokenlogs if a<=n(l['blockNumber'])<=b and transfer(l)['from']==TREASURY and transfer(l)['to']==POOL]),'buy_hashes':[x['tx'] for x in buys if timestamp(f'2026-10-09T0{offset}:00:00Z')<=x['timestamp']<timestamp(f'2026-10-19T0{offset}:00:00Z')]}
    verdict={'nine_buys_each_0.01_total_0.09':'MATCH' if len(selected)==9 and all(int(x['WBNB_input_atoms'])==10**16 for x in selected) and bnb==9*10**16 else 'MISMATCH','one_daily_except_15_UTC':'MATCH' if all(v==(0 if k.endswith('-15') else 1) for k,v in utc.items()) else 'MISMATCH','all_buy_output_to_treasury':'MATCH' if all(x['recipient']==TREASURY for x in selected) else 'MISMATCH','no_treasury_FJ_to_named_pool':'MATCH' if not to_pool else 'MISMATCH','October23_makeup':'UNKNOWN (future promise)'}
    return {'window':{'start':START,'endExclusive':END,'firstBlock':startblock,'lastBlock':endblock},'coverage':{'firstPaddedBlock':first,'lastPaddedBlock':last,'paddedTokenTransfers':len(tokenlogs),'paddedPoolEvents':len(poollogs),'paddedSwaps':len(swaps),'windowSwaps':len(in_window_swaps),'windowTokenTransfers':len(window),'windowTreasuryOutflows':len(outgoing),'windowTreasuryToPool':len(to_pool),'windowPoolOutflows':len(pool_outs),'windowPoolToTreasury':len([l for l in pool_outs if transfer(l)['to']==TREASURY]),'windowOtherSwaps':len(other_window),'windowOtherBuys':len([x for x in other_window if int(x['amount0'])<0<int(x['amount1'])]),'windowOtherSells':len([x for x in other_window if int(x['amount0'])>0>int(x['amount1'])]),'coarseRanges':len(d['scans']['token']['50000']['ranges']),'fineRanges':len(d['scans']['token']['25000']['ranges'])},'metadata':{'block':d['metadataBlock'],'token0':address(meta['token0']),'token1':address(meta['token1']),'factory':address(meta['factory']),'fee':n(meta['fee']),'FJ_name':decode_string(meta[FJ]['name']),'FJ_symbol':decode_string(meta[FJ]['symbol']),'WBNB_name':decode_string(meta[WBNB]['name']),'WBNB_symbol':decode_string(meta[WBNB]['symbol']),'decimals':18},'finalized':{k:d['finalized'][k] for k in ['number','hash','timestamp']},'buys':selected,'paddingBuys':[x for x in buys if x not in selected],'otherSwaps':others,'totals':{'buys':len(selected),'WBNB_atoms':str(bnb),'BNB':units(bnb),'FJ_atoms':str(fj),'FLAPJAX':units(fj),'native_value_atoms':str(value),'gas_atoms':str(gas),'gas_BNB':units(gas),'value_plus_gas_BNB':units(value+gas),'weightedPrice':price(bnb,fj),'firstPrice':selected[0]['price'],'lastPrice':selected[-1]['price']},'calendarCounts':{'UTC':utc,'UTC-5':cot,'UTC-4':edt},'localWindows':local,'verdicts':verdict}

def verify_journal(d,path):
    """Bind aggregate capture to the saved successful RPC requests/results."""
    records=[json.loads(s) for s in path.read_text().splitlines()]
    good={(r['url'],r['request']['method'],json.dumps(r['request']['params'],sort_keys=True)):r['response']['result'] for r in records if r['status']==200 and 'result' in r['response']}
    def check(url,m,p,expected):
        key=(url,m,json.dumps(p,sort_keys=True));need(key in good and good[key]==expected,'missing/changed journal evidence: '+m)
    for url in [d['primary'],d['secondary']]:need(n(good[(url,'eth_chainId','[]')])==56,'wrong journal network')
    check(d['primary'],'eth_getBlockByNumber',['finalized',False],d['finalized'])
    for key,blk in d['blocks'].items():check(d['primary'],'eth_getBlockByNumber',[hex(int(key)),False],blk)
    for name,scan in d['scans'].items():
        for part in scan.values():
            for a,b,count in part['ranges']:
                query={'address':FJ if name=='token' else POOL,'fromBlock':hex(a),'toBlock':hex(b)}
                if name=='token':query['topics']=[TRANSFER]
                expected=[l for l in part['logs'] if a<=n(l['blockNumber'])<=b]
                check(d['primary'],'eth_getLogs',[query],expected)
    for h,tx in d['transactions'].items():
        check(d['primary'],'eth_getTransactionByHash',[h],tx);check(d['primary'],'eth_getTransactionReceipt',[h],d['receipts'][h])
        sec=d['secondaryReads'][h]
        for m,p,v in [('eth_getTransactionByHash',[h],sec['transaction']),('eth_getTransactionReceipt',[h],sec['receipt']),('eth_getBlockByNumber',[tx['blockNumber'],False],sec['block'])]:check(d['secondary'],m,p,v)
    for name,sel in [('token0','0x0dfe1681'),('token1','0xd21220a7'),('fee','0xddca3f43'),('factory','0xc45a0155')]:check(d['primary'],'eth_call',[{'to':POOL,'data':sel},hex(d['metadataBlock'])],d['metadata'][name])
    args=FJ[2:].rjust(64,'0')+WBNB[2:].rjust(64,'0')+hex(10000)[2:].rjust(64,'0')
    check(d['primary'],'eth_call',[{'to':'0x'+d['metadata']['factory'][-40:],'data':'0x1698ee82'+args},hex(d['metadataBlock'])],d['metadata']['factoryPool'])
    for key,signature in {'Transfer':'Transfer(address,address,uint256)','Swap':'Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)'}.items():check(d['primary'],'web3_sha3',['0x'+signature.encode().hex()],d['metadata']['eventTopics'][key])
    for token in [FJ,WBNB]:
        for key,sel in [('decimals','0x313ce567'),('symbol','0x95d89b41'),('name','0x06fdde03')]:check(d['primary'],'eth_call',[{'to':token,'data':sel},hex(d['metadataBlock'])],d['metadata'][token][key])
    for balances in d['treasuryNativeBalances'].values():
        for bn,value in balances.items():check(d['primary'],'eth_getBalance',[TREASURY,hex(int(bn))],value)
    return len(records)

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=pathlib.Path,default=HERE/'evidence');p.add_argument('--out',type=pathlib.Path,default=HERE/'derived');a=p.parse_args()
    d=load_capture(a.evidence/'rpc.jsonl');summary=analyse(d);summary['rpcRecordsChecked']=verify_journal(d,a.evidence/'rpc.jsonl')
    a.out.mkdir(parents=True,exist_ok=True);(a.out/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    fields=['tx','block','blockHash','UTC','signer','router','recipient','BNB_input','WBNB_input_atoms','FLAPJAX','FJ_atoms','native_value_atoms','gas_atoms','native_residual_atoms','transferLogIndex','swapLogIndex']
    with (a.out/'buys.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');w.writeheader();w.writerows(summary['buys'])
    print(json.dumps({k:summary[k] for k in ['coverage','totals','verdicts']},indent=2))
if __name__=='__main__':main()
