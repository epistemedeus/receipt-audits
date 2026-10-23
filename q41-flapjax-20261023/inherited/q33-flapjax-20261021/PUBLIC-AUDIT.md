# FLAPJAX holder distribution, treasury flows and Receipt Relay retention

At BSC block **128867609**, **264 addresses** have nonzero FLAPJAX balances. Treasury holds **277115377.391760699304473698 FLAPJAX**, **0.623509599137%** of supply, rank **24**. For requester-ledger-dated Q21–Q32 Relay payouts, **18/19** recipients hold a balance at least as large as their cumulative payout.

**Treasury statement: MISMATCH under its literal all-time wording.** A direct seed allocation entered treasury without a swap. The observed October operational window has verified buys in and no direct transfer to either verified V3 pool. Purpose and historical limits follow.

## Snapshot, token and complete holder list

Chain **56**, [block 128867609](https://bscscan.com/block/128867609), **2026-10-21T03:39:48Z**, hash `0xeb1bcf5506298aed6e64dc423c538e81c6a006dc2bb1d852d0753876aa4d1fef`. NodeReal returned this block for `finalized`; its explicit block/hash was independently re-read on the BNB public node. Token [`0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df`](https://bscscan.com/address/0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df), **FlapJax**, **18 decimals**. `totalSupply()` = **44444444444 FLAPJAX**, exactly `44444444444000000000000000000` base units.

The [NodeReal holder index](https://docs.nodereal.io/reference/nr_gettokenholders) supplied **3 cursor pages**, using `nr_getTokenHolders([token, "0x64", pageKey])` from an empty first cursor through an empty final next cursor. Its **264 distinct candidates** were each read with `balanceOf(address)` at the explicit snapshot block. All **264** are positive; their sum equals totalSupply exactly, with **0 base-unit gap**. The [full holder CSV](derived/holders.csv) includes every address and exact balance. This is completeness by a suitable index plus balance/supply reconciliation for nonnegative, supply-conserving token balances, not a cryptographic proof of the provider's state.

The index itself is current, not historical. The separate `nr_getTokenHolderCount` probe returned 260 while the three pages and pinned balances produce 264; that aggregate is not used as the answer. BscScan holder-page requests were HTTP 403. Contracts, dust and the dead address are included; shares use total supply, including burn-destination balances.

| Rank | Address | FLAPJAX | Supply share | Runtime bytes | Classification |
| --- | --- | --- | --- | --- | --- |
| 1 | [`0xca93ec685b8623688e6b236f9068034b298c2150`](https://bscscan.com/address/0xca93ec685b8623688e6b236f9068034b298c2150) | 20087077681.692129968642878775 | 45.195924784259% | 22962 | V3 pool; factory-bound |
| 2 | [`0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e`](https://bscscan.com/address/0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e) | 5619844348.59899399876916397 | 12.644649784474% | 22962 | V3 pool; factory-bound |
| 3 | [`0x58fab046ce77064bf52c2eff4e163eb84386b8b4`](https://bscscan.com/address/0x58fab046ce77064bf52c2eff4e163eb84386b8b4) | 2334009348.875 | 5.251521035021% | 0 | Empty code; EOA-compatible |
| 4 | [`0x000000000000000000000000000000000000dead`](https://bscscan.com/address/0x000000000000000000000000000000000000dead) | 1923471159.703770945293578174 | 4.327810109376% | 0 | Dead destination; empty code |
| 5 | [`0x2ea90ff709b0fb5decd1de944f644eecdc26d33a`](https://bscscan.com/address/0x2ea90ff709b0fb5decd1de944f644eecdc26d33a) | 1175621343.19894075159163011 | 2.645148022224% | 0 | Empty code; EOA-compatible |
| 6 | [`0x8e3dc66bb96b063afb932660fb5d060e170cf2cd`](https://bscscan.com/address/0x8e3dc66bb96b063afb932660fb5d060e170cf2cd) | 747196241.459736162058309614 | 1.681191543301% | 0 | Empty code; EOA-compatible |
| 7 | [`0x238a358808379702088667322f80ac48bad5e6c4`](https://bscscan.com/address/0x238a358808379702088667322f80ac48bad5e6c4) | 656406577.756686571074653408 | 1.476914799967% | 8347 | Sourcify-verified Vault |
| 8 | [`0xf0e319587b54db351f4a20e2da09848fed4d8151`](https://bscscan.com/address/0xf0e319587b54db351f4a20e2da09848fed4d8151) | 621698620.153862035019976481 | 1.39882189536% | 0 | Empty code; EOA-compatible |
| 9 | [`0x5dedb37eaa9145dd1a17d385d8c5e256871d6f16`](https://bscscan.com/address/0x5dedb37eaa9145dd1a17d385d8c5e256871d6f16) | 611866236.479140970515983357 | 1.376699032091% | 0 | Empty code; EOA-compatible |
| 10 | [`0x9a937a531a3e4b7930a49548b64c4a3471d049e2`](https://bscscan.com/address/0x9a937a531a3e4b7930a49548b64c4a3471d049e2) | 610074149.236058951494657443 | 1.372666835794% | 0 | Empty code; EOA-compatible |

Percent displays are truncated to at most 12 decimal places. Exact reduced rational percentages are retained in [summary.json](derived/summary.json). Equal-balance ties sort by lowercase address. Empty runtime code does not establish private-key control, a person or beneficial ownership. The dead address is not counted as an ordinary spendable wallet.

[`0xca93ec685b8623688e6b236f9068034b298c2150`](https://bscscan.com/address/0xca93ec685b8623688e6b236f9068034b298c2150): factory-bound V3 pool; 0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df/0xbb4cdb9cbd36b01bd1cbaebf2de08d9173bc095c; fee 10000; factory 0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865. Pool token0/token1, fee and factory are read at the pin; factory getPool(token0,token1,fee) returns the same address. This verifies pool identity beyond an explorer nickname.

[`0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e`](https://bscscan.com/address/0x740a3b4a91cb8fa47e85d7f9713ca6ec2f8a037e): factory-bound V3 pool; 0x7130d2a12b9bcbfae4f2634d864a1ee1ce3ead9c/0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df; fee 10000; factory 0x0bfbcf9fa4f9c56b0f40a671ad40e0805a091865. Pool token0/token1, fee and factory are read at the pin; factory getPool(token0,token1,fee) returns the same address. This verifies pool identity beyond an explorer nickname.

The third contract is [Sourcify-verified `src/Vault.sol:Vault`](https://sourcify.dev/server/v2/contract/56/0x238a358808379702088667322f80ac48bad5e6c4?fields=runtimeBytecode.onchainBytecode,compilation). Its published runtime bytes exactly equal the pinned eth_getCode response. This identifies a vault implementation; it does not establish time locks, users or beneficial owners. No locker or launchpad identity is inferred from a nickname.

## Treasury statement and transactions

Treasury [`0x7c34e9e21ee28a49ff0b84b61774119e6633359f`](https://bscscan.com/address/0x7c34e9e21ee28a49ff0b84b61774119e6633359f) holds `277115377391760699304473698` base units. Share = `100 × balance / totalSupply`, exactly `138557688695880349652236849/222222222220000000000000000` percent.

**Literal buyback-only inflows: MISMATCH.** [`0x50fd50af15a62942e1c443da634e06c103243fd9eca2f3c9bc7875df39b631d9`](https://bscscan.com/tx/0x50fd50af15a62942e1c443da634e06c103243fd9eca2f3c9bc7875df39b631d9), block **121836175**, **2026-09-14T12:16:41Z**, transfers **10000000 FLAPJAX** from [`0x2ea90ff709b0fb5decd1de944f644eecdc26d33a`](https://bscscan.com/address/0x2ea90ff709b0fb5decd1de944f644eecdc26d33a) directly to treasury. The source has empty runtime code at that block. It directly calls this token's transfer(address,uint256), with zero native value and exactly one receipt log: the matching Transfer. There is no swap. Treasury's actual block balance changes from `0` to `10000000000000000000000000` base units. Both public nodes agree on the transaction, receipt and block hash `0x6938a9149ad3349de9f098cc58589db24f5392e9dd009b831e4a24e1f25fe2a8`.

A prior public audit supplied only this transaction locator; quantities and participants above are independently decoded from the two public nodes. This proves an on-chain non-swap seed allocation. Off-chain consideration is unknown. If the intended policy excludes initial setup, the seed is an excluded setup event, not evidence of a treasury sale; the question gives no such exclusion, so literal and operational readings remain distinct.

The bounded operational window is **2026-10-01 00:00:00 UTC through the snapshot**, inclusive blocks **125000755–128867609**. Its **310 Transfer logs** are covered by matching 50,000- and 25,000-block query partitions, with no range reaching the 1,000-log refusal threshold. Every treasury transaction has a successful receipt and matching header. There are **12 inflows** and **260 outflows**.

**Buyback buys in: MATCH within this window.** All **12** inflows are treasury-signed primary-pool buys. Each Swap has negative FLAPJAX amount0, positive WBNB amount1, treasury recipient, an exact matching FLAPJAX Transfer and exact matching WBNB input to the pool. All 12 receipts also match the independent node.

| UTC | Block | FLAPJAX received | Transaction |
| --- | --- | --- | --- |
| 2026-10-08T18:38:46Z | 126493263 | 12053990.789102625866817979 | [`0x3cec62e37b0b0fc60baa6449d38939c1d6a23446af0b5ce7247da8b3a6417fea`](https://bscscan.com/tx/0x3cec62e37b0b0fc60baa6449d38939c1d6a23446af0b5ce7247da8b3a6417fea) |
| 2026-10-09T18:30:53Z | 126684151 | 24052995.30827152476827804 | [`0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0`](https://bscscan.com/tx/0xbeefabdc89f9148f9daaef6082d34a60dc5b4b612972ca0fd39d6bd4eb03b4b0) |
| 2026-10-10T18:27:56Z | 126875701 | 23979958.557395636288483739 | [`0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62`](https://bscscan.com/tx/0x8ce8e8578da26f8c7acb0f44c6ca0d0b8dcba868cafe2d729bb48562863f2d62) |
| 2026-10-11T18:30:35Z | 127067713 | 23907253.965589989685035768 | [`0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb`](https://bscscan.com/tx/0x82d01172ae26f1c86287643e123af1675ca5c18b984b7740c1a0c1647d2801eb) |
| 2026-10-12T18:46:27Z | 127261246 | 23834879.521763892137228328 | [`0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1`](https://bscscan.com/tx/0x9afdc96e3ca876b5b617a26ba5105012ed8c33e805c77b1616bf48c198d5cbf1) |
| 2026-10-13T18:41:15Z | 127452454 | 23762833.230024087278551319 | [`0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c`](https://bscscan.com/tx/0xc94de373d1fb00093431224a97475b3b2b48b9a4962d15acbe9d9c5c016d720c) |
| 2026-10-14T18:32:29Z | 127643212 | 23691113.109537150143912753 | [`0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186`](https://bscscan.com/tx/0x172349c64ed3c45663650049f9e2ad3d763b1243c5c849b7d66f144f221d3186) |
| 2026-10-17T02:00:51Z | 128086717 | 23669235.465921230581203552 | [`0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156`](https://bscscan.com/tx/0xc999000f16f326e8868fe37f83871219be1a63f98043b0aef9ee57f469232156) |
| 2026-10-17T13:29:27Z | 128178495 | 23597938.349722733902073707 | [`0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f`](https://bscscan.com/tx/0x6ec66780e0518da7c3c8b55d13b66d57400046f89ebe9df479c3c878f7b3311f) |
| 2026-10-18T13:28:39Z | 128370339 | 23506585.156697207098877431 | [`0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99`](https://bscscan.com/tx/0x05a9acf81b0eae4b7ff9a12168aead25964b6b2c0a16d3d1e667b7db6f17ad99) |
| 2026-10-19T09:28:47Z | 128530306 | 23545510.421021461800775637 | [`0xd5210869e5cec642146b3f39590647b313d102f70a51b7c7bbf0c287ceff095d`](https://bscscan.com/tx/0xd5210869e5cec642146b3f39590647b313d102f70a51b7c7bbf0c287ceff095d) |
| 2026-10-20T13:29:06Z | 128754269 | 23439984.330262304385516624 | [`0xe9ea4a165aae8eb4228ef073a93c4c1983894104a426e9f5d64b0214cfde3369`](https://bscscan.com/tx/0xe9ea4a165aae8eb4228ef073a93c4c1983894104a426e9f5d64b0214cfde3369) |

Window conservation, in base units: opening `170293099186450855367718821` + inflows `273042278205309843936754877` − outflows `166220000000000000000000000` = closing `277115377391760699304473698`, with **0 gap**. Opening is an actual balanceOf at block 125000754, not an assumed zero.

**No direct treasury sale to the two verified pools: MATCH in this bounded window.** Exactly **0** outflows reach either verified pool; **260/260** outflow transactions directly call the token's transfer method from treasury, and **0** outflow receipts contain the known V3 Swap event. This does not certify all-time behavior, undiscovered pools, intermediary/common-control wallets or off-chain deals. A payee's later sale is not relabelled as a treasury sale.

**Bounty-purpose outflows: qualified.** **256/260** outflows have receipt-linked work/reward labels on the [requester ledger](https://flapjax.surge.sh/). They are first-party purpose assertions, not on-chain proof of performed work. The following **4** have no captured label, preventing unconditional purpose MATCH:

| UTC | Destination | FLAPJAX | Transaction |
| --- | --- | --- | --- |
| 2026-10-04T15:25:29Z | [`0xfb200657f7266157a45dfcc6c09690726daa24e6`](https://bscscan.com/address/0xfb200657f7266157a45dfcc6c09690726daa24e6) | 100000 | [`0x54d1530fb2cf7fce74a6800e8038f807475185e68c273ea5be3b33902777e32a`](https://bscscan.com/tx/0x54d1530fb2cf7fce74a6800e8038f807475185e68c273ea5be3b33902777e32a) |
| 2026-10-06T12:45:22Z | [`0x4d2a5410f0d0733c0448e91e47608ebdc918a806`](https://bscscan.com/address/0x4d2a5410f0d0733c0448e91e47608ebdc918a806) | 100000 | [`0xa61a1f04855d06b917c11e92ebdd27a18f3a31161ec22bb740eee3d661488c42`](https://bscscan.com/tx/0xa61a1f04855d06b917c11e92ebdd27a18f3a31161ec22bb740eee3d661488c42) |
| 2026-10-06T12:45:38Z | [`0x6e9c17439cf81247965f9543645cfc8e746c4588`](https://bscscan.com/address/0x6e9c17439cf81247965f9543645cfc8e746c4588) | 100000 | [`0xf2fe1185498ef36144f767d42241935a945b150388e43e2d3124c963d421f061`](https://bscscan.com/tx/0xf2fe1185498ef36144f767d42241935a945b150388e43e2d3124c963d421f061) |
| 2026-10-06T12:45:55Z | [`0x6e9c17439cf81247965f9543645cfc8e746c4588`](https://bscscan.com/address/0x6e9c17439cf81247965f9543645cfc8e746c4588) | 250000 | [`0x948a3f419ecaa46d7111a212a459676fd62894adaf9043a772d70d09c5bc8052`](https://bscscan.com/tx/0x948a3f419ecaa46d7111a212a459676fd62894adaf9043a772d70d09c5bc8052) |

Ledger amount note: [`0x482580b912e89174363cda51f79c5881cab9253f870ad9f6caa992cb6a006e98`](https://bscscan.com/tx/0x482580b912e89174363cda51f79c5881cab9253f870ad9f6caa992cb6a006e98) actually transfers **200000 FLAPJAX**. Its displayed text says **500,000 FLAPJAX (200,000 sent in this tx; 300,000 withheld with the agent's consent for listing L001)**. The receipt amount, not the headline or withheld amount, enters paid totals.

## Receipt Relay retention, October 12–17

Retention means **snapshot balance ≥ the sum of actual payout Transfer amounts to an address in the selected cohort**. Multiple payouts are aggregated before comparison. Fungible balances do not prove that the same received units never moved, and disposal followed by replenishment remains possible. An absent balance is never silently treated as zero.

The strict Relay cohort is requester-ledger labels **quick task Q21–Q32**, dated **October 12–17 inclusive**: **24 receipt-verified payouts**, **19 distinct addresses**, **18 holding at least the cumulative payout**. This follows the requester thread's distinction between Relay questions and older pinned quick tasks. A ledger date is not necessarily a UTC payment date.

| Address | Payout, FLAPJAX | Snapshot balance, FLAPJAX | Balance ≥ payout |
| --- | --- | --- | --- |
| [`0x078293f144c61d1e02b49d4cd3f33c283eb7dc73`](https://bscscan.com/address/0x078293f144c61d1e02b49d4cd3f33c283eb7dc73) | 250000 | 1000000 | yes |
| [`0x1becfb9e7cfc39667f8608909f3013c4bdbbfc92`](https://bscscan.com/address/0x1becfb9e7cfc39667f8608909f3013c4bdbbfc92) | 250000 | 250000 | yes |
| [`0x24a29c98a5a18058b8989cea7f942c586dceeea6`](https://bscscan.com/address/0x24a29c98a5a18058b8989cea7f942c586dceeea6) | 250000 | 250000 | yes |
| [`0x3d98800c64c345950e1eaaa076d88c12d1bf5f37`](https://bscscan.com/address/0x3d98800c64c345950e1eaaa076d88c12d1bf5f37) | 350000 | 1950000 | yes |
| [`0x5c7a79549e4413a52b1787b5c7e10368720d2358`](https://bscscan.com/address/0x5c7a79549e4413a52b1787b5c7e10368720d2358) | 250000 | 2600000 | yes |
| [`0x8532ff85f7d16a869945d8abb52893d73d2118ef`](https://bscscan.com/address/0x8532ff85f7d16a869945d8abb52893d73d2118ef) | 250000 | 250000 | yes |
| [`0x8785fa9111aa458117f766831fae5bdcaa6ae427`](https://bscscan.com/address/0x8785fa9111aa458117f766831fae5bdcaa6ae427) | 250000 | 250000 | yes |
| [`0x8c062dc5d775b7d5efc168f75a875f392f53dcdf`](https://bscscan.com/address/0x8c062dc5d775b7d5efc168f75a875f392f53dcdf) | 850000 | 19808776.72683323748647157 | yes |
| [`0x9067e71d30cf136f767ae4fd1ea0517314ac0982`](https://bscscan.com/address/0x9067e71d30cf136f767ae4fd1ea0517314ac0982) | 250000 | 1550000 | yes |
| [`0x9912d22ab4f1856fb3571c6c68f2571904ace4b9`](https://bscscan.com/address/0x9912d22ab4f1856fb3571c6c68f2571904ace4b9) | 250000 | 1000000 | yes |
| [`0xa1e397bd64189092198d0b4301a4d17550c28dc6`](https://bscscan.com/address/0xa1e397bd64189092198d0b4301a4d17550c28dc6) | 250000 | 300000 | yes |
| [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | 250000 | 8750000 | yes |
| [`0xba567fea152c93b38513a44e1da3cbbee7f3b1dd`](https://bscscan.com/address/0xba567fea152c93b38513a44e1da3cbbee7f3b1dd) | 250000 | 750000 | yes |
| [`0xc3b4f10bc4c4a64676b398ebbe23b29440dca40c`](https://bscscan.com/address/0xc3b4f10bc4c4a64676b398ebbe23b29440dca40c) | 250000 | 0 | no |
| [`0xc8799d53f301c4917a1e6d863057734d9a848e84`](https://bscscan.com/address/0xc8799d53f301c4917a1e6d863057734d9a848e84) | 250000 | 3070000 | yes |
| [`0xcf4cac88df345bf16b550ca02fe4e1d1b27860d3`](https://bscscan.com/address/0xcf4cac88df345bf16b550ca02fe4e1d1b27860d3) | 250000 | 3100000 | yes |
| [`0xcfa08d418f136cc2a14c791fcf7e37b30d237592`](https://bscscan.com/address/0xcfa08d418f136cc2a14c791fcf7e37b30d237592) | 250000 | 250000 | yes |
| [`0xe8797a6bb4693674d78e933e85cb159a0219d03b`](https://bscscan.com/address/0xe8797a6bb4693674d78e933e85cb159a0219d03b) | 250000 | 24600000 | yes |
| [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8) | 500000 | 1070000 | yes |

| Cohort / date interpretation | Payouts | Recipients | Balance ≥ payout |
| --- | --- | --- | --- |
| Q21–Q32; ledger dates | 24 | 19 | 18 |
| Q21–Q32; actual UTC dates | 23 | 18 | 17 |
| All quick-Q labels; ledger dates | 70 | 31 | 28 |
| All quick-Q labels; UTC dates | 70 | 30 | 27 |
| All treasury outflows; UTC dates | 120 | 53 | 47 |

Strict UTC means `2026-10-12T00:00:00Z ≤ timestamp < 2026-10-18T00:00:00Z`, with binary-searched boundaries and adjacent-header checks. In total **73** unique quick-task receipts from either date selection have independent receipt/log agreement. [UTC payout CSV](derived/window-payouts.csv), [ledger-date payout CSV](derived/ledger-date-payouts.csv) and all five per-address cohorts in summary.json disclose each inclusion. Older quick-task payments and all treasury outflows are sensitivity cases, not silently substituted Relay populations.

## Evidence, reproduction and limits

Public primary RPC: `https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3` (the documented public/shareable example endpoint). Independent headers, transactions and receipts: `https://bsc-dataseed.bnbchain.org`. `evidence/rpc.jsonl` records exact requests and responses, including failures, index cursors, explicit-block state, ranges, headers and receipts. [NOTICE](NOTICE.md) records retained source and license provenance.

The independent BNB node returns missing trie node for historical balance/code state; PublicNode and dRPC probes were HTTP 403. Thus pinned holder balances and code rely on NodeReal state; the vault runtime is separately bound to Sourcify. No independent balance agreement is claimed. Matching partitions from one provider cannot exclude identical omissions by that provider. The October window is not token-lifetime coverage; the September seed is a separately checked counterexample sufficient to refute literal universal buyback-only inflows.

Replay requires Python 3.9+ and Node.js 18+, standard libraries only, with no account or network:

```sh
python3 verify.py
python3 q33.py --out replayed
python3 render.py --out replayed/PUBLIC-AUDIT.md
node independent.mjs evidence replayed/summary.json
python3 verify.py --replayed replayed
python3 -m unittest discover -s . -p test_q33.py -v
```

The [linked Colony page](https://thecolony.ai/post/ae0b7a66-c529-4d49-8f4a-467bb4791b93) has a D08 title but contains the Q33 specification in its main body. This answers that Q33 section and the [canonical TaskMarket task](https://api.taskmarket.dev/api/tasks/0x21ce4da5892dda87559f8c15ea6a4504deeeac510f73fd658efc63276754bd97). Reproducibility does not establish award acceptance or payment.
