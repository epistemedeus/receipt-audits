#!/usr/bin/env node
// Independent BigInt reduction from raw public messages. No Python import,
// hand-entered balances, expected holder list, or preselected payout totals.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const ev=process.argv[2]||path.join(root,'evidence');
const summary=JSON.parse(fs.readFileSync(process.argv[3]||path.join(root,'derived/summary.json')));
const read=p=>fs.readFileSync(p,'utf8').trim().split('\n').map(JSON.parse);
const records=read(path.join(ev,'rpc.jsonl'));
const good=records.filter(r=>r.status===200&&r.response.result!==undefined);
const primary='https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3';
const secondary='https://bsc-dataseed.bnbchain.org';
const fj='0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df';
const treasury='0x7c34e9e21ee28a49ff0b84b61774119e6633359f';
const topic='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const key=x=>JSON.stringify(x);
function get(method,params,url=primary){
 const rs=good.filter(r=>r.url===url&&r.request.method===method&&key(r.request.params)===key(params));
 assert(rs.length,`missing raw source: ${method} ${key(params)}`);
 assert(rs.every(r=>key(r.response.result)===key(rs[0].response.result)),'conflicting raw source');
 return rs[0].response.result;
}
const pin=JSON.parse(fs.readFileSync(path.join(ev,'snapshot.json')));
for(const u of [primary,secondary]){
 assert.equal(BigInt(get('eth_chainId',[],u)),56n);
 assert.equal(get('eth_getBlockByNumber',[pin.number,false],u).hash,pin.hash);
}
const call=data=>get('eth_call',[{to:fj,data},pin.number]);
const balance=a=>BigInt(call('0x70a08231'+a.slice(2).padStart(64,'0')));
const supply=BigInt(call('0x18160ddd'));
let cursor='',seen=new Set(),addresses=[];
while(true){
 assert(!seen.has(cursor),'cursor loop');seen.add(cursor);
 const page=get('nr_getTokenHolders',[fj,'0x64',cursor]);
 addresses.push(...page.details.map(x=>x.accountAddress.toLowerCase()));
 cursor=page.pageKey||'';if(!cursor)break;
}
assert.equal(new Set(addresses).size,addresses.length,'duplicate candidate');
const holders=addresses.map(a=>[a,balance(a)]).filter(x=>x[1]>0n).sort((a,b)=>a[1]>b[1]?-1:a[1]<b[1]?1:a[0].localeCompare(b[0]));
const total=holders.reduce((x,y)=>x+y[1],0n);assert.equal(total,supply);
assert.equal(holders.length,summary.holderIndex.nonzero);
for(let i=0;i<10;i++){
 assert.equal(holders[i][0],summary.top10[i].address);assert.equal(holders[i][1].toString(),summary.top10[i].atoms);
 assert.equal((get('eth_getCode',[holders[i][0],pin.number]).length-2)/2,summary.top10[i].runtimeBytes);
}
assert.equal(balance(treasury).toString(),summary.treasury.atoms);
const old=read(path.join(root,'q35-reuse/evidence/rpc.jsonl'));
const all=new Map();
for(const r of [...old,...records]){
 if(r.status!==200||r.request.method!=='eth_getLogs'||r.request.params[0].address!==fj||!Array.isArray(r.response.result))continue;
 for(const l of r.response.result){
  assert.equal(l.topics[0],topic);const k=[l.blockHash,l.transactionHash,l.logIndex].join(':');
  if(all.has(k))assert.equal(key(all.get(k)),key(l));else all.set(k,l);
 }
}
const bound=JSON.parse(fs.readFileSync(path.join(ev,'boundaries.json')));
const first=BigInt(bound['2026-10-01T00:00:00Z']);const last=BigInt(pin.number);
const lo=BigInt(bound['2026-10-12T00:00:00Z']);const hi=BigInt(bound['2026-10-18T00:00:00Z']);
const addr=t=>'0x'+t.slice(-40).toLowerCase();
const logs=[...all.values()].filter(l=>BigInt(l.blockNumber)>=first&&BigInt(l.blockNumber)<=last);
assert.equal(logs.length,summary.coverage.tokenTransfers);
const incoming=logs.filter(l=>addr(l.topics[2])===treasury);
const outgoing=logs.filter(l=>addr(l.topics[1])===treasury);
assert.equal(incoming.length,summary.coverage.treasuryInflows);assert.equal(outgoing.length,summary.coverage.treasuryOutflows);
let opening=BigInt(get('eth_call',[{to:fj,data:'0x70a08231'+treasury.slice(2).padStart(64,'0')},'0x'+(first-1n).toString(16)]));
assert.equal(opening+incoming.reduce((a,l)=>a+BigInt(l.data),0n)-outgoing.reduce((a,l)=>a+BigInt(l.data),0n),balance(treasury));
const ledger=new Map();
const html=fs.readFileSync(path.join(ev,'flapjax.html'),'utf8');
for(const m of html.matchAll(/<li class="fjx-c-item">([\s\S]*?)<\/li>/g)){
 const metas=[...m[1].matchAll(/<span class="fjx-c-meta">([\s\S]*?)<\/span>/g)].map(x=>x[1].replace(/<[^>]*>/g,''));
 const datedMeta=metas.filter(x=>/^\d{4}-\d\d-\d\d · /.test(x));assert.equal(datedMeta.length,1);const meta=datedMeta[0];
 const h=m[1].match(/https:\/\/bscscan.com\/tx\/(0x[0-9a-fA-F]{64})/)[1].toLowerCase();
 const label=meta.match(/^(\d{4}-\d\d-\d\d) · (.*?) ·/);assert(label);
 if(!ledger.has(h))ledger.set(h,[]);ledger.get(h).push({date:label[1],label:label[2]});
}
const inUTC=l=>BigInt(l.blockNumber)>=lo&&BigInt(l.blockNumber)<hi;
const qn=e=>{const m=e.label.match(/^quick task Q(\d+)$/);return m?Number(m[1]):null};
const dated=e=>e.date>='2026-10-12'&&e.date<'2026-10-18';
const quick=l=>(ledger.get(l.transactionHash)||[]).some(e=>qn(e)!==null);
const narrow=l=>(ledger.get(l.transactionHash)||[]).some(e=>qn(e)!==null&&qn(e)>=21&&qn(e)<=32);
const dquick=l=>(ledger.get(l.transactionHash)||[]).some(e=>dated(e)&&qn(e)!==null);
const dnarrow=l=>(ledger.get(l.transactionHash)||[]).some(e=>dated(e)&&qn(e)!==null&&qn(e)>=21&&qn(e)<=32);
const cohorts={retentionAllOutflows:outgoing.filter(inUTC),retentionQuickTaskLabels:outgoing.filter(l=>inUTC(l)&&quick(l)),retentionQ21to32:outgoing.filter(l=>inUTC(l)&&narrow(l)),retentionLedgerDatedQuickTasks:outgoing.filter(dquick),retentionLedgerDatedQ21to32:outgoing.filter(dnarrow)};
const result={holders:holders.length,supplyAtoms:supply.toString(),treasuryAtoms:balance(treasury).toString(),cohorts:{}};
for(const [name,ls] of Object.entries(cohorts)){
 const paid=new Map();for(const l of ls){const a=addr(l.topics[2]);paid.set(a,(paid.get(a)||0n)+BigInt(l.data));}
 let kept=0;for(const [a,v] of paid)if(balance(a)>=v)kept++;
 const got={payouts:ls.length,recipients:paid.size,retained:kept};
 for(const [k,v] of Object.entries(got))assert.equal(v,summary[name][k],`${name}.${k}`);result.cohorts[name]=got;
}
const pointer=JSON.parse(fs.readFileSync(path.join(ev,'counterexample-pointer.json')));
const receipt=get('eth_getTransactionReceipt',[pointer.transaction],secondary);
assert.equal(BigInt(receipt.status),1n);assert.equal(receipt.logs.length,1);
const seedlog=receipt.logs[0];assert.equal(seedlog.address.toLowerCase(),fj);assert.equal(addr(seedlog.topics[2]),treasury);
assert.equal(BigInt(seedlog.data).toString(),summary.counterexample.atoms);
const seedtx=get('eth_getTransactionByHash',[pointer.transaction],secondary);assert(seedtx.input.startsWith('0xa9059cbb'));assert.equal(seedtx.to.toLowerCase(),fj);
assert.equal(seedtx.from.toLowerCase(),addr(seedlog.topics[1]));
console.log(JSON.stringify(result,null,2));
console.log('PASS: independent raw-message BigInt holder, treasury, five retention cohorts and seed calculations');
