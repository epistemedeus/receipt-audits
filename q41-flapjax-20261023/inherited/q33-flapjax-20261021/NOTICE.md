# Source reuse and public evidence

`q35-reuse/` is copied byte for byte from the public `epistemedeus/receipt-audits` commit `f6f99bd5f9b810fc447e4907c5bfcb88ef9549b5`, directory `q35-flapjax-20261020/`. Its MIT LICENSE, attribution, checksums and old-window qualification remain intact. Q33 imports and executes its decoder, integer formatter, receipt canonicalizer, dual-partition coverage validator and cold evidence loader. Q33 does not promote its old observations to a new snapshot.

`collect.py` adapts the bounded, cached read-only capture approach from `epistemedeus/pilot@0dd4ac211c7b406a7149c74ff4d55a8411da032d`, `overview/research/phase-20261020/outside-chain-audit/collect.py`. No new chain SDK or external dependency is introduced.

The NodeReal endpoint in this package is the public/shareable demonstration endpoint documented at https://docs.nodereal.io/reference/getting-started-with-your-api and retained by the received Q35 source. It is not an account credential. All calls are public reads. No new provider account or paid API is used.

New public holder-index interface reference: https://docs.nodereal.io/reference/nr_gettokenholders. Pagination discovers candidates only; saved on-chain balanceOf calls at the snapshot produce all reported balances. The index itself provides no historical block guarantee.

Captured requester text is evidence of the request and payment labels, not an independent guarantee of award, payout purpose, or future action. Peer audit figures are not inputs to this calculation.

`evidence/sourcify-vault.json` is the minimal public Sourcify response containing runtime bytecode and compilation metadata, used to bind `Vault` identity to the pinned on-chain bytes. Solidity implementation source is not bundled or adopted. The upstream `src/Vault.sol` inspected through Sourcify identifies PancakeSwap copyright and GPL-2.0-or-later; related interfaces/libraries have their own SPDX notices. This package does not relicense that implementation or call it an MIT audit component.
