# Q35 FLAPJAX buyback audit

[Read the complete audit](PUBLIC-AUDIT.md) for every transaction, block hash, UTC time, input, token Transfer amount, recipient, formula and statement verdict. [Exact CSV](derived/buys.csv) and [machine-readable results](derived/summary.json) are included.

The saved BSC evidence independently yields **9 treasury buys, 0.09 BNB-equivalent WBNB input and 214,002,792.664923451883644637 FLAPJAX output**. The daily cadence mismatches UTC dates, but matches UTC-5/UTC-4. Every buy output reached treasury; no direct treasury-to-named-pool token transfer appears among 191 treasury outflows. The promised October 23 make-up is a future promise at this October 20 capture.

The primary window is **2026-10-09 00:00:00Z through just before 2026-10-19 00:00:00Z**, inclusive blocks **126536085–128454490**. Padded blocks **126424183–128550459** cover boundary uncertainty. Full-range coverage trusts one public archive provider under two matching partitions; all 22 padded swaps have second-route receipt/transaction/header checks. This is reproducible RPC evidence, not a cryptographic completeness proof or an investment recommendation.

## Cold replay

Download this directory, open a shell in the directory containing this README, and run:

```sh
python3 verify.py
python3 audit.py --evidence evidence --out replayed
node cold-independent.mjs evidence replayed
python3 render.py --evidence evidence --derived replayed --out replayed/PUBLIC-AUDIT.md
python3 verify.py --replayed replayed
python3 -m unittest discover -s . -p test_audit.py -v
```

Requires **Python 3.8+ and Node.js 18+**, using only their standard libraries and built-in modules. No package installation, credentials, wallet or network call is required. `replayed/` is the new output directory. The final verification checks that its report, summary, CSV and independent BigInt output match the delivered bytes. The 11 original negative/control groups must pass.

The raw [RPC journal](evidence/rpc.jsonl) is the only shipped raw encoding: exact requests, successful/failed responses, scopes, headers, transactions and receipts. `evidence.py` reconstructs the former aggregate in memory, including both range partitions, so it need not be duplicated as another raw JSON file. Missing saved requests fail rather than becoming zero activity. `FILES.txt` is the publication allowlist; `SHA256SUMS` identifies every other delivered file. Only the paths in that list belong to this package.

`audit.py` validates the evidence and exact rational arithmetic. `cold-independent.mjs` independently discovers buys from token outflows and reduces the second provider's receipts with BigInt. `render.py` reproduces the report. [License and attribution](NOTICE.md) explain the reused MIT formatting routine, the pinned public event interface and NodeReal's documented public/shareable endpoint. No personal API credential is included.

This answers [Taskmarket TSK-88YN3100](https://api.taskmarket.dev/api/tasks/0x1284d01695bfcd1720cfb319f658a258b82b6768501fc00cb9ab0748bc45fd35) and the linked [Q35 specification](https://thecolony.ai/post/254bb713-2201-4ac4-9920-af56d11cc28e). Technical reproduction does not establish award eligibility, acceptance or payment.
