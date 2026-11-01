# Q78 first-funder receipt audit, 28 October 2026 COT

Public receipt audit for Taskmarket task `0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6` (`TSK-QMV5MMJW`). Read [PUBLIC-AUDIT.md](PUBLIC-AUDIT.md). Exact rows are in [derived/summary.json](derived/summary.json), the CSV files, and [derived/rows.jsonl](derived/rows.jsonl).

The day is 10-28 COT (UTC-5), 2026, blocks 130221520 through 130413457. The audit lists every FLAPJAX outflow from treasury `0x7c34e9e21ee28a49ff0b84b61774119e6633359f`, each recipient's first BNB funder through finalized block 130983729, and the evidence groups. A shared funder is a group. It does not prove one operator. Five recipients have no BNB credit through that pin. That absence is a finished end-state read.

Python 3.9+, standard library only. From this directory:

```sh
python3 audit.py
python3 independent.py
python3 render.py
python3 -m unittest test_audit.py -v
python3 verify.py
```

The first four commands stay offline. `verify.py` repeats them and checks one outflow receipt plus the first boundary header on `https://bsc-dataseed.bnbchain.org`. `test_audit.py` uses synthetic rows. It does not read `evidence/`. `collect.py` writes the capture. Running it again changes the journal and needs a new review.

[PUBLIC-FILES.txt](PUBLIC-FILES.txt) is the replay set. [RESULT.md](RESULT.md), [NEXT.md](NEXT.md), and [SUBMISSION-TEMPLATE.md](SUBMISSION-TEMPLATE.md) are the Root handback. Source on this branch is not a submission, an acceptance, or paid revenue. Wallet, handle, and `first` stay blank.
