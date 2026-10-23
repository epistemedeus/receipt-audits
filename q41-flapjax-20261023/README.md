# Q41 public-evidence replay package

Read [PUBLIC-AUDIT.md](PUBLIC-AUDIT.md) for the complete October 9–21 COT audit, every buy and rule verdict. Exact prices, hashes, atomic totals, calendar and native-value accounting are in [derived/summary.json](derived/summary.json) and CSV files. Existing Q35/Q33 bytes remain unchanged.

Python 3.9+ on Linux and Node.js 18+, standard libraries only. From this directory:

```sh
python3 cold.py --out replayed
```

The receiver runs serially. It verifies PUBLIC-FILES.txt/SHA256SUMS, cold-replays Q35 and Q33 including their original reports and independent decoders, recomputes Q41, independently compares every Q41 row with BigInt, runs 11 retained Q35 + 21 retained Q33 + 22 new Q41 failure/recovery tests, and byte-compares the new report and six derived files. It writes bounded logs and timing/RSS evidence to `replayed/verification.json`. No dependency install, network, wallet or model child is used. Python children have a 512 MiB virtual-address cap; Node children have a 128 MiB V8 heap. The finite receiver samples child RSS, stops an owned child above 768 MiB, and records kernel child high-water RSS, serially. This is comfortably inside the 2 GiB assignment budget.

Minimal Q41-only cold commands:

```sh
python3 verify.py
python3 q41.py --out replayed
python3 render.py --summary replayed/summary.json --out replayed/PUBLIC-AUDIT.md
node --max-old-space-size=128 independent.mjs replayed/summary.json
python3 -m unittest discover -s . -p test_q41.py -v
```

`collect.py` is a fixed-window public read collector, not a general indexer. It reuses successful immutable queries from both inherited journals, pins one finalized observation, bounds each range and response size, caps 900 new requests per invocation, and retries transport/rate failures at most three times with backoff. It never mutates a chain. `collect_supplement.py` obtains native-flow traces and one independent historical-state availability probe. The current saved new journal has 317 requests including three explicit historical-state failures. Original acquisition ran before final packaging; the exact original records remain authoritative. Re-running a collector can add observations and requires new hashes/review, so it is not part of cold replay.

Additional block-before headers and the second-route slot0 availability probe are saved in the same journal. Their exact request objects are inspectable, and the replay requires every prior header. They used the same collector's read/cache path. No entire-chain or unrelated-account scan was made. Fresh requester/official documentation captures and hashes are in evidence/SOURCES.json; raw journals distinguish inherited October 20/21 observations from the October 23 extension.

The public reproduction set is exactly PUBLIC-FILES.txt. RESULT.md, WORKER-RESULT.json, input binding, admission notes, execution receipts, failed timing-wrapper diagnostic and repository telemetry are operator records excluded from that set. A later publisher can copy only that allowlist. Source-ready does not mean published, accepted or paid. See [NOTICE.md](NOTICE.md) and [INHERITED.json](INHERITED.json).
