#!/usr/bin/env python3
"""Cold Q41 audit from immutable public journals; no RPC calls or peer totals."""
import csv,datetime as dt,json,re,sys
from decimal import Decimal,localcontext
from fractions import Fraction
from pathlib import Path
from collections import Counter
HERE=Path(__file__).resolve().parent
OLD=HERE/'inherited/q33-flapjax-20261021'
sys.path.insert(0,str(OLD/'q35-reuse'))
from evidence import FJ,WBNB,POOL,TREASURY,PRIMARY,SECONDARY,TRANSFER,SWAP,load_capture,timestamp
from audit import need,n,units,address,words,signed,transfer,canonical_log,iso,validate_coverage,analyse as old_analyse
START='2026-10-09T05:00:00Z';END='2026-10-22T05:00:00Z'
TRACE={'tracer':'prestateTracer','timeout':'5s','tracerConfig':{'diffMode':False}}
CALLTRACE={'tracer':'callTracer','timeout':'5s'}

def records():
 out=[]
 for p in (OLD/'q35-reuse/evidence/rpc.jsonl',OLD/'evidence/rpc.jsonl',HERE/'evidence/rpc.jsonl'):
  out.extend(json.loads(l) for l in p.read_text().splitlines())
 return out
class Saved:
 def __init__(self,rows):
  self.good={}
  for r in rows:
   if r['status']!=200 or 'result' not in r['response']:continue
   m,p=r['request']['method'],r['request']['params']
   if m=='eth_getBlockByNumber' and p[0] in ('latest','finalized'):continue
   k=self.key(r['url'],m,p);v=r['response']['result']
   need(k not in self.good or self.good[k]==v,'contradictory saved response');self.good[k]=v
 @staticmethod
 def key(u,m,p):return json.dumps([u,m,p],sort_keys=True)
 def get(self,m,p,u=PRIMARY):
  k=self.key(u,m,p);need(k in self.good,'missing evidence '+m+' '+str(p)[:100]);return self.good[k]
 def optional(self,m,p,u=PRIMARY):return self.good.get(self.key(u,m,p))

def rational(num,den):
 need(den>0,'nonpositive denominator');f=Fraction(num,den)
 with localcontext() as c:c.prec=40;approx=format(Decimal(f.numerator)/Decimal(f.denominator),'.18E')
 return {'numerator':str(f.numerator),'denominator':str(f.denominator),'decimal':approx}
def atomic(s):
 x=Decimal(s)*10**18;need(x==int(x),'fractional atom');return int(x)
def rules(text):
 buy=re.search(r'each buy spends ([0-9.]+) BNB',text)
 floor=re.search(r'under ([0-9.]+) BNB',text)
 need(buy and floor and 'at most one buy per program day counted in COT' in text and 'only buys FLAPJAX' in text,'unreceived changed rule wording')
 return {'buyAtoms':atomic(buy[1]),'floorAtoms':atomic(floor[1]),'maxBuysPerCOTDay':1}
def cot(t):return dt.datetime.fromtimestamp(t,dt.timezone(dt.timedelta(hours=-5))).isoformat()
def selected(t):return timestamp(START)<=t<timestamp(END)
def native_flows(trace,tx):
 need(trace.get('type')=='CALL' and trace['from'].lower()==tx['from'].lower() and trace['to'].lower()==tx['to'].lower() and n(trace.get('value','0x0'))==n(tx['value']) and not trace.get('error'),'call trace root mismatch')
 incoming=outgoing=0
 def walk(frame,root=False,failed=False):
  nonlocal incoming,outgoing
  failed=failed or bool(frame.get('error'))
  if not failed and frame.get('type') in ('CALL','CREATE','CREATE2','SELFDESTRUCT'):
   value=n(frame.get('value','0x0'))
   if frame.get('to','').lower()==TREASURY:incoming+=value
   if frame.get('from','').lower()==TREASURY and not root:outgoing+=value
  for child in frame.get('calls',[]):walk(child,failed=failed)
 walk(trace,True);return incoming,outgoing

