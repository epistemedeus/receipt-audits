#!/usr/bin/env python3
"""Reproduce Q33 solely from saved public evidence and the received Q35 decoder."""
from collections import defaultdict
import csv
from fractions import Fraction
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'q35-reuse'))
from audit import need,n,units,address,words,signed,transfer,canonical_log,log_id,decode_string,iso,validate_coverage,analyse as analyse_q35
from evidence import FJ,POOL,WBNB,TREASURY,TRANSFER,SWAP,PRIMARY,SECONDARY,load_capture
from sources import ledger
HERE=Path(__file__).resolve().parent
ZERO='0x'+'0'*40
class Saved:
    def __init__(self,records):
        self.good={}
        for r in records:
            if r['status']!=200 or 'result' not in r['response']:continue
            key=self.key(r['url'],r['request']['method'],r['request']['params'])
            v=r['response']['result']
            need(key not in self.good or self.good[key]==v,'contradictory saved RPC')
            self.good[key]=v
    @staticmethod
    def key(u,m,p):return json.dumps([u,m,p],sort_keys=True)
    def get(self,m,p,u=PRIMARY):
        k=self.key(u,m,p);need(k in self.good,'absent saved source: '+m+' '+str(p)[:130]);return self.good[k]
    def optional(self,m,p,u=SECONDARY):
        return self.good.get(self.key(u,m,p))

