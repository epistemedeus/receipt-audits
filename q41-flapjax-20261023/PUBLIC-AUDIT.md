# Q41: FLAPJAX treasury buybacks, October 9–21, 2026

The named treasury made **12 buys**, spending **0.12 BNB** of WBNB pool input and receiving **284418120.150881746565276184 FLAPJAX**. There is one buy on each of 12 COT dates; **October 15 has no buy**. No treasury sale into the named pool was found in the complete audited window.

Each executed buy spends exactly 0.01 BNB, every output goes to the treasury, and no COT day has more than one treasury buy. The lowest transaction-local balance after buy plus gas is **0.036158610033772485 BNB**, above 0.025. The chain does not identify why October 15 was missed. A missing day is not evidence that the balance-floor exception caused a skip.

## Scope and identities

The [Taskmarket question](https://api.taskmarket.dev/api/tasks/0x642b0b54e35e416dacd8a6b27e6e40c63a8d0bc204218649cc229b02bdb2f074) and [linked Q41 specification](https://thecolony.ai/post/5e52843e-c2d3-4b4f-9568-b9960289563b) request October 9–21 inclusive. The announced programme runs October 9–22, fourteen dates. This audit covers the first **thirteen COT dates**, not fourteen days and not a UTC-only calendar. The [original programme thread](https://thecolony.ai/post/28acbdea-449b-4717-9517-6619a94247c8) specifies the floor after buy **plus gas**. Its displayed October 9 02:11 UTC publication falls on October 8 in COT. These current requester pages state the rules; they are not authenticated edit histories. Other answers and requester confirmations were not calculation inputs.

Audit network: BNB Smart Chain **56**. The marketplace listing is on Base **8453**; those are separate networks. Pool calls verify token0 FLAPJAX `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df`, token1 WBNB `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c`, **18 decimals each**, fee 10000 (1%), and the PancakeSwap V3 factory binding. Treasury: `0x7c34e9e21ee28a49ff0b84b61774119e6633359f`. Pool: `0xca93ec685b8623688e6b236f9068034b298c2150`.

The interval is **2026-10-09T05:00:00Z ≤ timestamp < 2026-10-22T05:00:00Z**: blocks **126576071–129070212** inclusive. Saved adjacent boundary headers prove both endpoints. Finalized observation: block **129254769**, `0xd62a9c36500c55aad2178cc20316cf2c8c21925e77327811846ff2fa0a686bac`, 2026-10-23T04:04:41Z; both public routes return its hash.

## Every treasury buy

Amounts are exact decimal renderings of uint256 atoms. Prices are BNB per FLAPJAX, rounded here to 19 significant digits; exact rational numerators, denominators, block hashes, sqrtPriceX96, receipt indices and all raw state reads are in [summary.json](derived/summary.json) and [buys.csv](derived/buys.csv).

| Transaction | Block | UTC | COT (UTC-5) | BNB in | FLAPJAX out | Effective price | Pool at block-1 |
| --- | ---: | --- | --- | ---: | ---: | ---: | ---: |
| [0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0](https://bscscan.com/tx/0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0) | 126684151 | 2026-10-09T18:30:53Z | 2026-10-09T13:30:53-05:00 | 0.01 | 24052995.30827152476827804 | 4.157486363688403023E-10 | 4.109653030008281900E-10 |
| [0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62](https://bscscan.com/tx/0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62) | 126875701 | 2026-10-10T18:27:56Z | 2026-10-10T13:27:56-05:00 | 0.01 | 23979958.557395636288483739 | 4.170148991736230286E-10 | 4.122179500935193488E-10 |
| [0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb](https://bscscan.com/tx/0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb) | 127067713 | 2026-10-11T18:30:35Z | 2026-10-11T13:30:35-05:00 | 0.01 | 23907253.965589989685035768 | 4.182830874007163412E-10 | 4.134725033542979881E-10 |
| [0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1](https://bscscan.com/tx/0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1) | 127261246 | 2026-10-12T18:46:27Z | 2026-10-12T13:46:27-05:00 | 0.01 | 23834879.521763892137228328 | 4.195532010501202402E-10 | 4.147289627831641078E-10 |
| [0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c](https://bscscan.com/tx/0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c) | 127452454 | 2026-10-13T18:41:15Z | 2026-10-13T13:41:15-05:00 | 0.01 | 23762833.230024087278551319 | 4.208252401218347256E-10 | 4.159873283801177081E-10 |
| [0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186](https://bscscan.com/tx/0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186) | 127643212 | 2026-10-14T18:32:29Z | 2026-10-14T13:32:29-05:00 | 0.01 | 23691113.109537150143912753 | 4.220992046158597972E-10 | 4.172476001451587888E-10 |
| [0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156](https://bscscan.com/tx/0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156) | 128086717 | 2026-10-17T02:00:51Z | 2026-10-16T21:00:51-05:00 | 0.01 | 23669235.465921230581203552 | 4.224893539294041531E-10 | 4.176335563730760880E-10 |
| [0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f](https://bscscan.com/tx/0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f) | 128178495 | 2026-10-17T13:29:27Z | 2026-10-17T08:29:27-05:00 | 0.01 | 23597938.349722733902073707 | 4.237658329214804436E-10 | 4.188963174911878754E-10 |
| [0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99](https://bscscan.com/tx/0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99) | 128370339 | 2026-10-18T13:28:39Z | 2026-10-18T08:28:39-05:00 | 0.01 | 23506585.156697207098877431 | 4.254127059859616830E-10 | 4.205254943041065388E-10 |
| [0xd5210869e5cec642146b3f39590647b313d102f70a51b7c7bbf0c287ceff095d](https://bscscan.com/tx/0xd5210869e5cec642146b3f39590647b313d102f70a51b7c7bbf0c287ceff095d) | 128530306 | 2026-10-19T09:28:47Z | 2026-10-19T04:28:47-05:00 | 0.01 | 23545510.421021461800775637 | 4.247094168352361229E-10 | 4.198297619605386305E-10 |
| [0xe9ea4a165aae8eb4228ef073a93c4c1983894104a426e9f5d64b0214cfde3369](https://bscscan.com/tx/0xe9ea4a165aae8eb4228ef073a93c4c1983894104a426e9f5d64b0214cfde3369) | 128754269 | 2026-10-20T13:29:06Z | 2026-10-20T08:29:06-05:00 | 0.01 | 23439984.330262304385516624 | 4.266214456077708190E-10 | 4.217212470891907940E-10 |
| [0xbf984ef91d8df34f75998aa40bb539db84085cc1f1654cd5106de7e3db0be48f](https://bscscan.com/tx/0xbf984ef91d8df34f75998aa40bb539db84085cc1f1654cd5106de7e3db0be48f) | 128946201 | 2026-10-21T13:29:29Z | 2026-10-21T08:29:29-05:00 | 0.01 | 23429832.734674528495339286 | 4.268062906484472300E-10 | 4.219041062459925130E-10 |

Total WBNB input: `120000000000000000` atoms = **0.12 BNB**. Total token output: `284418120150881746565276184` atoms = **284418120.150881746565276184 FLAPJAX**. Weighted effective price is **4.219140466027300643E-10 BNB/FLAPJAX**, the ratio of totals, not the arithmetic mean of daily prices.

## Price and native-value formulas

Let `a1 > 0` be the pool Swap WBNB delta and `a0 < 0` the FLAPJAX delta. The PancakeSwap-specific Swap event has seven non-indexed ABI words, including two protocol-fee words; it is not the five-word Uniswap event. Receipt token Transfers independently match `a1` WBNB credited to the pool and `-a0` FLAPJAX debited from it to the treasury. The [official event interface](https://github.com/pancakeswap/pancake-v3-contracts/blob/986847948755cba528324d41be19480731c36c2a/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolEvents.sol) defines deltas from the pool perspective and the event sqrt price after the swap.

With received decimals `d0 = d1 = 18`: effective BNB/FLAPJAX = `(a1 / 10^18) / (-a0 / 10^18) = a1 / -a0`. Weighted price = `sum(a1) / sum(-a0)`. For `s = slot0().sqrtPriceX96` read at block `buyBlock - 1`, pool spot WBNB/FLAPJAX = `(s² / 2^192) × 10^(d0-d1) = s² / 2^192`. The [official slot0 interface](https://github.com/pancakeswap/pancake-v3-contracts/blob/986847948755cba528324d41be19480731c36c2a/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolState.sol) supplies its Q64.96 meaning. This spot excludes fees and trade impact; it is not an executable quote.

No earlier pool Swap appears in any of the twelve buy blocks. The report preserves the requested **block-before** read explicitly. In general, another swap earlier in a shared block can make that read differ from immediate pre-swap state; this replay records earlier swaps and does not silently treat any block-before price as transaction-local state.

Native transaction value and WBNB pool input are separately received and each totals `120000000000000000` atoms = 0.12 BNB here. Gas = `gasUsed × effectiveGasPrice`, totalling `76458500000000` wei = **0.0000764585 BNB**. Total treasury native debit on these transactions is **0.1200764585 BNB**. Successful native call trees show zero treasury refunds and zero extra internal native outflows in these buys. That evidence, rather than equality assumed from tx.value, separates spending, wrapping, gas and refunds.

## Floor and ordering evidence

Transaction prestate is received with `debug_traceTransaction(hash, {tracer:"prestateTracer", tracerConfig:{diffMode:false}})`. The treasury nonce matches the transaction nonce. The [Geth native tracer documentation](https://geth.ethereum.org/docs/developers/evm-tracing/built-in-tracers) defines prestate and call traces. Successful call frames give actual native refunds and additional outflows. For each buy: `post = pre - tx.value - gasUsed × effectiveGasPrice + nativeRefunds - extraNativeOut`. A failed call and its descendants contribute no committed transfer. Full ordered blocks bind transactionIndex. No earlier direct treasury transaction appears in these blocks.

| COT date | Pre-transaction BNB | Buy native value | Gas BNB | Post-transaction BNB | Floor |
| --- | ---: | ---: | ---: | ---: | --- |
| 2026-10-09 | 0.18685948641 | 0.01 | 0.0000063741 | 0.17685311231 | KEPT |
| 2026-10-10 | 0.164703604959380905 | 0.01 | 0.0000063741 | 0.154697230859380905 | KEPT |
| 2026-10-11 | 0.154646461259380905 | 0.01 | 0.0000063777 | 0.144640083559380905 | KEPT |
| 2026-10-12 | 0.142613528959380905 | 0.01 | 0.0000063764 | 0.132607152559380905 | KEPT |
| 2026-10-13 | 0.128270955846597688 | 0.01 | 0.0000063763 | 0.118264579546597688 | KEPT |
| 2026-10-14 | 0.116954348228579177 | 0.01 | 0.0000063763 | 0.106947971928579177 | KEPT |
| 2026-10-16 | 0.10422003565479818 | 0.01 | 0.0000063262 | 0.09421370945479818 | KEPT |
| 2026-10-17 | 0.09418014865479818 | 0.01 | 0.0000063757 | 0.08417377295479818 | KEPT |
| 2026-10-18 | 0.08409591095479818 | 0.01 | 0.0000063751 | 0.07408953585479818 | KEPT |
| 2026-10-19 | 0.071686772029709148 | 0.01 | 0.0000063763 | 0.061680395729709148 | KEPT |
| 2026-10-20 | 0.056236887533772485 | 0.01 | 0.0000063755 | 0.046230512033772485 | KEPT |
| 2026-10-21 | 0.046164984833772485 | 0.01 | 0.0000063748 | 0.036158610033772485 | KEPT |

Every prestate balance also equals the received block-before treasury balance, and every reconstructed poststate equals the block-end balance, with zero residual in all twelve cases. These equalities are cross-checks; a later balance by itself would not establish pre-transaction state. Historical state and traces were available from the documented NodeReal public demonstration route. A probe on the BNB dataseed route returns `missing trie node` for balance, prestate and slot0. State therefore retains one-provider trust, even though decisive receipts, transactions and headers agree across both endpoint families. Shared backend independence is not proved.

## Rules and calendar

| Rule | Verdict | Decisive evidence |
| --- | --- | --- |
| Each buy spends 0.01 BNB | KEPT | All 12 signed Swap inputs and matching WBNB pool credits equal 10^16 atoms. |
| Buy-only in the named pool | KEPT | All 12 treasury swaps buy FLAPJAX, outputs go to treasury; zero treasury FLAPJAX Transfers to the named pool in the complete window. |
| At most one buy per COT day | KEPT | One each on October 9–14 and 16–21; zero on October 15. The October 17 02:00:51 UTC transaction belongs to October 16 COT. |
| Skip a buy that would leave less than 0.025 BNB | KEPT for executed buys | Transaction-local prestate and native flow, including gas, leave at least 0.036158610033772485 BNB. No executed violating buy. |
| Daily schedule through October 21 | 12 of 13 dates filled | October 15 is missed. Whether that miss was an allowed floor skip is UNKNOWN: no scheduled-time counterfactual or decision evidence is supplied by these swaps. |

The announced October 22 date and any later make-up fall outside the requested window. This report does not classify a future promise as fulfillment. [calendar.csv](derived/calendar.csv) includes every audited date.

## Complete bounded discovery and replay

The replay checks **334 FLAPJAX Transfer logs**, **31 pool events/swaps**, and **312 related transactions** in the requested interval. There are 12 treasury buys and 19 swaps attributed to other signers/recipients, listed in [other-swaps.csv](derived/other-swaps.csv). All 280 treasury token outflows are itemized in [treasury-outflows.csv](derived/treasury-outflows.csv); none sends FLAPJAX to this pool. Their non-pool payment purposes are outside this buyback audit, not automatically sales. There are no unclassified treasury pool swaps. This is not a token-lifetime or all-venues no-sale claim.

Each segment is queried twice using contiguous, non-overlapping 50,000-block and 25,000-block partitions. Both partitions must agree on canonical log identities and bytes; every response is below the 1,000-log refusal threshold. Requests have explicit fromBlock/toBlock, no unreceived pagination cursor. Complete token and pool receipt logs must match their scans, so a pool omission in both partitions is still caught when its token receipt is present. A missing request, duplicate, gap, failed receipt or truncated partition fails closed. Empty results are accepted only for a saved successful bounded request. Common omissions by a faulty RPC across all evidence remain an RPC-trust limit.

| Capture segment | First block | Last block | 50k requests | 25k requests | Logs | Origin |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| token | 126424183 | 128550459 | 43 | 86 | 232 | retained public capture |
| token | 128550460 | 128867609 | 7 | 13 | 66 | retained public capture |
| token | 128867610 | 129070212 | 5 | 9 | 38 | new Q41 capture |
| pool | 126424183 | 128550459 | 43 | 86 | 22 | retained public capture |
| pool | 128550460 | 129070212 | 11 | 21 | 10 | new Q41 capture |

The retained [Q35 package](https://github.com/epistemedeus/receipt-audits/tree/f6f99bd5f9b810fc447e4907c5bfcb88ef9549b5/q35-flapjax-20261020) and [Q33 package](https://github.com/epistemedeus/receipt-audits/tree/8f1a10148a483c970bf8695789acf05f8541c478/q33-flapjax-20261021) supply unchanged raw captures, tested integer decoders and exact earlier partitions. They were received at index head `563a9e91dfe4dd4c2e98ff5ac32c22a42e63ce62`. Both original packages replay before this extension is received. Their old windows are not promoted to cover October 21. New work extends token/pool coverage, receives the final buy, prices and transaction-local balance/flow evidence, and tests COT/rule/state failure cases. See [NOTICE.md](NOTICE.md) for attribution and [README.md](README.md) for serial cold commands.

New and inherited request/response journals are public evidence, including failed reads. The [source manifest](evidence/SOURCES.json) records requester and official-document capture clocks, URLs and hashes. The [BNB endpoint documentation](https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/) and [NodeReal public endpoint documentation](https://docs.nodereal.io/reference/getting-started-with-your-api) identify the read routes. Live availability can change. No account, signing key, purchase or paid API is required by this recipe.

Cold replay from this package, using only Python and Node standard libraries:

```sh
python3 cold.py --out replayed
```

This verifies saved-file checksums, reruns the inherited checks, recomputes every table and this report, independently decodes the journals with BigInt, runs serial failure/recovery tests, and compares generated outputs byte for byte. The report supports the named-window rule findings and preserves the exact remaining unknowns; it makes no motive, investment, token-return or award claim.
