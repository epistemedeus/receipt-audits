// Independent BigInt replay: no Python imports, expected tx list or derived amounts as inputs.
import fs from 'node:fs';
import path from 'node:path';
import assert from 'node:assert/strict';
import {fileURLToPath} from 'node:url';
const root=path.dirname(fileURLToPath(import.meta.url));
const old=path.join(root,'inherited/q33-flapjax-20261021');
const files=[path.join(old,'q35-reuse/evidence/rpc.jsonl'),path.join(old,'evidence/rpc.jsonl'),path.join(root,'evidence/rpc.jsonl')];
const primary='https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3';
const treasury='0x7c34e9e21ee28a49ff0b84b61774119e6633359f', pool='0xca93ec685b8623688e6b236f9068034b298c2150', token='0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df';
const swapTopic='0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83';
const transferTopic='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const saved=new Map(),logs=new Map();
for (const f of files) for (const line of fs.readFileSync(f,'utf8').trim().split('\n')) {
 const r=JSON.parse(line); if(r.status!==200 || !('result' in r.response)) continue;
 const {method,params}=r.request;
 saved.set(JSON.stringify([r.url,method,params]),r.response.result);
 if(r.url===primary && method==='eth_getLogs') for(const l of r.response.result) logs.set(`${l.blockHash}:${l.transactionHash}:${l.logIndex}`,l);
}
const get=(m,p)=>{const k=JSON.stringify([primary,m,p]);assert(saved.has(k),`missing ${m}`);return saved.get(k);};
const w=s=>s.slice(2).match(/.{64}/g).map(s=>BigInt('0x'+s));
const signed=b=>b>>255n?b-(1n<<256n):b;
const start=BigInt(Date.parse('2026-10-09T05:00:00Z')/1000),end=BigInt(Date.parse('2026-10-22T05:00:00Z')/1000);
const found=[];let bnb=0n,fj=0n,gas=0n,minimum=null,sells=0;const days={};
for(const l of logs.values()){
 if(l.address.toLowerCase()!==pool || l.topics[0]!==swapTopic)continue;
 const tx=get('eth_getTransactionByHash',[l.transactionHash]);
 const block=get('eth_getBlockByNumber',[l.blockNumber,false]);
 const when=BigInt(block.timestamp);if(when<start||when>=end||tx.from.toLowerCase()!==treasury)continue;
 const rc=get('eth_getTransactionReceipt',[l.transactionHash]);assert.equal(rc.status,'0x1');
 const [zero,one]=w(l.data).map(signed);if(zero>0n){sells++;continue;}
 assert(one>0n);assert.equal(l.topics[2].slice(-40),treasury.slice(2));
 const outs=rc.logs.filter(x=>x.address.toLowerCase()===token&&x.topics[0]===transferTopic&&x.topics[1].slice(-40)===pool.slice(2)&&x.topics[2].slice(-40)===treasury.slice(2));
 assert.equal(outs.length,1);const amount=w(outs[0].data)[0];assert.equal(amount,-zero);
 const bn=BigInt(l.blockNumber),before='0x'+(bn-1n).toString(16);const sqrt=w(get('eth_call',[{to:pool,data:'0x3850c7bd'},before]))[0];
 const pre=get('debug_traceTransaction',[l.transactionHash,{tracer:'prestateTracer',timeout:'5s',tracerConfig:{diffMode:false}}])[treasury];
 assert.equal(BigInt(pre.nonce),BigInt(tx.nonce));const fee=BigInt(rc.gasUsed)*BigInt(rc.effectiveGasPrice);const post=BigInt(pre.balance)-BigInt(tx.value)-fee;
 // Raw block state independently closes the no-refund equation for each observed buy.
 assert.equal(post,BigInt(get('eth_getBalance',[treasury,l.blockNumber])));
 if(minimum===null||post<minimum)minimum=post;
 const day=new Date(Number(when-18000n)*1000).toISOString().slice(0,10);days[day]=(days[day]||0)+1;
 found.push({tx:l.transactionHash,bnb:one.toString(),fj:amount.toString(),sqrt:sqrt.toString(),priceNum:sqrt*sqrt,priceDen:1n<<192n,post:post.toString(),day});bnb+=one;fj+=amount;gas+=fee;
}
const expected=JSON.parse(fs.readFileSync(process.argv[2]||path.join(root,'derived/summary.json'),'utf8'));
assert.equal(found.length,expected.totals.buys);assert.equal(bnb.toString(),expected.totals.WBNB_atoms);assert.equal(fj.toString(),expected.totals.FJ_atoms);assert.equal(gas.toString(),expected.totals.gasAtoms);assert.equal(sells,0);
for(const a of found){const b=expected.buys.find(x=>x.tx===a.tx);assert(b);assert.equal(a.fj,b.FJ_atoms);assert.equal(a.bnb,b.WBNB_atoms);assert.equal(a.sqrt,b.sqrtPriceX96);assert.equal(a.post,b.postTransactionBalanceAtoms);assert.equal(a.priceNum*BigInt(b.blockBeforePrice.denominator),a.priceDen*BigInt(b.blockBeforePrice.numerator));assert.equal(b.COT.slice(0,10),a.day);}
assert.equal(expected.missedDays.join(','),'2026-10-15');assert.equal(Object.values(days).filter(x=>x===1).length,12);
// Two hand-decoded uint256 controls; do not round through Number or CSV decimals.
assert.equal(found.find(x=>x.tx.startsWith('0xbeefabdc')).fj,'24052995308271524768278040');
assert.equal(found.find(x=>x.tx.startsWith('0x172349c6')).fj,'23691113109537150143912753');
console.log(JSON.stringify({independent:'BigInt direct journal decode',buys:found.length,bnbAtoms:bnb.toString(),fjAtoms:fj.toString(),gasAtoms:gas.toString(),minimumPostAtoms:minimum.toString(),sells,allRowsCompared:true},null,2));
