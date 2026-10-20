# License and public evidence provenance

The included audit/replay source is provided under the MIT terms in [LICENSE](LICENSE). The original upstream copyright and permission notice is preserved unchanged.

`audit.py`'s integer-only decimal formatting adapts `fmt` from [kaminariouji/flapjax-probe, q21-receipt-audit.mjs at 8555d606e3528cd68880fbde36c9d3e19411c351](https://github.com/kaminariouji/flapjax-probe/blob/8555d606e3528cd68880fbde36c9d3e19411c351/q21-receipt-audit.mjs), copyright 2026 kaminari-research, MIT. The receipt/issuer binding approach was inspected there; its expected transaction list and totals are not inputs to discovery. No external package implementation is otherwise bundled.

The event signature and word layout follow the [official PancakeSwap V3 pool-event interface at 986847948755cba528324d41be19480731c36c2a](https://github.com/pancakeswap/pancake-v3-contracts/blob/986847948755cba528324d41be19480731c36c2a/projects/v3-core/contracts/interfaces/pool/IPancakeV3PoolEvents.sol). Its public URL, revision and original-source SHA-256 are recorded in [evidence/pool-events-source.json](evidence/pool-events-source.json); the Solidity implementation is not redistributed. Saved `web3_sha3` calls confirm the Transfer and PancakeSwap-specific Swap topics.

The journal's `https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3` is NodeReal's [officially documented public and shareable endpoint](https://docs.nodereal.io/reference/getting-started-with-your-api), not a personal credential. The second route is `https://bsc-dataseed.bnbchain.org`. The journal contains only public read-only JSON-RPC requests/responses, including five HTTP 429 responses followed by successful bounded retry. No personal credential, signing key, account record or private operating record is part of this delivery.

Public blockchain quantities and observation timestamps are reproduced as evidence. Their inclusion does not establish ownership of any address. This package makes no claim of investment merit, token fiat value, payment authority, award acceptance or future fulfillment.
