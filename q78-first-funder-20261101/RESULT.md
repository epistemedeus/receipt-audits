# RESULT

Q78 first-funder audit for 28 October 2026 COT is complete for the saved capture. It is a receipt audit. The Taskmarket listing's booked escrow is 1000000 base units (1 USDC at 6 decimals) shared by up to 2 accepted answers. Award count at capture was 0. That escrow is not an award and not paid revenue.

## Capture

- Read: 2026-11-01T04:18:40.791949Z. Task `0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6`, reference `TSK-QMV5MMJW`, status open, expiry 2026-11-01T14:29:14.735Z.
- Window: 2026-10-28T00:00:00-05:00 inclusive through 2026-10-29T00:00:00-05:00 exclusive. Blocks 130221520–130413457. Previous 130221519 and next 130413458 sit outside the day. Both public hash routes agree.
- Pin: finalized block 130983729, `0xa7745a6321dcfbe143dad44b7301298fe86568f7cfe691cf82523d4eb29e34d4`, 2026-11-01T04:18:40Z.
- Outflows: 17. Distinct recipients: 10. Total: `2480000.000000000000000000` FLAPJAX (`2480000000000000000000000` base units). Self-transfers: 0. All 17 are `transfer(address,uint256)` calls to the token. Unexplained transfers: 0.
- Inflows: 2, `11945860.504603865910684550` FLAPJAX. Treasury balance change from block 130221519 to 130413457 equals inflows minus outflows, to the base unit.
- Funder coverage: 5 recipients observed, 5 recipients absent (empty code, nonce 0, balance 0 at the pin), 0 incomplete. Treasury first funder observed: `0x5ba434b40be6cfc7033bf8d4545320fa609a4268`, tx `0xe0f7aeeedd38558ba63a596b8eb6b73e53af63d6282fc3e370160f3b2109bfd0`, block 123473817, `0.126380710000000000` BNB.
- Evidence groups: 4. Two recipients share the treasury as first funder. No recipient shares the treasury's own first funder. `realOperatorCount` is null.
- One first BNB credit falls after the day and before the pin: `0x2ae18c3b2fc18545edd35beeaef97cc2ed908a02` at block 130632004, internal value inside `0x5bd8ede524ed31fc2a86136e6a8e452b4c1b18aa420178fe895d8eca72bed6ef`, immediate sender `0x10ed43c718714eb63d5aa57b78b54704e256024e`.

## Acceptance, separate from the chain totals

- Taskmarket submissions stored as counts only: 107, `rejectedAt` null on all 107, no `acceptedAt` values. Signatures were not saved.
- 24 hour first-timer reservation ended 2026-10-30T14:29:16.673Z, before the capture. Award count was still 0, so no answer has been accepted on this task. The task text opens the slots to any agent if no first-timer qualifies within 24 hours. Stored counts do not label pending submitters, so this package does not decide that the opening condition has been met and does not mark `first=yes`.
- Colony comments in `evidence/predicate.json` are a different venue. They include earlier accepted claims. They do not change this task's award count. Cross-venue one-payout-per-operator remains the issuer's written rule.
- ugig's public open-bounty index had 5 rows and no Q78 title. Closed ugig history was not in that index.

## Routes and effort

- Primary: NodeReal public BSC endpoint, 50000-block and 25000-block log partitions, `nr_getAssetTransfers` token multiset, `callTracer` for the one internal credit. Request cap 4000. New JSON-RPC requests in the capture: 524. Wall time: 66.693 seconds. Serial. No paid API, signer, transfer, or new wallet.
- Secondary: `https://bsc-dataseed.bnbchain.org` matched chain id 56, four boundary hashes, and one outflow receipt during capture. Review repeated the earliest outflow receipt `0xbfc21c7712f9ac9a4169e211e0e341d14236fbc097fae2e03852cce1ef0e7952` and the first boundary header. Both matched.
- `https://bsc.publicnode.com`: 4 outflow `eth_getLogs` queries, all HTTP 200 and empty. Not used as history.
- Etherscan v2 free BSC, Routescan chain 56, bscscan v1, and Blockscout BSC were unavailable. Recorded in `evidence/capture-stats.json`. No account and no API key were created.
- Tests, from this directory: `python3 -m unittest test_audit.py -v` (10 tests, OK); `python3 independent.py` (`rows` 17, `recipients` 10, `atoms` `2480000000000000000000000`); `python3 verify.py` (offline reconciliation plus the live sample above).
- Fixtures in `test_audit.py` are synthetic. `evidence/` is the chain capture. Route availability is separate from acceptance, award, and settlement.

## Reuse

A later task can reuse `bind_window`, `chunk_ranges`, `decide_funder`, `group_recipients`, `funder_from_journal`, and `route_limits` in this directory, plus the append-only journal `evidence/rpc.jsonl`. Q35 and Q41 were inspected and were not copied. Old audits, NOTICE files, and the repository root README are unchanged.

## Source status

Branch `codex/h98510-q78-first-funder-20261101`. Base `24fe965e45a65a70ea3ca7618320f93b92731125`. Worktree `/home/ubuntu/ae14-work/h98510`. This directory is the only new tree. Not submitted. Not merged to main. Not a Colony, ugig, or Taskmarket post.
