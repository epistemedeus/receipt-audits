# RESULT

Q78 receipt audit for 28 October 2026 COT records the saved capture. Lifetime BNB first-funder and lifetime absence are not proved. This scoped correction is not a completed qualifying paid task. The Taskmarket listing's booked escrow is 1000000 base units (1 USDC at 6 decimals) shared by up to 2 accepted answers. Award count at capture was 0. That escrow is not an award and not paid revenue.

## Capture

- Read: 2026-11-01T04:18:40.791949Z. Task `0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6`, reference `TSK-QMV5MMJW`, status open, expiry 2026-11-01T14:29:14.735Z.
- Window: 2026-10-28T00:00:00-05:00 inclusive through 2026-10-29T00:00:00-05:00 exclusive. Blocks 130221520–130413457. Previous 130221519 and next 130413458 sit outside the day. Both public hash routes agree.
- Pin: finalized block 130983729, `0xa7745a6321dcfbe143dad44b7301298fe86568f7cfe691cf82523d4eb29e34d4`, 2026-11-01T04:18:40Z.
- Outflows: 17. Distinct recipients: 10. Total: `2480000.000000000000000000` FLAPJAX (`2480000000000000000000000` base units). Self-transfers: 0. All 17 are `transfer(address,uint256)` calls to the token. Unexplained transfers: 0.
- Inflows: 2, `11945860.504603865910684550` FLAPJAX. Treasury balance change from block 130221519 to 130413457 equals inflows minus outflows, to the base unit.
- BNB lifetime first and lifetime absence: not proved. Empty pin code, balance, and nonce do not prove absence. The same emptiness at every sampled block end still would not. A contract can be created, funded, and SELFDESTRUCT in one transaction. EIP-6780 specification item 2 preserves that deletion, so code, nonce, and balance can be empty at every block boundary. This is a permitted counterexample, not a finding that any captured recipient used it, and not a BSC fork-version claim. Saved call traces do not cover every successful transaction in the crossing blocks. External-index equality is not internal coverage. `verify.py` repeats two readonly public receipt and header checks. Those checks do not prove lifetime history.
- Candidate receipts retained from the saved crossing blocks, with `lifetimeFirstProved` false: five recipients and the treasury. The treasury candidate sender is `0x5ba434b40be6cfc7033bf8d4545320fa609a4268`, tx `0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0`, block 123473817, `0.126380710000000000` BNB. Five other recipients are candidate-missing: empty pin and no saved candidate. All ten recipients are lifetime-unknown, including the five with a candidate. The raw capture file still says `absent` or `observed`; derived coverage is `lifetime-unknown`. Real operator count is unknown.
- Evidence groups: 4 candidate groups. Two recipients share the treasury as a candidate sender. No recipient shares the treasury's own candidate sender. `lifetimeFirstProved` is false on every group. `realOperatorCount` is null. Legacy key `treasuryFirstFunder` is that candidate sender.
- One candidate BNB credit falls after the day and before the pin: `0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02` at block 130632004, internal value inside `0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef`, immediate sender `0x10ed43c718714eb63d5aa57b78b54704e256024e`. That credit is not a proved lifetime first funder.

## Acceptance, separate from the chain totals

- Taskmarket submissions stored as counts only: 107, `rejectedAt` null on all 107, no `acceptedAt` values. Signatures were not saved.
- Taskmarket award count 0 is this task only. It does not prove an uncovered eligible receipt.
- Colony comment `5e50258f-95c4-42ea-92db-e3ce6de5d5d6` accepts treasury funding `0xe0f7aeee`. Comment `d9490ee9-e138-4c86-8f35-69873a37248f` says the 17 transfers and 4 first-funder transactions in that claim were already covered. Comment `44d6b171-0703-4945-852c-c8dc1a313839` accepts post-cutoff `0x5bd8ede5`. No saved receipt is provably outside that coverage.
- Qualifying increment established: no. Do not submit.
- ugig's public open-bounty index had 5 rows and no Q78 title. Closed ugig history was not in that index.

## Routes and effort

- Primary: NodeReal public BSC endpoint, 50000-block and 25000-block log partitions, `nr_getAssetTransfers` token multiset, `callTracer` for the one internal credit. Request cap 4000. New JSON-RPC requests in the capture: 524. Wall time: 66.693 seconds. Serial. No paid API, signer, transfer, or new wallet.
- Secondary: `https://bsc-dataseed.bnbchain.org` matched chain id 56, four boundary hashes, and one outflow receipt during capture. Review repeated the earliest outflow receipt `0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952` and the first boundary header. Both matched.
- `https://bsc.publicnode.com`: 4 outflow `eth_getLogs` queries, all HTTP 200 and empty. Not used as history.
- Etherscan v2 free BSC, Routescan chain 56, bscscan v1, and Blockscout BSC were unavailable. Recorded in `evidence/capture-stats.json`. No account and no API key were created.
- Tests, from this directory: `python3 -m unittest test_audit.py -v` (18 tests, OK); `python3 independent.py` (`rows` 17, `recipients` 10, `atoms` `2480000000000000000000000`); `python3 verify.py` (exit 0; offline reconciliation plus readonly receipt `0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952` and boundary block 130221520).
- Fixtures in `test_audit.py` are synthetic. `evidence/` is the chain capture. Route availability is separate from acceptance, award, and settlement.

## Reuse

A later task can reuse `bind_window`, `chunk_ranges`, `assemble_block_credits`, `lifetime_premise_justified`, `coverage_label`, `group_recipients`, `funder_from_journal`, `qualifying_increment`, and `route_limits` in this directory, plus the append-only journal `evidence/rpc.jsonl`. `decide_funder` remains a block-local helper. `lifetime_premise_justified` returns false for every end-of-block code map. Q35 and Q41 were inspected and were not copied. Old audits, NOTICE files, and the repository root README are unchanged.

## Source status

Branch `codex/h98510-q78-first-funder-20261101`. Worktree `/home/ubuntu/ae14-work/h98510`. Raw `evidence/` is the original capture. Derived files were regenerated offline. Not submitted. Not merged to main. No qualifying increment is established.