def analyse(rows=None,task=None,linked=None,verify_old=True):
 if verify_old:old_analyse(load_capture(OLD/'q35-reuse/evidence/rpc.jsonl'))
 rows=records() if rows is None else rows;s=Saved(rows);get=s.get
 task=json.loads((HERE/'evidence/task-current.json').read_text()) if task is None else task
 linked=(HERE/'evidence/colony-linked.txt').read_text() if linked is None else linked
 rule=rules(task['description']);need(rule==rules(linked),'task and linked rule disagreement')
 need(task['id']=='0x642b0b54e35e416dacd8a6b27e6e40c63a8d0bc204218649cc229b02bdb2f074','wrong task')
 # Marketplace is Base; audit data is BSC. They must not be conflated.
 need(task['chainId']==8453,'unexpected marketplace network')
 for u in (PRIMARY,SECONDARY):need(n(get('eth_chainId',[],u))==56,'wrong chain')
 bounds=json.loads((HERE/'evidence/boundaries.json').read_text());first=bounds[START];last=bounds[END]-1
 def block(b,u=PRIMARY,full=False):
  v=get('eth_getBlockByNumber',[hex(b),full],u);need(n(v['number'])==b,'header number mismatch');return v
 for date,b in bounds.items():
  a,c=block(b-1),block(b)
  need(n(a['timestamp'])<timestamp(date)<=n(c['timestamp']) and c['parentHash']==a['hash'],'calendar boundary mismatch')
 pin=json.loads((HERE/'evidence/snapshot.json').read_text())
 need(any(r['request']['method']=='eth_getBlockByNumber' and r['request']['params']==['finalized',False] and r['response'].get('result')==pin for r in rows),'missing finalized pin')
 need(n(pin['number'])>last and n(pin['timestamp'])>=timestamp(END),'insufficient finalized range')
 for u in (PRIMARY,SECONDARY):need(block(n(pin['number']),u)['hash']==pin['hash'],'snapshot route mismatch')
 def call(to,sel,b=last):return get('eth_call',[{'to':to,'data':sel},hex(b)])
 need(address(call(POOL,'0x0dfe1681'))==FJ and address(call(POOL,'0xd21220a7'))==WBNB,'pool token/order mismatch')
 need(n(call(POOL,'0xddca3f43'))==10000 and address(call(POOL,'0xc45a0155'))=='0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865','pool fee/factory mismatch')
 for token in (FJ,WBNB):need(n(call(token,'0x313ce567'))==18,'decimals mismatch')
 coverage=[]
 def scan(kind):
  # Exact inherited partitions, never a new chain-wide scan.
  segments=[(126424183,128550459)]
  segments+=([(128550460,128867609),(128867610,last)] if kind=='token' else [(128550460,last)])
  logs=[]
  for lo,hi in segments:
   part={}
   for step in (50000,25000):
    rr=[];ll=[]
    for a in range(lo,hi+1,step):
     b=min(a+step-1,hi);q={'address':FJ if kind=='token' else POOL,'fromBlock':hex(a),'toBlock':hex(b)}
     if kind=='token':q['topics']=[TRANSFER]
     found=get('eth_getLogs',[q]);need(isinstance(found,list),'invalid log result');ll.extend(found);rr.append([a,b,len(found)])
    part[str(step)]={'ranges':rr,'logs':ll}
   valid=validate_coverage(part,lo,hi,FJ if kind=='token' else POOL,TRANSFER if kind=='token' else None)
   coverage.append({'kind':kind,'first':lo,'last':hi,'ranges50000':len(part['50000']['ranges']),'ranges25000':len(part['25000']['ranges']),'logs':len(valid),'inherited':hi<=128867609 if kind=='token' else hi<=128550459})
   logs.extend(valid)
  need(len({(l['blockHash'],l['transactionHash'],l['logIndex']) for l in logs})==len(logs),'cross-segment duplicate')
  return [l for l in logs if first<=n(l['blockNumber'])<=last]
 tokenlogs=scan('token');poollogs=scan('pool');swaps=[l for l in poollogs if l['topics'][0]==SWAP]
 treasurylogs=[l for l in tokenlogs if TREASURY in (transfer(l)['from'],transfer(l)['to'])]
 hashes={l['transactionHash'] for l in swaps+treasurylogs};txs={};receipts={}
 for h in sorted(hashes):
  tx=get('eth_getTransactionByHash',[h]);rc=get('eth_getTransactionReceipt',[h]);need(tx and rc and n(rc['status'])==1,'failed/missing receipt')
  bn=n(tx['blockNumber']);b=block(bn)
  need(tx['hash']==rc['transactionHash']==h and tx['blockHash']==rc['blockHash']==b['hash'] and n(rc['blockNumber'])==bn,'transaction/header mismatch')
  need(n(tx['transactionIndex'])==n(rc['transactionIndex']),'transaction ordering mismatch')
  for l in rc['logs']:
   need(l['transactionHash']==h and l['blockHash']==b['hash'] and n(l['blockNumber'])==bn and n(l['transactionIndex'])==n(tx['transactionIndex']) and not l.get('removed',False),'receipt log identity mismatch')
  tl=[l for l in tokenlogs if l['transactionHash']==h];rl=[l for l in rc['logs'] if l['address'].lower()==FJ and l['topics'][0]==TRANSFER]
  need(sorted(map(canonical_log,tl))==sorted(map(canonical_log,rl)),'missing token scan/receipt log')
  pl=[l for l in poollogs if l['transactionHash']==h];pr=[l for l in rc['logs'] if l['address'].lower()==POOL]
  need(sorted(map(canonical_log,pl))==sorted(map(canonical_log,pr)),'missing pool scan/receipt log')
  txs[h]=tx;receipts[h]=rc
 buys=[];others=[];sells=[];unknown=[]
 for l in sorted(swaps,key=lambda x:(n(x['blockNumber']),n(x['transactionIndex']),n(x['logIndex']))):
  h=l['transactionHash'];tx=txs[h];rc=receipts[h];bn=n(l['blockNumber']);b=block(bn);w=words(l['data'])
  need(l['address'].lower()==POOL and len(l['topics'])==3 and len(w)==7,'pool/event ABI mismatch')
  need(any(canonical_log(l)==canonical_log(z) for z in rc['logs']),'swap absent from receipt')
  for u in (SECONDARY,):
   sec=get('eth_getTransactionReceipt',[h],u);st=get('eth_getTransactionByHash',[h],u);sb=block(bn,u)
   need(sec and n(sec['status'])==1 and sec['blockHash']==b['hash'] and sb['hash']==b['hash'] and sb['timestamp']==b['timestamp'],'secondary receipt/header mismatch')
   need(sorted(map(canonical_log,sec['logs']))==sorted(map(canonical_log,rc['logs'])),'secondary logs mismatch')
   need(all(st[k]==tx[k] for k in ('hash','from','to','value','input','nonce','blockHash','blockNumber','transactionIndex')),'secondary transaction mismatch')
  a0,a1=signed(w[0]),signed(w[1]);recipient=address(l['topics'][2]);t=n(b['timestamp'])
  need(selected(t),'log time outside COT window')
  outgoing=[z for z in tokenlogs if z['transactionHash']==h and transfer(z)['from']==TREASURY and transfer(z)['to']==POOL]
  relevant=tx['from'].lower()==TREASURY or recipient==TREASURY or bool(outgoing)
  basic={'tx':h,'block':bn,'UTC':iso(t),'COT':cot(t),'amount0':str(a0),'amount1':str(a1),'signer':tx['from'],'recipient':recipient}
  if not relevant:others.append(basic);continue
  if a0>0>a1:sells.append(basic);continue
  if not (a0<0<a1):unknown.append(basic);continue
  need(tx['from'].lower()==TREASURY and recipient==TREASURY,'ambiguous treasury buy attribution')
  out=[z for z in rc['logs'] if z['address'].lower()==FJ and z['topics'][0]==TRANSFER and transfer(z)['from']==POOL]
  need(len(out)==1 and transfer(out[0])=={'from':POOL,'to':TREASURY,'atoms':-a0},'treasury output mismatch')
  credits=[z for z in rc['logs'] if z['address'].lower()==WBNB and z['topics'][0]==TRANSFER and address(z['topics'][2])==POOL]
  need(sum(words(z['data'])[0] for z in credits)==a1,'WBNB credit mismatch')
  gas=n(rc['gasUsed'])*n(rc['effectiveGasPrice']);value=n(tx['value'])
  pre=s.optional('debug_traceTransaction',[h,TRACE]);flow=s.optional('debug_traceTransaction',[h,CALLTRACE])
  prebal=None;incoming=extraout=None;post=None
  if pre is not None:
   account=pre.get(TREASURY);need(account and account['nonce']==n(tx['nonce']),'prestate nonce/treasury mismatch');prebal=n(account['balance'])
  if flow is not None:incoming,extraout=native_flows(flow,tx)
  if prebal is not None and incoming is not None:post=prebal-value-gas+incoming-extraout
  full=block(bn,full=True);idx=n(tx['transactionIndex'])
  need(full['hash']==b['hash'] and full['transactions'][idx]['hash']==h,'ordered block mismatch')
  earlier_direct=[z['hash'] for z in full['transactions'][:idx] if z['from'].lower()==TREASURY or (z.get('to') or '').lower()==TREASURY]
  startbal=s.optional('eth_getBalance',[TREASURY,hex(bn-1)]);endbal=s.optional('eth_getBalance',[TREASURY,hex(bn)])
  slot=s.optional('eth_call',[{'to':POOL,'data':'0x3850c7bd'},hex(bn-1)])
  sqrt=None
  if slot is not None:
   ww=words(slot);need(len(ww)==7 and 0<ww[0]<2**160,'invalid slot0');sqrt=ww[0]
  previous=block(bn-1);need(b['parentHash']==previous['hash'],'pre-swap header parent mismatch')
  prior_swaps=[z['transactionHash'] for z in poollogs if n(z['blockNumber'])==bn and n(z['logIndex'])<n(l['logIndex']) and z['topics'][0]==SWAP]
  buy={**basic,'blockHash':b['hash'],'transactionIndex':idx,'swapLogIndex':n(l['logIndex']),'transferLogIndex':n(out[0]['logIndex']),'BNB_input':units(a1),'WBNB_atoms':str(a1),'FLAPJAX':units(-a0),'FJ_atoms':str(-a0),'effectivePrice':rational(a1,-a0),'nativeValueAtoms':str(value),'gasAtoms':str(gas),'nativeRefundAtoms':None if incoming is None else str(incoming),'extraNativeOutAtoms':None if extraout is None else str(extraout),'preTransactionBalanceAtoms':None if prebal is None else str(prebal),'postTransactionBalanceAtoms':None if post is None else str(post),'blockBeforeBalanceAtoms':None if startbal is None else str(n(startbal)),'blockEndBalanceAtoms':None if endbal is None else str(n(endbal)),'earlierDirectTreasuryTransactions':earlier_direct,'blockBefore':bn-1,'blockBeforeHash':previous['hash'],'sqrtPriceX96':None if sqrt is None else str(sqrt),'blockBeforePrice':None if sqrt is None else rational(sqrt*sqrt,2**192),'earlierPoolSwapsInBlock':prior_swaps,'floorVerdict':'UNKNOWN' if post is None else ('KEPT' if post>=rule['floorAtoms'] else 'BROKEN')}
  buys.append(buy)
 days={f'2026-10-{i:02}':0 for i in range(9,22)}
 for b in buys:days[b['COT'][:10]]+=1
 wb=sum(int(b['WBNB_atoms']) for b in buys);fj=sum(int(b['FJ_atoms']) for b in buys)
 outflows=[]
 for l in treasurylogs:
  tr=transfer(l)
  if tr['from']==TREASURY:
   h=l['transactionHash'];b=block(n(l['blockNumber']));outflows.append({'tx':h,'block':n(l['blockNumber']),'UTC':iso(n(b['timestamp'])),'COT':cot(n(b['timestamp'])),'logIndex':n(l['logIndex']),'to':tr['to'],'FJ_atoms':str(tr['atoms']),'FLAPJAX':units(tr['atoms']),'classification':'to named pool' if tr['to']==POOL else 'outside named pool; purpose outside this audit'})
 to_pool=[x for x in outflows if x['to']==POOL]
 floor='BROKEN' if any(b['floorVerdict']=='BROKEN' for b in buys) else ('UNKNOWN' if any(b['floorVerdict']=='UNKNOWN' for b in buys) or not buys else 'KEPT for executed buys')
 return {'task':{'id':task['id'],'marketplaceChainId':task['chainId'],'status':task['status'],'phase':task['phase'],'submissionWindowOpen':task['submissionWindowOpen'],'submissions':task['submissionCount'],'awards':task['awardCount'],'expiry':task['expiryTime']},'auditChainId':56,'window':{'startUTC':START,'endUTCExclusive':END,'firstBlock':first,'lastBlock':last,'programme':'October 9–22 COT; audit October 9–21 inclusive'},'pin':{k:pin[k] for k in ('number','hash','timestamp')},'rules':{k:str(v) for k,v in rule.items()},'coverage':coverage,'windowCounts':{'tokenTransfers':len(tokenlogs),'poolEvents':len(poollogs),'poolSwaps':len(swaps),'treasuryTokenOutflows':len(outflows),'treasuryToPool':len(to_pool),'transactionsChecked':len(hashes)},'boundaries':{date:{'previous':{k:block(b-1)[k] for k in ('number','hash','timestamp')},'first':{k:block(b)[k] for k in ('number','hash','timestamp')}} for date,b in bounds.items()},'buys':buys,'otherSwaps':others,'treasurySells':sells,'unclassifiedPoolSwaps':unknown,'treasuryOutflows':outflows,'dailyCounts':days,'missedDays':[d for d,c in days.items() if not c],'totals':{'buys':len(buys),'programDaysWithBuy':sum(c>0 for c in days.values()),'programDaysAudited':len(days),'WBNB_atoms':str(wb),'BNB':units(wb),'FJ_atoms':str(fj),'FLAPJAX':units(fj),'gasAtoms':str(sum(int(b['gasAtoms']) for b in buys)),'nativeValueAtoms':str(sum(int(b['nativeValueAtoms']) for b in buys)),'weightedPrice':rational(wb,fj) if fj else None},'verdicts':{'each_buy_0_01_BNB':'KEPT' if buys and all(int(b['WBNB_atoms'])==rule['buyAtoms'] for b in buys) else 'BROKEN','buy_only_named_pool':'BROKEN' if sells or to_pool else ('UNKNOWN' if unknown else 'KEPT'),'at_most_one_per_COT_day':'KEPT' if max(days.values())<=rule['maxBuysPerCOTDay'] else 'BROKEN','skip_if_under_floor':floor,'reason_for_missed_day':'UNKNOWN: no executed swap or contemporaneous decision/counterfactual is recorded for October 15'}}

def write(out,s):
 out.mkdir(parents=True,exist_ok=True);(out/'summary.json').write_text(json.dumps(s,indent=2)+'\n')
 for name,rows in [('buys',s['buys']),('treasury-outflows',s['treasuryOutflows']),('other-swaps',s['otherSwaps']),('calendar',[{'COT_day':d,'buys':c} for d,c in s['dailyCounts'].items()])]:
  with (out/(name+'.csv')).open('w') as f:
   if rows:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows([{k:json.dumps(v,sort_keys=True) if isinstance(v,(dict,list)) else v for k,v in row.items()} for row in rows])
if __name__=='__main__':
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=HERE/'derived');a=p.parse_args();s=analyse();write(a.out,s);print(json.dumps({k:s[k] for k in ('totals','verdicts','windowCounts')},indent=2))
