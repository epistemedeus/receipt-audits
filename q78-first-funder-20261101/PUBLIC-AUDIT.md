# Q78 treasury outflows for 28 October 2026 COT

This is a chain receipt audit of FLAPJAX transfers out of one treasury address during one Central offset day. It is a receipt record. It is not a token offer, a price, or a request to buy. The booked escrow below is the listing's locked amount. It is not an award and it is not paid revenue. Nothing in this repository was submitted to the requester.

Task [`0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6`](https://api.taskmarket.dev/api/tasks/0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6) (`TSK-QMV5MMJW`), specification [Colony post cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb](https://thecolony.ai/post/cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb). Token `0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df` (18 decimals). Treasury `0x7c34e9e21ee28a49ff0b84b61774119e6633359f`. BSC chain id 56. The USDC escrow is on Base chain id 8453.

The task says 10-28 COT (UTC-5). The task was created 2026-10-29, so the day is 28 October 2026. Inclusive start `2026-10-28T00:00:00-05:00` (1793163600). Exclusive end `2026-10-29T00:00:00-05:00` (1793250000).

## Acceptance at capture

Taskmarket read at `2026-11-01T04:18:40.791949+00:00`. Status `open`. Award count `0`. Submission count `107`. Stored submissions with `rejectedAt` null: `107`. Stored `acceptedAt` values: `0`. Acceptance fields present: `rejectedAt`. Reward field `1000000` base units. Escrow booked `1000000` base units. `escrowIsAward` is `false`. Expiry `2026-11-01T14:29:14.735Z`.

The written 24 hour first-timer reservation ends `2026-10-30T14:29:16.673000+00:00`. This capture is after that instant (`capturedAfterFirstTimerWindow` `true`). Award count `0` means no answer has been accepted on this task. The task text says that if no first-timer qualifies within 24 hours, the slots open to any agent. The stored submission counts do not label which workers are first-timers, so this package does not decide that the opening condition has been met, and it does not mark any submitter `first=yes`.

Colony is a separate venue. `12` issuer comments that mention Q78, B583, or B584 are stored in [predicate.json](evidence/predicate.json). Those comments record Colony acceptances and declines, including a treasury first-funding transaction at block 123473817 and transaction `0x5bd8ede5` for recipient `0x2ae18c3b`. The same two transactions were read again from BSC below. The comments do not change this task's award count. The issuer's written rule is one payout per operator across Colony, ugig, and Taskmarket. This audit does not decide whether any later submitter was paid before.

The public ugig bounty index at the same read listed `5` open rows and `q78Listed` `false`. That index has no closed-bounty history. Taskmarket awardCount is this task's accepted-claim count. Colony decisions are a different venue. A public ugig index that omits Q78 does not prove ugig never accepted it.

## Day boundaries

Blocks are the first and last whose timestamps fall in that half-open interval. NodeReal and `bsc-dataseed.bnbchain.org` returned the same four hashes.

| Edge | Block | Timestamp | COT | Hash |
| --- | --- | --- | --- | --- |
| Previous | 130221519 | 1793163599 | 2026-10-27T23:59:59-05:00 | 0x0de6f3ae9b9e35ec37a2fd4ea1fe52de1df82354c827781c7c493fc9097d6e7a |
| First | 130221520 | 1793163600 | 2026-10-28T00:00:00-05:00 | 0x8c45336ba8635660de6d723d38cfbc6ed3e8a711e649c8cae54da6df48854b93 |
| Last | 130413457 | 1793249999 | 2026-10-28T23:59:59-05:00 | 0x2db8cc93fb90059b145d66a39fcc0794bd25efafc86317387310082abae04b46 |
| Next | 130413458 | 1793250000 | 2026-10-29T00:00:00-05:00 | 0x2f081b0f45363e20bf362ff342cc84e2d626c941b8fd7dcaebd1e622af781343 |

Pin used for funder end-state: block `130983729`, hash `0xa7745a6321dcfbe143dad44b7301298fe86568f7cfe691cf82523d4eb29e34d4`, unix `1793506720`, COT `2026-10-31T23:18:40-05:00`. Absence means no BNB balance and nonce 0 at this pin. A later credit is outside this capture.

## Outflows

External transfers: **17**. Distinct recipients: **10**. Total sent: **2480000.000000000000000000 FLAPJAX** (`2480000000000000000000000` base units). Self-transfers: 0.

Treasury token balance moved from 816196536.447382439762897131 at block 130221519 to 825662396.951986305673581681 at block 130413457. Inflow logs in the same day: 2, 11945860.504603865910684550 FLAPJAX (`11945860504603865910684550` base units). treasury balance change equals inflow logs minus outflow logs, to the base unit.

| COT | Block | Recipient | Amount | Mechanism | Transaction |
| --- | --- | --- | --- | --- | --- |
| 2026-10-28T08:29:31-05:00 | 130289426 | [`0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c`](https://bscscan.com/address/0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c) | 300000.000000000000000000 | normal-transfer-call | [`0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952`](https://bscscan.com/tx/0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952) |
| 2026-10-28T08:29:35-05:00 | 130289434 | [`0xfb200657f7266157a45dfcc6c09690726daa24e6`](https://bscscan.com/address/0xfb200657f7266157a45dfcc6c09690726daa24e6) | 25000.000000000000000000 | normal-transfer-call | [`0x76f4abaa6a14005726257d1412d9a9842af6c09a5bb6395c2604f844f9bff77d`](https://bscscan.com/tx/0x76f4abaa6a14005726257d1412d9a9842af6c09a5bb6395c2604f844f9bff77d) |
| 2026-10-28T08:29:39-05:00 | 130289443 | [`0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c`](https://bscscan.com/address/0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c) | 25000.000000000000000000 | normal-transfer-call | [`0xdd2feb71c1dda3945b233ab7c924b1d1e6d52b7d3dcd4cc6354e3248df9b3da4`](https://bscscan.com/tx/0xdd2feb71c1dda3945b233ab7c924b1d1e6d52b7d3dcd4cc6354e3248df9b3da4) |
| 2026-10-28T08:29:43-05:00 | 130289453 | [`0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62`](https://bscscan.com/address/0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62) | 25000.000000000000000000 | normal-transfer-call | [`0x8c6305282436e1867eeac42b859ff947dad7f0db447af34fb8ff7185d88bb0d9`](https://bscscan.com/tx/0x8c6305282436e1867eeac42b859ff947dad7f0db447af34fb8ff7185d88bb0d9) |
| 2026-10-28T08:29:48-05:00 | 130289462 | [`0x3d98800c64c345950e1eaaa076d88c12d1bf5f37`](https://bscscan.com/address/0x3d98800c64c345950e1eaaa076d88c12d1bf5f37) | 25000.000000000000000000 | normal-transfer-call | [`0xe468d224801e50cf936296a8f79b6bc9dc13d14bede24bd9945312e597b2074e`](https://bscscan.com/tx/0xe468d224801e50cf936296a8f79b6bc9dc13d14bede24bd9945312e597b2074e) |
| 2026-10-28T08:29:52-05:00 | 130289472 | [`0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5`](https://bscscan.com/address/0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5) | 25000.000000000000000000 | normal-transfer-call | [`0x7e8f90f49597397529cc81cea8723debc2dd08da35ba78999fcc2840dc4cad0c`](https://bscscan.com/tx/0x7e8f90f49597397529cc81cea8723debc2dd08da35ba78999fcc2840dc4cad0c) |
| 2026-10-28T08:29:56-05:00 | 130289480 | [`0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62`](https://bscscan.com/address/0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62) | 300000.000000000000000000 | normal-transfer-call | [`0x0c7d758ba9955a141839d137c2830b41860eb00ccdb0bb1a10ef33829e9b1bb6`](https://bscscan.com/tx/0x0c7d758ba9955a141839d137c2830b41860eb00ccdb0bb1a10ef33829e9b1bb6) |
| 2026-10-28T08:38:11-05:00 | 130290580 | [`0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c`](https://bscscan.com/address/0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c) | 300000.000000000000000000 | normal-transfer-call | [`0x825b5c67d1cf033e9f756dcd5c69f683d77f2478ee0ee5d8f6b04d42df05c8ae`](https://bscscan.com/tx/0x825b5c67d1cf033e9f756dcd5c69f683d77f2478ee0ee5d8f6b04d42df05c8ae) |
| 2026-10-28T08:49:02-05:00 | 130292025 | [`0x8c062dc5d775b7d5efc168f75a875f392f53dcdf`](https://bscscan.com/address/0x8c062dc5d775b7d5efc168f75a875f392f53dcdf) | 10000.000000000000000000 | normal-transfer-call | [`0x388a55851ce63aaf984e6671f305155b165c47225dc5d7dab0e47d8ce2763372`](https://bscscan.com/tx/0x388a55851ce63aaf984e6671f305155b165c47225dc5d7dab0e47d8ce2763372) |
| 2026-10-28T10:32:43-05:00 | 130305844 | [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8) | 25000.000000000000000000 | normal-transfer-call | [`0x69fea445443ca8d27e43d3c11f53aaa34a2edc7e997e84668409d86eb021abb5`](https://bscscan.com/tx/0x69fea445443ca8d27e43d3c11f53aaa34a2edc7e997e84668409d86eb021abb5) |
| 2026-10-28T10:32:47-05:00 | 130305853 | [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8) | 300000.000000000000000000 | normal-transfer-call | [`0x3f4d252efc70064dd841e062847aad926bebca630137787832c77b10fd246de5`](https://bscscan.com/tx/0x3f4d252efc70064dd841e062847aad926bebca630137787832c77b10fd246de5) |
| 2026-10-28T10:32:52-05:00 | 130305864 | [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8) | 120000.000000000000000000 | normal-transfer-call | [`0x4f591ad86bb514247d59dbc91cf5793b0a63f22b9e73929aa4bb05946cc3f1f9`](https://bscscan.com/tx/0x4f591ad86bb514247d59dbc91cf5793b0a63f22b9e73929aa4bb05946cc3f1f9) |
| 2026-10-28T13:26:40-05:00 | 130329034 | [`0xca58696564492ef9c3229c89072365b253bda246`](https://bscscan.com/address/0xca58696564492ef9c3229c89072365b253bda246) | 150000.000000000000000000 | normal-transfer-call | [`0x00b7423c3baf0986ceda24d5286733747a5aed181106a8cf166f6319eacd94bd`](https://bscscan.com/tx/0x00b7423c3baf0986ceda24d5286733747a5aed181106a8cf166f6319eacd94bd) |
| 2026-10-28T19:18:07-05:00 | 130375885 | [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | 250000.000000000000000000 | normal-transfer-call | [`0x41f5bc43f9d147a414d86778cfee19c21b62da0d8fed1f9e22cd04f36b283c8e`](https://bscscan.com/tx/0x41f5bc43f9d147a414d86778cfee19c21b62da0d8fed1f9e22cd04f36b283c8e) |
| 2026-10-28T19:18:10-05:00 | 130375893 | [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | 50000.000000000000000000 | normal-transfer-call | [`0x36485b4966c1dbcd0198d840a865c4e97e2fec32c5f1f74cf55f5030d88bae37`](https://bscscan.com/tx/0x36485b4966c1dbcd0198d840a865c4e97e2fec32c5f1f74cf55f5030d88bae37) |
| 2026-10-28T19:18:15-05:00 | 130375904 | [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | 250000.000000000000000000 | normal-transfer-call | [`0x9af6e7e8ba53540a930d3a7c532af1637c6ccc6324067ab402693b24aff992b0`](https://bscscan.com/tx/0x9af6e7e8ba53540a930d3a7c532af1637c6ccc6324067ab402693b24aff992b0) |
| 2026-10-28T23:26:50-05:00 | 130409040 | [`0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02`](https://bscscan.com/address/0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02) | 300000.000000000000000000 | normal-transfer-call | [`0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5`](https://bscscan.com/tx/0xcdbada2d2795f663a10fdb373337139f93b11256a6dfe102368c4538149412a5) |

A normal transfer call is `transfer(address,uint256)` sent to the token. A contract-mediated row is still a Transfer log from the treasury; the outer transaction called some other account. Both count. Amounts are the log amounts, in 18 decimal places.

### Same-day inflows used for the balance check

| COT | Block | From | Amount | Mechanism | Transaction |
| --- | --- | --- | --- | --- | --- |
| 2026-10-28T13:41:46-05:00 | 130331045 | [`0xca93ec685b8623688e6b236f9068034b298c2150`](https://bscscan.com/address/0xca93ec685b8623688e6b236f9068034b298c2150) | 11645860.504603865910684550 | contract-mediated-transfer-event | [`0xa6f25856a9ce66cdf3ba4dba21bb2c19423610076db7ed7dd827d2029d1416fa`](https://bscscan.com/tx/0xa6f25856a9ce66cdf3ba4dba21bb2c19423610076db7ed7dd827d2029d1416fa) |
| 2026-10-28T15:41:37-05:00 | 130347025 | [`0xca58696564492ef9c3229c89072365b253bda246`](https://bscscan.com/address/0xca58696564492ef9c3229c89072365b253bda246) | 300000.000000000000000000 | normal-transfer-call | [`0x6ebd86862873513c0f9e69421bee5fad25721e70ac999b90f040a0d5c10d7dc8`](https://bscscan.com/tx/0x6ebd86862873513c0f9e69421bee5fad25721e70ac999b90f040a0d5c10d7dc8) |

## First BNB funder

For each recipient, and for the treasury, the search uses end-of-block balance and nonce through the pin. Empty code, nonce 0, and balance 0 at the pin is recorded as absent: an ordinary account cannot spend BNB without increasing its nonce. Nonempty code is recorded as incomplete, because a contract can receive and forward inside one transaction and end at zero. The first funder is the immediate account that sent the BNB value. On an internal transfer, that account can differ from the transaction signer.

A shared first funder is one evidence group. The group does not prove that one operator controls the wallets. Recipients with absent or incomplete history stay outside the groups.

| Role | Address | Coverage | First funder | Category | BNB | Funder block | Funder transaction |
| --- | --- | --- | --- | --- | --- | --- | --- |
| recipient | [`0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02`](https://bscscan.com/address/0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02) | observed | [`0x10ed43c718714eb63d5aa57b78b54704e256024e`](https://bscscan.com/address/0x10ed43c718714eb63d5aa57b78b54704e256024e) | internal | 0.000006257934517396 | 130632004 | [`0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef`](https://bscscan.com/tx/0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef) |
| recipient | [`0x3d98800c64c345950e1eaaa076d88c12d1bf5f37`](https://bscscan.com/address/0x3d98800c64c345950e1eaaa076d88c12d1bf5f37) | absent |  |  |  |  |  |
| recipient | [`0x8c062dc5d775b7d5efc168f75a875f392f53dcdf`](https://bscscan.com/address/0x8c062dc5d775b7d5efc168f75a875f392f53dcdf) | observed | [`0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f`](https://bscscan.com/address/0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f) | external | 0.000066161600000000 | 124103796 | [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) |
| recipient | [`0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c`](https://bscscan.com/address/0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c) | absent |  |  |  |  |  |
| recipient | [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | observed | [`0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589`](https://bscscan.com/address/0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589) | external | 0.000164397936681007 | 128955356 | [`0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840`](https://bscscan.com/tx/0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840) |
| recipient | [`0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62`](https://bscscan.com/address/0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62) | absent |  |  |  |  |  |
| recipient | [`0xca58696564492ef9c3229c89072365b253bda246`](https://bscscan.com/address/0xca58696564492ef9c3229c89072365b253bda246) | observed | [`0x7c34e9e21ee28a49ff0b84b61774119e6633359f`](https://bscscan.com/address/0x7c34e9e21ee28a49ff0b84b61774119e6633359f) | external | 0.000500000000000000 | 130097514 | [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) |
| recipient | [`0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5`](https://bscscan.com/address/0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5) | absent |  |  |  |  |  |
| recipient | [`0xfb200657f7266157a45dfcc6c09690726daa24e6`](https://bscscan.com/address/0xfb200657f7266157a45dfcc6c09690726daa24e6) | observed | [`0x7c34e9e21ee28a49ff0b84b61774119e6633359f`](https://bscscan.com/address/0x7c34e9e21ee28a49ff0b84b61774119e6633359f) | external | 0.000500000000000000 | 126835408 | [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) |
| recipient | [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8) | absent |  |  |  |  |  |
| treasury | [`0x7c34e9e21ee28a49ff0b84b61774119e6633359f`](https://bscscan.com/address/0x7c34e9e21ee28a49ff0b84b61774119e6633359f) | observed | [`0x5ba434b40be6cfc7033bf8d4545320fa609a4268`](https://bscscan.com/address/0x5ba434b40be6cfc7033bf8d4545320fa609a4268) | external | 0.126380710000000000 | 123473817 | [`0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0`](https://bscscan.com/tx/0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0) |

Evidence-defined recipient groups: **4**. Unfunded recipients: 5. Incomplete funder histories: 0. Real operator count: unknown (`realOperatorCount` is null). The task asks how many distinct operators the groups imply. These observations do not supply that number.

The treasury's own first funder is `0x5ba434b40be6cfc7033bf8d4545320fa609a4268`. `sharesTreasuryFirstFunder` is true only when a recipient group has that same funder. `funderIsTreasury` is true when the treasury address itself is the recipient's first funder.

A shared first BNB funder is an evidence group. It does not prove common operator control. Unfunded and incomplete recipients are not counted as proved operators.

First BNB credit after the last block of 10-28 COT, and before the pin: [`0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02`](https://bscscan.com/address/0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02) at block 130632004.

| Funder | Recipients | Linking transactions | Funder is treasury | Same funder as treasury |
| --- | --- | --- | --- | --- |
| [`0x10ed43c718714eb63d5aa57b78b54704e256024e`](https://bscscan.com/address/0x10ed43c718714eb63d5aa57b78b54704e256024e) | [`0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02`](https://bscscan.com/address/0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02) | [`0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef`](https://bscscan.com/tx/0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef) | False | False |
| [`0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f`](https://bscscan.com/address/0x67f5d43cbd8129bf41aae37a609aac44bd55dd1f) | [`0x8c062dc5d775b7d5efc168f75a875f392f53dcdf`](https://bscscan.com/address/0x8c062dc5d775b7d5efc168f75a875f392f53dcdf) | [`0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8`](https://bscscan.com/tx/0xb5a5215482c7cade369d789258eb4da375a32d62aa0392d669e56256d6d36ed8) | False | False |
| [`0x7c34e9e21ee28a49ff0b84b61774119e6633359f`](https://bscscan.com/address/0x7c34e9e21ee28a49ff0b84b61774119e6633359f) | [`0xca58696564492ef9c3229c89072365b253bda246`](https://bscscan.com/address/0xca58696564492ef9c3229c89072365b253bda246) [`0xfb200657f7266157a45dfcc6c09690726daa24e6`](https://bscscan.com/address/0xfb200657f7266157a45dfcc6c09690726daa24e6) | [`0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456`](https://bscscan.com/tx/0x87443eff758296585f6d6eb7b68800ea6c73f143239e60541a6ef5b1f072d456) [`0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7`](https://bscscan.com/tx/0xa3d7042983f4f2352b9b8f324414688db10887e2b2b2a125deca9a8bec6624e7) | True | False |
| [`0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589`](https://bscscan.com/address/0xca7ded7e4f4ba8ab3b10009236ae6d1b95094589) | [`0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9`](https://bscscan.com/address/0xa21fc88bd8c17cae306089d7b00a1f5cd5ad3ee9) | [`0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840`](https://bscscan.com/tx/0x322f5447e749887d2ea22c54536959d2a9f06890005c0ac2306d368e265c5840) | False | False |

No observed first BNB funder, empty code through the pin: [`0x3d98800c64c345950e1eaaa076d88c12d1bf5f37`](https://bscscan.com/address/0x3d98800c64c345950e1eaaa076d88c12d1bf5f37), [`0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c`](https://bscscan.com/address/0x97cd18b8bbb629b17675d868259ea84c0a2a5a9c), [`0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62`](https://bscscan.com/address/0xabc2c3daffa4c1963299da225c25f2aa7d4ddf62), [`0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5`](https://bscscan.com/address/0xdf4ff9d2f45f99f11a90b16f277d4b7edddb72a5), [`0xfdf05af8ddce3621f01713e01721d6e9ad702ea8`](https://bscscan.com/address/0xfdf05af8ddce3621f01713e01721d6e9ad702ea8).

## Unexplained transfers

None.

An explained token transfer can still have an unknown operator. An absent BNB row is a finished end-state read. An incomplete row would be an unfinished scan and is listed separately above.

## Coverage and limits

Primary route: `https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3`. `eth_getLogs` was read in two full partitions, 50000-block and 25000-block steps, for treasury sends and treasury receipts. A page of 1000 logs is rejected as a possible cap. The token-transfer index `nr_getAssetTransfers` (category 20, 90000-block steps, 100000-block provider cap) matches the outflow multiset, including any self-transfer.

Normal BNB transfers are top-level transactions in the first activity block with `to` equal to the address and positive value, status 1. Internal BNB transfers are used only when that index's external set matches those top-level transfers and a `callTracer` trace confirms the credit. Category `external` in the funder table is a normal transfer. Category `internal` is a value call inside a transaction. If the earliest normal transfer is not at transaction index 0 and the internal index is incomplete, the row stays incomplete.

The treasury balance at block 1 is 0, so the balance method reached archive state. The funder search stops at the pin above.

Secondary route `https://bsc-dataseed.bnbchain.org` supplied chain id, the four boundary headers, and one outflow receipt. It is a hash check, not the log index.

`https://bsc.publicnode.com` answered `4` outflow `eth_getLogs` queries: `4` empty, `0` nonempty, `0` errors. `publicnodeUsedAsHistory` is `false`. Empty responses are a missing index on that route.

Etherscan API v2 refused free BSC coverage. Routescan returned chain-not-supported. The old bscscan v1 host returned an HTML migration page. Blockscout's BSC host returned HTTP 404. Each failed route is recorded in [capture-stats.json](evidence/capture-stats.json) and [predicate.json](evidence/predicate.json).

Replay, from this directory, with no installs:

```sh
python3 audit.py
python3 independent.py
python3 render.py
python3 -m unittest test_audit.py -v
python3 verify.py
```

`audit.py`, `independent.py`, `render.py`, and `test_audit.py` stay offline. `test_audit.py` uses synthetic rows and does not reread this capture. `verify.py` repeats the offline checks and reads one saved outflow receipt plus the first boundary header from `bsc-dataseed.bnbchain.org`. `collect.py` is the only writer of `evidence/`. Running it again adds a new capture and needs a new review.
