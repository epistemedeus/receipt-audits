#!/usr/bin/env node
// Separate cold calculation: discover buys from token outflows, use SECONDARY
// receipts, and recompute directly from saved RPC messages; no Python imports.
import fs from 'node:fs';
import assert from 'node:assert/strict';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const here=path.dirname(fileURLToPath(import.meta.url));
const evidence=process.argv[2]||path.join(here,'evidence');
const derived=process.argv[3]||path.join(here,'derived');
const raw=fs.readFileSync(path.join(evidence,'rpc.jsonl'),'utf8').trim().split('\n').map(JSON.parse);
const ok=raw.filter(r=>r.status===200&&r.response.result!==undefined);
const fj='0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df',pool='0xca93ec685b8623688e6b236f9068034b298c2150',treasury='0x7c34e9e21ee28a49ff0b84b61774119e6633359f',wbnb='0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c';
const transfer='0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef';
const start=Date.parse('2026-10-09T00:00:00Z')/1000,end=Date.parse('2026-10-19T00:00:00Z')/1000;
const addr=t=>'0x'+t.slice(-40).toLowerCase();
const logkey=l=>`${l.blockHash}:${l.transactionHash}:${l.logIndex}`;
// Match the independently saved exact 50k partition, including its short last page.
const candidate=ok.filter(r=>r.request.method==='eth_getLogs'&&r.request.params[0].address===fj&&BigInt(r.request.params[0].toBlock)-BigInt(r.request.params[0].fromBlock)+1n<=50000n);
const first=Math.min(...candidate.map(r=>Number(BigInt(r.request.params[0].fromBlock))));
const last=Math.max(...candidate.map(r=>Number(BigInt(r.request.params[0].toBlock))));
const pages=[];
for(let a=first;a<=last;a+=50000){
 const b=Math.min(a+49999,last);const p=ok.find(r=>r.request.method==='eth_getLogs'&&r.request.params[0].address===fj&&Number(BigInt(r.request.params[0].fromBlock))===a&&Number(BigInt(r.request.params[0].toBlock))===b);assert(p,'missing range');pages.push(p);
}
const token=pages.flatMap(p=>p.response.result);assert.equal(new Set(token.map(logkey)).size,token.length);
const secondary=ok.filter(r=>r.url==='https://bsc-dataseed.bnbchain.org');
const find=(method,firstParam)=>{const r=secondary.find(r=>r.request.method===method&&r.request.params[0]===firstParam);assert(r,`absent secondary ${method}`);return r.response.result};
const primaryHeaders=ok.filter(r=>r.request.method==='eth_getBlockByNumber'&&r.url.includes('nodereal')).map(r=>r.response.result);
const rows=[];
for(const l of token){
 if(addr(l.topics[1])!==pool)continue;
 const tx=find('eth_getTransactionByHash',l.transactionHash);
 if(tx.from.toLowerCase()!==treasury)continue;
 const receipt=find('eth_getTransactionReceipt',l.transactionHash),block=find('eth_getBlockByNumber',l.blockNumber);
 assert.equal(receipt.status,'0x1');assert.equal(receipt.blockHash,block.hash);
 const time=Number(BigInt(block.timestamp));if(time<start||time>=end)continue;
 const saved=receipt.logs.find(x=>logkey(x)===logkey(l));assert.deepEqual(saved.topics,l.topics);assert.equal(saved.data,l.data);
 const credits=receipt.logs.filter(x=>x.address.toLowerCase()===wbnb&&x.topics[0]===transfer&&addr(x.topics[2])===pool);
 const input=credits.reduce((s,x)=>s+BigInt(x.data),0n),out=BigInt(l.data),gas=BigInt(receipt.gasUsed)*BigInt(receipt.effectiveGasPrice);
 rows.push({tx:l.transactionHash,block:Number(BigInt(l.blockNumber)),UTC:new Date(time*1000).toISOString().replace('.000Z','Z'),FJ_atoms:out.toString(),WBNB_atoms:input.toString(),native_value_atoms:BigInt(tx.value).toString(),gas_atoms:gas.toString(),recipient:addr(l.topics[2])});
}
rows.sort((a,b)=>a.block-b.block);
const sum=k=>rows.reduce((s,x)=>s+BigInt(x[k]),0n).toString();
const numerator=sum('WBNB_atoms'),denominator=sum('FJ_atoms');
// No Number conversion for monetary amounts, including at 26-digit token scales.
const gcd=(a,b)=>b===0n?a:gcd(b,a%b);
const ratio=(a,b)=>{const g=gcd(BigInt(a),BigInt(b));return [(BigInt(a)/g).toString(),(BigInt(b)/g).toString()]};
// For all treasury outflows, use block numbers derived from timestamp-boundary headers.
const byTime=t=>Math.min(...primaryHeaders.filter(b=>Number(BigInt(b.timestamp))>=t).map(b=>Number(BigInt(b.number))));
const firstUTC=byTime(start),afterUTC=byTime(end);
const inUTC=token.filter(l=>Number(BigInt(l.blockNumber))>=firstUTC&&Number(BigInt(l.blockNumber))<afterUTC);
const outflows=inUTC.filter(l=>addr(l.topics[1])===treasury),sells=outflows.filter(l=>addr(l.topics[2])===pool);
const result={method:'independent BigInt reduction of saved token logs and secondary receipts',rows,totals:{buys:rows.length,FJ_atoms:denominator,WBNB_atoms:numerator,native_value_atoms:sum('native_value_atoms'),gas_atoms:sum('gas_atoms'),weightedRatio:ratio(numerator,denominator),firstRatio:ratio(rows[0].WBNB_atoms,rows[0].FJ_atoms),lastRatio:ratio(rows.at(-1).WBNB_atoms,rows.at(-1).FJ_atoms)},coverage:{firstUTC,afterUTC,transfers:inUTC.length,treasuryOutflows:outflows.length,treasuryToPool:sells.length}};
const expected=JSON.parse(fs.readFileSync(path.join(derived,'summary.json'),'utf8'));
for(const [key,value] of Object.entries(result.totals)){
 if(key.endsWith('Ratio')){const ref=expected.totals[key==='weightedRatio'?'weightedPrice':key==='firstRatio'?'firstPrice':'lastPrice'];assert.deepEqual(value,[ref.numerator,ref.denominator]);}
 else assert.equal(value,expected.totals[key]);
}
assert.deepEqual(rows.map(x=>[x.tx,x.block,x.UTC,x.FJ_atoms,x.recipient]),expected.buys.map(x=>[x.tx,x.block,x.UTC,x.FJ_atoms,x.recipient]));
assert.equal(sells.length,expected.coverage.windowTreasuryToPool);assert.equal(outflows.length,expected.coverage.windowTreasuryOutflows);assert.equal(inUTC.length,expected.coverage.windowTokenTransfers);
fs.writeFileSync(path.join(derived,'cold-independent.json'),JSON.stringify(result,null,2)+'\n');
console.log(`Independent cold replay agrees: ${rows.length} buys, ${denominator} FJ atoms; ${inUTC.length} transfers/${outflows.length} treasury outflows/${sells.length} to pool.`);