def fraction(value,supply):
    f=Fraction(value*100,supply)
    return {'numerator':str(f.numerator),'denominator':str(f.denominator),'percent':units(value*100*10**12//supply,12)}
def ranking(balances):return sorted(((a,v) for a,v in balances.items() if v>0),key=lambda x:(-x[1],x[0]))
def reduce_transfers(logs,opening=None):
    balances=defaultdict(int,opening or {});minted=burned=0
    for l in sorted(logs,key=lambda x:(n(x['blockNumber']),n(x['transactionIndex']),n(x['logIndex']))):
        t=transfer(l);v=t['atoms']
        if t['from']==ZERO:minted+=v
        else:balances[t['from']]-=v;need(balances[t['from']]>=0,'negative reconstructed balance')
        if t['to']==ZERO:burned+=v
        else:balances[t['to']]+=v
    return dict(balances),minted,burned

def retention(payouts,balances):
    paid=defaultdict(int)
    for p in payouts:paid[p['to']]+=int(p['atoms'])
    rows=[]
    for a,v in sorted(paid.items()):
        need(a in balances,'unavailable retention balance')
        rows.append({'address':a,'paidAtoms':str(v),'balanceAtoms':str(balances[a]),'holdsAtLeastPayout':balances[a]>=v})
    return {'payouts':len(payouts),'recipients':len(rows),'retained':sum(x['holdsAtLeastPayout'] for x in rows),'rows':rows}

def analyse(directory=HERE/'evidence', old=None, records=None):
    if old is None:old=load_capture(HERE/'q35-reuse/evidence/rpc.jsonl')
    analyse_q35(old)  # Actual received validator, not an unchecked copied list.
    if records is None:records=[json.loads(l) for l in (directory/'rpc.jsonl').read_text().splitlines()]
    saved=Saved(records);get=saved.get
    pin=json.loads((directory/'snapshot.json').read_text());bn=n(pin['number']);tag=hex(bn)
    observation=json.loads((directory/'probe-eth_getBlockByNumber.json').read_text())
    need(observation['status']==200 and observation['request']['params']==['finalized',False] and observation['response']['result']==pin,'snapshot lacks saved finalized observation')
    for u in (PRIMARY,SECONDARY):
        need(n(get('eth_chainId',[],u))==56,'wrong chain')
        block=get('eth_getBlockByNumber',[tag,False],u)
        need(block['hash']==pin['hash'] and block['timestamp']==pin['timestamp'],'snapshot block mismatch')
    def call(data,to=FJ,u=PRIMARY):return get('eth_call',[{'to':to,'data':data},tag],u)
    def bal(a,u=PRIMARY):return n(call('0x70a08231'+a[2:].rjust(64,'0'),u=u))
    decimals=n(call('0x313ce567'));supply=n(call('0x18160ddd'))
    need(decimals==18 and supply>0,'invalid token decimals/supply')
    second=saved.optional('eth_call',[{'to':FJ,'data':'0x18160ddd'},tag])
    if second is not None:need(n(second)==supply,'independent supply mismatch')
    need(decode_string(call('0x95d89b41')).upper()=='FLAPJAX','wrong token identity')
    key='';seenkeys=set();candidates=[];pages=0
    while True:
        need(key not in seenkeys,'index cursor loop');seenkeys.add(key)
        p=get('nr_getTokenHolders',[FJ,'0x64',key]);pages+=1
        need(isinstance(p.get('details'),list) and len(p['details'])<=100,'malformed index page')
        candidates.extend(d['accountAddress'].lower() for d in p['details']);key=p.get('pageKey','')
        if not key:break
        need(pages<10,'index capture bound exceeded')
    need(len(candidates)==len(set(candidates)),'duplicate holder candidate')
    balances={a:bal(a) for a in candidates}
    need(ZERO not in balances or balances[ZERO]==0,'zero address balance requires supply reconciliation')
    need(sum(balances.values())==supply,'incomplete holder coverage: balance/supply gap')
    ordered=ranking(balances);top=[]
    for rank,(a,v) in enumerate(ordered[:10],1):
        code=get('eth_getCode',[a,tag]);second=saved.optional('eth_getCode',[a,tag])
        if second is not None:need(code==second,'independent code mismatch')
        second=saved.optional('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag])
        if second is not None:need(n(second)==v,'independent top balance mismatch')
        role='no runtime code; EOA-compatible'
        if a=='0x000000000000000000000000000000000000dead':role='burn destination; no runtime code (control unknown)'
        if code!='0x':
            role='contract; role unverified'
            # A role is accepted only from the pool interface plus factory binding.
            try:
                token0=address(call('0x0dfe1681',a));token1=address(call('0xd21220a7',a));fee=n(call('0xddca3f43',a));factory=address(call('0xc45a0155',a))
                args=token0[2:].rjust(64,'0')+token1[2:].rjust(64,'0')+hex(fee)[2:].rjust(64,'0')
                found=address(call('0x1698ee82'+args,factory))
                need(found==a and FJ in (token0,token1),'factory pool mismatch')
                role=f'factory-bound V3 pool; {token0}/{token1}; fee {fee}; factory {factory}'
            except ValueError as e:
                if 'absent saved source' not in str(e):raise
            if a=='0x238a358808379702088667322f80ac48bad5e6c4':
                verified=json.loads((directory/'sourcify-vault.json').read_text())
                need(verified['address'].lower()==a and str(verified['chainId'])=='56' and verified['runtimeMatch'] in ('match','exact_match'),'unverified vault source')
                need(verified['runtimeBytecode']['onchainBytecode'].lower()==code.lower(),'verified runtime differs from snapshot')
                need(verified['compilation']['fullyQualifiedName']=='src/Vault.sol:Vault','wrong vault compilation')
                role='Sourcify-verified Vault; runtime matches snapshot; beneficial owners and lock status unknown'
        top.append({'rank':rank,'address':a,'atoms':str(v),'FLAPJAX':units(v,decimals),'share':fraction(v,supply),'runtimeBytes':(len(code)-2)//2,'role':role})
    tv=bal(TREASURY);second=saved.optional('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},tag])
    if second is not None:need(tv==n(second),'independent treasury balance mismatch')
    bounds=json.loads((directory/'boundaries.json').read_text());first=bounds['2026-10-01T00:00:00Z'];last=bn
    for d,b in bounds.items():
        prev=get('eth_getBlockByNumber',[hex(b-1),False]);cur=get('eth_getBlockByNumber',[hex(b),False])
        from evidence import timestamp
        need(n(prev['timestamp'])<timestamp(d)<=n(cur['timestamp']) and cur['parentHash']==prev['hash'],'bad UTC boundary')
    tokenlogs=list(old['scans']['token']['50000']['logs'])
    for lo,hi in ((first,126424182),(128550460,last)):
        scan={}
        for step in (50000,25000):
            logs=[];ranges=[]
            for a in range(lo,hi+1,step):
                b=min(a+step-1,hi);found=get('eth_getLogs',[{'address':FJ,'topics':[TRANSFER],'fromBlock':hex(a),'toBlock':hex(b)}]);ranges.append([a,b,len(found)]);logs.extend(found)
            scan[str(step)]={'ranges':ranges,'logs':logs}
        tokenlogs.extend(validate_coverage(scan,lo,hi,FJ,TRANSFER))
    need(len(set(map(log_id,tokenlogs)))==len(tokenlogs),'duplicate combined log')
    entries=ledger((directory/'flapjax.html').read_text());bytx=defaultdict(list)
    for e in entries:bytx[e['tx']].append(e)
    flows=[];inflows=[];outflows=[];window=[];labelled=[];narrow=[];unlabelled=[];ledgerquick=[];ledgernarrow=[];amountmismatches=[]
    for l in sorted(tokenlogs,key=lambda l:(n(l['blockNumber']),n(l['transactionIndex']),n(l['logIndex']))):
        t=transfer(l)
        if TREASURY not in (t['from'],t['to']):continue
        h=l['transactionHash'];rc=get('eth_getTransactionReceipt',[h]);tx=get('eth_getTransactionByHash',[h]);b=get('eth_getBlockByNumber',[l['blockNumber'],False])
        need(n(rc['status'])==1 and tx['hash']==rc['transactionHash']==h,'failed or mismatched treasury receipt')
        need(tx['blockHash']==rc['blockHash']==l['blockHash']==b['hash'],'treasury block mismatch')
        need(any(canonical_log(l)==canonical_log(x) for x in rc['logs']),'treasury transfer absent from receipt')
        need(sorted(canonical_log(x) for x in rc['logs'] if x['address'].lower()==FJ and x['topics'][0]==TRANSFER)==sorted(canonical_log(x) for x in tokenlogs if x['transactionHash']==h),'incomplete token receipt scan')
        labels=bytx.get(h,[])
        flow={'tx':h,'block':n(l['blockNumber']),'UTC':iso(n(b['timestamp'])),'from':t['from'],'to':t['to'],'atoms':str(t['atoms']),'FLAPJAX':units(t['atoms']),'labels':labels,'logIndex':n(l['logIndex'])}
        flow['directTreasuryTokenTransfer']=tx['from'].lower()==TREASURY and tx['to'].lower()==FJ and tx['input'].startswith('0xa9059cbb')
        flow['anyKnownV3SwapInReceipt']=any(x['topics'] and x['topics'][0]==SWAP for x in rc['logs'])
        flows.append(flow)
        if t['to']==TREASURY:
            sec=get('eth_getTransactionReceipt',[h],SECONDARY)
            need(sec['blockHash']==rc['blockHash'] and sorted(map(canonical_log,sec['logs']))==sorted(map(canonical_log,rc['logs'])),'independent inflow receipt mismatch')
            swaps=[x for x in rc['logs'] if x['address'].lower()==POOL and x['topics'][0]==SWAP]
            def matched_buy(s):
                w=words(s['data'])
                if len(w)!=7 or len(s['topics'])!=3:return False
                a0,a1=signed(w[0]),signed(w[1])
                wbnb=[x for x in rc['logs'] if x['address'].lower()==WBNB and len(x['topics'])==3 and x['topics'][0]==TRANSFER and address(x['topics'][2])==POOL]
                return a0<0<a1 and -a0==t['atoms'] and address(s['topics'][2])==TREASURY and sum(words(x['data'])[0] for x in wbnb)==a1
            flow['verifiedPrimaryPoolBuy']=any(matched_buy(s) for s in swaps) and tx['from'].lower()==TREASURY and t['from']==POOL
            flow['swapEventPresent']=any(x['topics'] and x['topics'][0]==SWAP for x in rc['logs'])
            inflows.append(flow)
        if t['from']==TREASURY:
            outflows.append(flow)
            if not labels:unlabelled.append(flow)
            elif not any(int(e['atoms'])==t['atoms'] for e in labels):amountmismatches.append(flow)
            dated=[e for e in labels if '2026-10-12'<=e['date']<'2026-10-18' and e['label'].startswith('quick task Q')]
            if dated:
                ledgerquick.append(flow)
                if any(e['label'].split('Q')[-1].isdigit() and 21<=int(e['label'].split('Q')[-1])<=32 for e in dated):ledgernarrow.append(flow)
            if bounds['2026-10-12T00:00:00Z']<=n(l['blockNumber'])<bounds['2026-10-18T00:00:00Z']:
                window.append(flow)
                if any(e['label'].startswith('quick task Q') for e in labels):
                    labelled.append(flow)
                    if any(e['label'].split('Q')[-1].isdigit() and 21<=int(e['label'].split('Q')[-1])<=32 for e in labels):narrow.append(flow)
    # Retention includes zero balances absent from current-holder candidates only
    # when a real saved balanceOf exists. It never defaults an absent row to zero.
    for f in window+ledgerquick:
        if f['to'] not in balances:balances[f['to']]=bal(f['to'])
    direct=[f for f in outflows if f['to'] in (POOL,'0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e')]
    nonbuy=[f for f in inflows if not f['verifiedPrimaryPoolBuy']]
    opening=n(get('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},hex(first-1)]))
    totalin=sum(int(f['atoms']) for f in inflows);totalout=sum(int(f['atoms']) for f in outflows)
    need(opening+totalin-totalout==tv,'treasury window balance conservation failure')
    pointer=json.loads((directory/'counterexample-pointer.json').read_text());h=pointer['transaction']
    rc=get('eth_getTransactionReceipt',[h]);tx=get('eth_getTransactionByHash',[h]);block=get('eth_getBlockByNumber',[rc['blockNumber'],False])
    second=get('eth_getTransactionReceipt',[h],SECONDARY);secondtx=get('eth_getTransactionByHash',[h],SECONDARY);secondblock=get('eth_getBlockByNumber',[rc['blockNumber'],False],SECONDARY)
    need(n(rc['status'])==1 and rc['transactionHash']==tx['hash']==h,'counterexample receipt failed')
    need(rc['blockHash']==tx['blockHash']==block['hash']==second['blockHash']==secondblock['hash'],'counterexample block mismatch')
    need(sorted(map(canonical_log,rc['logs']))==sorted(map(canonical_log,second['logs'])),'independent counterexample receipt mismatch')
    need(all(tx[k]==secondtx[k] for k in ('hash','from','to','input','value','blockHash','blockNumber')),'independent counterexample transaction mismatch')
    need(tx['to'].lower()==FJ and tx['input'].startswith('0xa9059cbb') and n(tx['value'])==0,'counterexample is not a direct token transfer')
    need(len(rc['logs'])==1,'counterexample contains additional events')
    seed=transfer(rc['logs'][0]);args=words('0x'+tx['input'][10:])
    need(seed['from']==tx['from'].lower() and seed['to']==TREASURY and address('0x'+tx['input'][10:74])==TREASURY and len(args)==2 and args[1]==seed['atoms'],'counterexample input/event mismatch')
    code=get('eth_getCode',[seed['from'],rc['blockNumber']]);need(code=='0x','counterexample source has runtime code')
    seedbn=n(rc['blockNumber'])
    before=n(get('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},hex(seedbn-1)]))
    after=n(get('eth_call',[{'to':FJ,'data':'0x70a08231'+TREASURY[2:].rjust(64,'0')},hex(seedbn)]))
    need(after-before==seed['atoms'],'counterexample block balance delta mismatch')
    counterexample={'tx':h,'block':seedbn,'blockHash':block['hash'],'UTC':iso(n(block['timestamp'])),'from':seed['from'],'to':TREASURY,'atoms':str(seed['atoms']),'FLAPJAX':units(seed['atoms']),'treasuryBeforeAtoms':str(before),'treasuryAfterAtoms':str(after),'sourceRuntimeBytes':0,'receiptLogs':len(rc['logs']),'verdict':'MISMATCH for literal all-time buyback-only inflows: direct non-swap seed transfer'}
    checked=set()
    for f in labelled+ledgerquick:
        if f['tx'] in checked:continue
        sec=get('eth_getTransactionReceipt',[f['tx']],SECONDARY)
        prim=get('eth_getTransactionReceipt',[f['tx']])
        need(n(sec['status'])==1 and sec['blockHash']==prim['blockHash'] and sorted(map(canonical_log,sec['logs']))==sorted(map(canonical_log,prim['logs'])),'independent payout receipt mismatch')
        checked.add(f['tx'])
    statechecks=[]
    for a in [x['address'] for x in top]+[TREASURY]:
        for method,params in [('eth_getCode',[a,tag]),('eth_call',[{'to':FJ,'data':'0x70a08231'+a[2:].rjust(64,'0')},tag])]:
            statechecks.append({'address':a,'method':method,'independentResultAvailable':saved.optional(method,params) is not None})
    return {
        'snapshot':{'number':bn,'hash':pin['hash'],'UTC':iso(n(pin['timestamp']))},
        'token':{'address':FJ,'name':decode_string(call('0x06fdde03')),'decimals':decimals,'supplyAtoms':str(supply),'supply':units(supply)},
        'holderIndex':{'pages':pages,'candidates':len(candidates),'nonzero':len(ordered),'sumAtoms':str(sum(v for _,v in ordered)),'gapAtoms':'0'},
        'holders':[{'address':a,'atoms':str(v),'FLAPJAX':units(v)} for a,v in ordered],
        'top10':top,
        'treasury':{'address':TREASURY,'atoms':str(tv),'FLAPJAX':units(tv),'share':fraction(tv,supply),'rank':next((i+1 for i,(a,v) in enumerate(ordered) if a==TREASURY),None),'openingAtoms':str(opening),'inflowAtoms':str(totalin),'outflowAtoms':str(totalout),'conservationGapAtoms':'0'},
        'coverage':{'firstBlock':first,'lastBlock':last,'tokenTransfers':len(tokenlogs),'treasuryInflows':len(inflows),'treasuryOutflows':len(outflows),'directToTwoVerifiedPools':len(direct),'unlabelledOutflows':len(unlabelled),'independentlyCheckedLabelledReceipts':len(checked)},
        'inflows':inflows,'outflows':outflows,'nonPrimaryPoolBuyInflows':nonbuy,'unlabelledOutflows':unlabelled,'ledgerAmountMismatches':amountmismatches,
        'counterexample':counterexample,'independentStateChecks':statechecks,
        'retentionAllOutflows':retention(window,balances),
        'retentionQuickTaskLabels':retention(labelled,balances),
        'retentionQ21to32':retention(narrow,balances),
        'retentionLedgerDatedQuickTasks':retention(ledgerquick,balances),
        'retentionLedgerDatedQ21to32':retention(ledgernarrow,balances),
        'windowPayouts':window,'ledgerDatedQuickPayouts':ledgerquick,
    }

def main():
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--evidence',type=Path,default=HERE/'evidence');p.add_argument('--out',type=Path,default=HERE/'derived');a=p.parse_args()
    s=analyse(a.evidence);a.out.mkdir(parents=True,exist_ok=True);(a.out/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
    for name,rows in [('holders',s['holders']),('top10',s['top10']),('window-payouts',s['windowPayouts']),('ledger-date-payouts',s['ledgerDatedQuickPayouts']),('retention-relay-ledger',s['retentionLedgerDatedQ21to32']['rows']),('treasury-flows',s['inflows']+s['outflows'])]:
        with (a.out/(name+'.csv')).open('w') as f:
            w=csv.DictWriter(f,fieldnames=list(rows[0]) if rows else [],lineterminator='\n');w.writeheader();w.writerows({k:json.dumps(v,sort_keys=True) if isinstance(v,(list,dict)) else v for k,v in r.items()} for r in rows)
    print(json.dumps({k:s[k] for k in ('snapshot','holderIndex','treasury','coverage')},indent=2))
if __name__=='__main__':main()
