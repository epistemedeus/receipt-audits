#!/usr/bin/env python3
"""Replay the saved capture, check totals, and sample one public route."""
import json
import urllib.request
from pathlib import Path

import audit
import independent

HERE = Path(__file__).resolve().parent
SECONDARY = "https://bsc-dataseed.bnbchain.org"


def live(method, params):
    payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
    request = urllib.request.Request(
        SECONDARY,
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json", "User-Agent": "receipt-audits-q78-readonly"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        body = json.loads(response.read())
    if "result" not in body:
        raise SystemExit("live sample failed: " + json.dumps(body)[:300])
    return body["result"]


def main():
    summary = audit.analyse()
    audit.write_derived(summary)
    independent.main()
    sample = summary["outflows"][0]
    receipt = live("eth_getTransactionReceipt", [sample["tx"]])
    header = live("eth_getBlockByNumber", [hex(summary["bounds"]["firstBlock"]), False])
    if int(receipt["status"], 16) != 1 or int(receipt["blockNumber"], 16) != sample["block"]:
        raise SystemExit("live receipt does not match the saved outflow")
    if header["hash"].lower() != summary["bounds"]["headers"][str(summary["bounds"]["firstBlock"])]["hash"]:
        raise SystemExit("live boundary hash does not match")
    print(json.dumps({
        "external": summary["counts"]["externalOutflows"],
        "total": summary["totals"]["externalOut"],
        "groups": summary["groups"]["evidenceGroupCount"],
        "liveReceipt": sample["tx"],
        "liveBlock": summary["bounds"]["firstBlock"],
    }))


if __name__ == "__main__":
    main()
