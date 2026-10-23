# Q33 FLAPJAX holder and treasury audit

[PUBLIC-AUDIT.md](PUBLIC-AUDIT.md) contains the reproducible audit. It provides the named finalized snapshot, all top-ten balances and verified runtime roles, treasury balance/share, the literal-statement counterexample and explicit retention cohorts.

At block **128867609**, the full indexed candidate set reconciles to **264 nonzero addresses**, **44,444,444,444 FLAPJAX**, and **zero base-unit supply gap**. Treasury holds **277,115,377.391760699304473698** FLAPJAX, **0.623509599137%**. The requester-ledger-dated Q21–Q32 cohort has **18/19** balances at least equal to cumulative payouts; a strict UTC payment-date interpretation has **17/18**. All broader populations and every row remain explicit.

The literal buyback-only inflow statement is contradicted by an independently checked 10,000,000-token direct seed. In the complete bounded October 1–snapshot log window, twelve inflows are verified buys and no outflow goes directly to either verified V3 pool. Four outflows lack a captured public purpose label. This is not token-lifetime no-sale coverage.

## Cold replay

Python 3.9+ and Node.js 18+; standard libraries only. From this directory:

```sh
python3 verify.py
python3 q33.py --out replayed
python3 render.py --out replayed/PUBLIC-AUDIT.md
node independent.mjs evidence replayed/summary.json
python3 verify.py --replayed replayed
python3 -m unittest discover -s . -p test_q33.py -v
```

`q33.py` re-executes the actual received Q35 validator before calculating Q33. `independent.mjs` discovers candidates and cohorts from the raw messages and requester HTML using a separate BigInt implementation. The final verifier compares every report/table output byte for byte. Missing source requests, missing pages, duplicates, gaps, truncation, wrong chain/decimals, mismatched receipts and inconsistent supply fail rather than becoming zero activity.

The unchanged Q35 package has its own six-command cold replay in [q35-reuse/README.md](q35-reuse/README.md). It proves only its old window. Its 17 delivered files and original checksums remain intact.

## Public source capture

`collect.py` uses only the documented public NodeReal demonstration endpoint and BNB public RPC, explicit fixed snapshot state, a ten-page holder-index bound, bounded retries, and two bounded log extensions around the retained Q35 evidence. `collect_supplement.py` verifies the seed transaction locator independently and receives second-node receipts for both interpretations of the labelled payout window. Existing saved requests are cached; these commands resume this fixed capture, not silently advance the snapshot. They require network, but no account, key, signing capability, paid API, package install or financial operation.

`evidence/rpc.jsonl` contains exact request/response objects and observation timestamps, including failed historical-state reads. `evidence/SOURCES.json` binds static URLs to capture-file hashes and their observed filesystem write times. `derived/holders.csv` contains all holders; `derived/treasury-flows.csv` all bounded-window treasury flows; the payout CSVs expose UTC and ledger-date selection; `derived/retention-relay-ledger.csv` is the main 19-address retention table. Summary JSON preserves exact integer amounts and rational shares.

`verify.py`, FILES.txt and SHA256SUMS define this package. No dependency directory or Python cache belongs to the export. See [NOTICE.md](NOTICE.md) for source and license provenance.

FILES.txt lists this public reproducibility package. Publication does not establish award acceptance or payment.
