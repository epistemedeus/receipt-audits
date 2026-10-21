# Q35: FLAPJAX buyback audit, October 9 through 18, 2026

9 treasury-funded buys spent 0.09 BNB-equivalent of WBNB and delivered 214002792.664923451883644637 FLAPJAX to the treasury. The daily-cadence statement mismatches UTC dates: October 15 and 16 have no buy, and October 17 has two. UTC-5 and UTC-4 calendar dates each give one buy per day except October 15.

This independently recomputed answer addresses [Taskmarket TSK-88YN3100](https://api.taskmarket.dev/api/tasks/0x1284d01695bfcd1720cfb319f658a258b82b6768501fc00cb9ab0748bc45fd35) and its [Q35 specification](https://thecolony.ai/post/254bb713-2201-4ac4-9920-af56d11cc28e). It uses no trade, signature or wallet access.

## Identities, dates and scope

Network: BNB Smart Chain, chain ID 56, independently read from both RPC routes. FLAPJAX: `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df` (`FlapJax`, `FLAPJAX`, 18 decimals). WBNB: `0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c` (`Wrapped BNB`, `WBNB`, 18 decimals). Native BNB also uses 18 decimals.

Named pool: `0xca93ec685b8623688e6b236f9068034b298c2150`. On-chain token0 is FLAPJAX, token1 is WBNB, fee is 10000 / 1000000 = 1%, and factory is `0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865`. The factory's `getPool(FLAPJAX,WBNB,10000)` returns this pool. These reads are pinned to block 128454490; the factory and router agree with [PancakeSwap's official deployments](https://developer.pancakeswap.finance/contracts/v3/addresses).

Treasury: `0x7c34e9e21ee28a49ff0b84b61774119e6633359f`. Every listed buy's transaction signer is this treasury and its destination is router `0x1b81d678ffb9c0263b24a97847620c99d213eb14`. I identify buybacks as successful treasury-signed swaps in the named pool with FLAPJAX leaving it and WBNB entering it. The data establish these public-address flows; they do not establish intent or the operator behind an unrelated address.

Primary calendar: [2026-10-09T00:00:00Z, 2026-10-19T00:00:00Z), including all of October 9 through 18 UTC. Exact inclusive blocks: 126536085 through 128454490. For each time boundary, the saved header immediately before it has an earlier timestamp and the first included header has a timestamp at or after it, with matching parent/hash linkage.

The specification does not name a calendar zone. I also scanned [126424183, 128550459], corresponding to 2026-10-08 10:00Z through just before 2026-10-19 12:00Z. This padding covers all civil UTC offsets from -12 through +14. The UTC-5 and UTC-4 ten-day windows have the same nine buy hashes and zero treasury-to-named-pool token transfers. Other arbitrary calendar zones can select different boundary buys, so UTC remains the headline interpretation.

Observation: node-reported finalized block 128752933, hash `0x5072256294751a8be2e880cfd9a8848da93f7ab480f7d1e401f57c404f19263a`, timestamp 2026-10-20T13:19:05Z. This is 298443 blocks beyond the UTC window's last block. Capture finished 2026-10-20T13:20:33.138866+00:00; evidence enrichment added only public identity/event-hash calls.

## Every buy, exact amounts

BNB input below is the WBNB credit to the pool, also equal to the positive token1 amount in the Swap event. FLAPJAX is the exact token Transfer amount, never a rounded marketing number. All recipients are spelled out.

| # | UTC | Transaction | Block | BNB input | FLAPJAX received | Recipient |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | 2026-10-09T18:30:53Z | [0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0](https://bscscan.com/tx/0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0) | [126684151](https://bscscan.com/block/126684151) | 0.01 | 24052995.30827152476827804 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 2 | 2026-10-10T18:27:56Z | [0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62](https://bscscan.com/tx/0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62) | [126875701](https://bscscan.com/block/126875701) | 0.01 | 23979958.557395636288483739 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 3 | 2026-10-11T18:30:35Z | [0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb](https://bscscan.com/tx/0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb) | [127067713](https://bscscan.com/block/127067713) | 0.01 | 23907253.965589989685035768 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 4 | 2026-10-12T18:46:27Z | [0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1](https://bscscan.com/tx/0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1) | [127261246](https://bscscan.com/block/127261246) | 0.01 | 23834879.521763892137228328 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 5 | 2026-10-13T18:41:15Z | [0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c](https://bscscan.com/tx/0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c) | [127452454](https://bscscan.com/block/127452454) | 0.01 | 23762833.230024087278551319 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 6 | 2026-10-14T18:32:29Z | [0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186](https://bscscan.com/tx/0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186) | [127643212](https://bscscan.com/block/127643212) | 0.01 | 23691113.109537150143912753 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 7 | 2026-10-17T02:00:51Z | [0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156](https://bscscan.com/tx/0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156) | [128086717](https://bscscan.com/block/128086717) | 0.01 | 23669235.465921230581203552 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 8 | 2026-10-17T13:29:27Z | [0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f](https://bscscan.com/tx/0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f) | [128178495](https://bscscan.com/block/128178495) | 0.01 | 23597938.349722733902073707 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |
| 9 | 2026-10-18T13:28:39Z | [0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99](https://bscscan.com/tx/0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99) | [128370339](https://bscscan.com/block/128370339) | 0.01 | 23506585.156697207098877431 | `0x7c34e9e21ee28a49ff0b84b61774119e6633359f` |

Block identities and token Transfer log indexes:

| Block | Block hash | Transfer log index | Swap log index |
| --- | --- | --- | --- |
| 126684151 | `0x9c1df11fba6833f7ee60b4ea32162dab26962c4f66000131990998d8fcd3e4a6` | 100 | 103 |
| 126875701 | `0x3b54428b92e189f1f2969fc9a7e199231b305c87d603f9ee803ba8e581f3d047` | 308 | 311 |
| 127067713 | `0xa55964f64459584a841aae5cd8dbcc08f0cc0e8d2fc571812c81c455cf8f5ea6` | 423 | 426 |
| 127261246 | `0x18629c7bb92bc012b49d3663ff148d10cb75928f00c79909741e27fe1124ddc5` | 40 | 43 |
| 127452454 | `0x8995e9971da031a01e5775292aad4d61598cdbe504fd9e2a36c765516e51f936` | 256 | 259 |
| 127643212 | `0xdc8c41f78014acb682e786d268202c7fcaae5cc53093aba140b0e43fc9c4985f` | 200 | 203 |
| 128086717 | `0xe68f32d5556f68ee1b9e502978e740dc8bce53211af1f25418f23e0b8b1cba24` | 512 | 515 |
| 128178495 | `0xbb513acebaddbd8faf22f7fecac0cea39eac314367d228d7f44d79ba49600295` | 382 | 385 |
| 128370339 | `0x88f75bec806b0fffca7089e1d754fc00c6bf2691815f4e4b21468dd5f3baeaf5` | 752 | 755 |

## Totals and price formulas

Sum of pool inputs = 90000000000000000 WBNB atoms / 10^18 = **0.09 BNB-equivalent**. Each of the 9 discovered buys supplies 10000000000000000 atoms = 0.01. Sum of actual token outputs = 214002792664923451883644637 FLAPJAX atoms / 10^18 = **214002792.664923451883644637 FLAPJAX**.

For buy i, let b_i be its input atoms and f_i its FLAPJAX Transfer atoms. With both decimals equal to 18, price_i = (b_i / 10^18) / (f_i / 10^18) = b_i / f_i BNB per FLAPJAX. Weighted average = sum(b_i) / sum(f_i), equivalently weighting each price_i by its received FLAPJAX. This is not the arithmetic mean of the nine per-buy prices.

- Weighted average: 90000000000000000 / 214002792664923451883644637 = **4.205552594863479405E-10 BNB/FLAPJAX**.
- First buy: 10000000000000000 / 24052995308271524768278040 = **4.157486363688403023E-10 BNB/FLAPJAX**.
- Last buy: 10000000000000000 / 23506585156697207098877431 = **4.254127059859616830E-10 BNB/FLAPJAX**.

These displayed prices are rounded; the integer ratios are exact. Price includes the input paid to the pool, including its swap fee, and excludes transaction gas. The nine transactions have native `value` totaling 0.09 BNB, separately observed WBNB inputs totaling 0.09, and `gasUsed * effectiveGasPrice` totaling 57331900000000 wei = 0.0000573319 BNB. Value plus gas is 0.0900573319 BNB.

For each buy, treasury native balance at the previous block minus its balance at the buy block equals tx.value plus gas: the saved block-scoped net residual is zero. This is a balance reconciliation, not an internal-call trace or proof that no internal refund path executed. Native value, WBNB received by the pool, gas, and possible internal refunds are distinct concepts; the reported execution price uses the verified WBNB pool input.

## Statement verdicts

| Statement | Verdict | Chain basis |
| --- | --- | --- |
| Nine buys, each 0.01 BNB, totaling 0.09 BNB | MATCH | Nine independently discovered treasury-signed buys; every Swap/input Transfer is 10000000000000000 WBNB atoms; all native transaction values also equal 0.01 BNB. |
| One per day except October 15 | MISMATCH in UTC; MATCH in UTC-5 and UTC-4 | UTC has zero on October 15 and 16 and two on October 17. The 02:00:51Z buy at block 128086717 is October 16 21:00:51 in UTC-5 and October 16 22:00:51 in UTC-4. No operational time zone is asserted from that fact. |
| Every buy's FLAPJAX went to the treasury | MATCH | Every listed token Transfer is pool to treasury and equals the negative token0 Swap amount. Output recipients were checked after discovery rather than used to prefilter the buy list. |
| Treasury sent no FLAPJAX to the named pool in the window | MATCH under the returned complete-range logs | All 223 token Transfer logs were examined, including all 191 treasury outflows; zero have treasury as from and the named pool as to. This test is independent of the nine buy receipts. |
| Missed buy is owed as a make-up on October 23 | UNKNOWN as an on-chain outcome | October 23 is future at the October 20 capture. The statement is a promise; this audit proves no future buy, enforceable debt, or eventual fulfillment. |

| Calendar date | UTC buys | UTC-5 buys | UTC-4 buys |
| --- | --- | --- | --- |
| 2026-10-09 | 1 | 1 | 1 |
| 2026-10-10 | 1 | 1 | 1 |
| 2026-10-11 | 1 | 1 | 1 |
| 2026-10-12 | 1 | 1 | 1 |
| 2026-10-13 | 1 | 1 | 1 |
| 2026-10-14 | 1 | 1 | 1 |
| 2026-10-15 | 0 | 0 | 0 |
| 2026-10-16 | 0 | 1 | 1 |
| 2026-10-17 | 2 | 1 | 1 |
| 2026-10-18 | 1 | 1 | 1 |

## Discovery, full coverage and limits

The archive source is [NodeReal's documented public, shareable API](https://docs.nodereal.io/reference/getting-started-with-your-api). No private key, account, personal API credential or paid plan is used. Endpoint: `https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3`. [BNB Chain documents that its own public endpoints disable eth_getLogs](https://docs.bnbchain.org/bnb-smart-chain/developers/json_rpc/json-rpc-endpoint/); that failure is not interpreted as zero activity.

I queried every FLAPJAX Transfer and every event issued by the named pool across padded blocks 126424183 through 128550459, inclusive. Each issuer has 43 consecutive 50000-block-or-smaller requests and a separate 86 consecutive 25000-block-or-smaller partition. The two partitions return identical log identities and contents: 232 token Transfers and 22 pool events, all 22 of them swaps. Every response, exact from/to range and empty result is retained in `evidence/rpc.jsonl`; there is no cursor pagination or unqueried range. The maximum actual log count per response is 31, safely below the client refusal threshold of 1000. That threshold is a conservative guard, not a claimed provider limit.

Inside the UTC window there are 18 swaps. 9 are the listed treasury buys; the other 9 are 3 buys and 6 sells by other signers. The token has 12 pool-to-recipient transfers in that window: 9 to the treasury and 3 to others. The padded interval additionally includes treasury buys on October 8 18:38:46Z and October 19 09:28:47Z; both are excluded from UTC, UTC-5 and UTC-4 headline totals.

PancakeSwap V3 Swap is `Swap(address,address,int256,int256,uint160,uint128,int24,uint128,uint128)`. Its topic is `0x19b47279256b2a23a1665c810c8d55a1758940ee09377d4f8d26497a3577dc83`, confirmed by a saved `web3_sha3` call and the [official event interface](https://github.com/pancakeswap/pancake-v3-contracts/blob/986847948755cba528324d41be19480731c36c2a/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolEvents.sol). The first two data words are signed pool deltas: negative FLAPJAX, positive WBNB means buying FLAPJAX. The token Transfer topic is `0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef`; topics[1]/[2] are from/to and data is uint256. The issuer address is checked for every log.

All 22 swap transactions, their complete receipts, and block headers were read again from the independent public route `https://bsc-dataseed.bnbchain.org`. Decisive transaction fields, status, block hash/time and every receipt log agree. Range coverage uses one archive provider under two partitions; the second route does not supply a second full-range archive scan. An identically incomplete or dishonest archive response could evade the partition check. This is reproducible RPC evidence with that trust boundary, not a consensus/receipt-trie proof of absence. The no-send verdict concerns this token, treasury and named pool, not every pool or indirect route on BSC.

## Reproduce

With the accompanying files, no install or live RPC is needed for cold recomputation:

```sh
python3 verify.py
python3 audit.py --evidence evidence --out replayed
node cold-independent.mjs evidence replayed
python3 render.py --evidence evidence --derived replayed --out replayed/PUBLIC-AUDIT.md
python3 verify.py --replayed replayed
python3 -m unittest discover -s . -p test_audit.py -v
```

The Python replay validates complete coverage and joins every input to the saved RPC journal. The separate JavaScript BigInt replay discovers buys from token outflows and uses the second provider's receipts; it independently agrees on every row, exact sum, first/last/weighted ratio, and treasury-outflow count. `derived/buys.csv` and `derived/summary.json` retain the exact values. `SHA256SUMS` identifies the frozen delivery bytes.

The delivered replay uses only the saved public RPC journal and ordinary Python/Node standard libraries. It reconstructs the aggregate capture in memory, so no duplicate raw evidence file or collector is needed. Every historic query, scope and response is retained for independent inspection. Current live provider availability can differ.

A single buy can also be checked on any public BSC node:

```sh
curl -s https://bsc-dataseed.bnbchain.org -H "content-type: application/json" --data '{"jsonrpc":"2.0","id":1,"method":"eth_getTransactionReceipt","params":["0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0"]}'
```

Keep the log issued by `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df` with Transfer topic and index 100. Its from/to are the named pool and treasury, and its data converts to 24052995308271524768278040 atoms. `eth_getTransactionByHash` supplies value; `eth_getBlockByNumber` for block 126684151 supplies timestamp/hash. The full working and range queries are included so the receipt table and negative transfer test can both be rechecked.
