#!/usr/bin/env python3
"""Serial public reads for the Q78 treasury day and first BNB funders.

No signer, transfer, paid API, or new wallet. A failed route is recorded.
An empty log page is evidence only for the range that was actually returned.
"""
import datetime as dt
import json
import time
import urllib.error
import urllib.request
from pathlib import Path

from audit import (
    PRIMARY,
    SECONDARY,
    TOKEN,
    TRACE_PARAM,
    TRANSFER,
    TREASURY,
    asset_query,
    bind_window,
    chunk_ranges,
    decide_funder,
    pad_address,
    quantity,
    walk_value,
)

HERE = Path(__file__).resolve().parent
EVIDENCE = HERE / "evidence"
PUBLICNODE = "https://bsc.publicnode.com"
ALLOWED = {
    "eth_chainId",
    "eth_getBlockByNumber",
    "eth_call",
    "eth_getLogs",
    "eth_getBalance",
    "eth_getTransactionReceipt",
    "eth_getTransactionByHash",
    "eth_getTransactionCount",
    "eth_getCode",
    "debug_traceTransaction",
    "nr_getAssetTransfers",
    "web3_sha3",
}
URLS = {PRIMARY, SECONDARY, PUBLICNODE}


class RPC:
    def __init__(self, path):
        self.path = path
        self.cache = {}
        self.live = 0
        self.errors = []
        if path.exists():
            for line in path.read_text().splitlines():
                if not line.strip():
                    continue
                row = json.loads(line)
                if row.get("status") == 200 and "result" in row.get("response", {}):
                    self.cache[self.key(row["url"], row["request"]["method"], row["request"]["params"])] = row["response"]["result"]

    @staticmethod
    def key(url, method, params):
        return json.dumps([url, method, params], sort_keys=True)

    def __call__(self, method, params, url=PRIMARY, optional=False):
        if method not in ALLOWED or url not in URLS:
            raise RuntimeError("route is not allowed")
        key = self.key(url, method, params)
        if key in self.cache:
            return self.cache[key]
        payload = {"jsonrpc": "2.0", "id": 1, "method": method, "params": params}
        for attempt in range(4):
            if self.live >= 4000:
                raise RuntimeError("request budget exhausted")
            started = time.monotonic()
            at = dt.datetime.now(dt.timezone.utc).isoformat()
            try:
                request = urllib.request.Request(
                    url,
                    data=json.dumps(payload).encode(),
                    headers={"Content-Type": "application/json", "User-Agent": "receipt-audits-q78-readonly"},
                )
                with urllib.request.urlopen(request, timeout=40) as response:
                    status = response.status
                    body = response.read(12000000).decode()
            except urllib.error.HTTPError as exc:
                status = exc.code
                body = exc.read(4000).decode(errors="replace")
            except OSError as exc:
                status = 0
                body = str(exc)
            try:
                parsed = json.loads(body)
            except ValueError:
                parsed = {"transportError": body[:2000]}
            row = {"at": at, "seconds": round(time.monotonic() - started, 4), "url": url, "request": payload, "status": status, "response": parsed}
            with self.path.open("a") as handle:
                handle.write(json.dumps(row, separators=(",", ":")) + "\n")
            self.live += 1
            if status == 200 and "result" in parsed:
                self.cache[key] = parsed["result"]
                time.sleep(0.02)
                return parsed["result"]
            if status in (0, 429, 502, 503, 504) or "rate" in json.dumps(parsed).lower():
                time.sleep(2 ** attempt)
                continue
            self.errors.append({"method": method, "url": url, "status": status, "error": parsed.get("error", parsed) if isinstance(parsed, dict) else parsed})
            if optional:
                return None
            raise RuntimeError(method + " failed: " + json.dumps(parsed)[:500])
        if optional:
            return None
        raise RuntimeError("retries exhausted for " + method)


def get_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": "receipt-audits-q78-readonly", "Accept": "application/json"})
    with urllib.request.urlopen(request, timeout=60) as response:
        return response.status, json.loads(response.read())


def state_of(rpc, address, block):
    balance = quantity(rpc("eth_getBalance", [address, hex(block)]))
    nonce = quantity(rpc("eth_getTransactionCount", [address, hex(block)]))
    return balance, nonce


def first_activity(rpc, address, pin):
    balance, nonce = state_of(rpc, address, pin)
    if balance == 0 and nonce == 0:
        return None
    low, high = 1, pin
    while low + 1 < high:
        mid = (low + high) // 2
        mid_balance, mid_nonce = state_of(rpc, address, mid)
        if mid_balance or mid_nonce:
            high = mid
        else:
            low = mid
    return high


def asset_pages(rpc, params):
    rows = []
    page = None
    for _ in range(8):
        query = dict(params[0])
        if page:
            query["pageKey"] = page
        result = rpc("nr_getAssetTransfers", [query])
        if not isinstance(result, dict) or not isinstance(result.get("transfers"), list):
            raise RuntimeError("asset transfer page is invalid")
        rows.extend(result["transfers"])
        page = result.get("pageKey")
        if not page:
            return rows
    raise RuntimeError("asset transfer pagination did not finish")


def token_asset_rows(rpc, first, last):
    found = []
    cursor = first
    while cursor <= last:
        end = min(cursor + 89999, last)
        params = [{
            "category": ["20"],
            "fromBlock": hex(cursor),
            "toBlock": hex(end + 1),
            "fromAddress": TREASURY,
            "contractAddresses": [TOKEN],
            "order": "asc",
            "maxCount": "0x3e8",
        }]
        for item in asset_pages(rpc, params):
            block = quantity(item["blockNum"])
            if not cursor <= block <= end:
                continue
            if item.get("from", "").lower() != TREASURY or item.get("contractAddress", "").lower() != TOKEN:
                continue
            if int(item.get("receiptsStatus", 0)) != 1:
                continue
            found.append({
                "tx": item["hash"].lower(),
                "from": item["from"].lower(),
                "to": item["to"].lower(),
                "atoms": quantity(item["value"]),
                "block": block,
            })
        cursor = end + 1
    return found


def log_query(start, end, direction):
    topics = [TRANSFER, pad_address(TREASURY), None] if direction == "out" else [TRANSFER, None, pad_address(TREASURY)]
    return [{"address": TOKEN, "topics": topics, "fromBlock": hex(start), "toBlock": hex(end)}]


def scan_logs(rpc, first, last, step, direction, url=PRIMARY):
    found = []
    for start, end in chunk_ranges(first, last, step):
        result = rpc("eth_getLogs", log_query(start, end, direction), url)
        if not isinstance(result, list) or len(result) >= 1000:
            raise RuntimeError("log page is capped or invalid")
        found.extend(result)
    return found


def run():
    started = time.monotonic()
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    rpc = RPC(EVIDENCE / "rpc.jsonl")
    status, task = get_json("https://api.taskmarket.dev/api/tasks/" + "0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6")
    read_at = dt.datetime.now(dt.timezone.utc).isoformat()
    (EVIDENCE / "task-current.json").write_text(json.dumps({"readAt": read_at, "status": status, "source": "https://api.taskmarket.dev/api/tasks/0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6", "task": task}, indent=2) + "\n")
    window = bind_window(task["createdAt"], task["description"])
    _, submissions = get_json("https://api.taskmarket.dev/api/tasks/0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6/submissions")
    acceptance_fields = sorted({key for item in submissions for key in item if "accept" in key.lower() or key in ("rejectedAt", "status", "award")})
    submission_summary = {
        "count": len(submissions),
        "rejectedAtNull": sum(item.get("rejectedAt") is None for item in submissions),
        "acceptedAtValues": sum(bool(item.get("acceptedAt")) for item in submissions),
        "acceptanceFields": acceptance_fields,
    }
    colony = []
    for page in range(1, 6):
        _, payload = get_json("https://thecolony.ai/api/v1/posts/cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb/comments?page=" + str(page))
        for item in payload.get("items", []):
            author = (item.get("author") or {}).get("username")
            body = item.get("body") or ""
            if author == "flapjaxculture" and ("Q78" in body or "B583" in body or "B584" in body):
                colony.append({"id": item.get("id"), "created_at": item.get("created_at"), "body": body})
        if not payload.get("has_more"):
            break
    _, ugig = get_json("https://ugig.net/api/bounties")
    ugig_rows = [{"id": row.get("id"), "title": row.get("title"), "status": row.get("status")} for row in ugig.get("data", [])]
    routes = {
        "etherscanV2Bsc": "https://api.etherscan.io/v2/api refused free BSC coverage before this capture",
        "routescanBsc": "https://api.routescan.io returned chain not supported",
        "bscscanV1": "https://api.bscscan.com/api returned an HTML API-migration page",
        "blockscoutBsc": "https://bsc.blockscout.com/api and /api/v2 returned HTTP 404",
        "ugig": "unauthenticated GET /api/bounties",
    }
    predicate = {
        "readAt": read_at,
        "taskStatus": task.get("status"),
        "awardCount": task.get("awardCount"),
        "submissionCount": task.get("submissionCount"),
        "rewardBaseUnits": task.get("reward"),
        "escrowBooked": (task.get("escrow") or {}).get("booked"),
        "escrowIsAward": False,
        "expiryTime": task.get("expiryTime"),
        "createdAt": task.get("createdAt"),
        "window": window,
        "capturedAfterFirstTimerWindow": read_at > window["firstTimerUntil"],
        "submissionSummary": submission_summary,
        "colonyIssuerDecisions": colony,
        "ugigPublicIndex": {"pagination": ugig.get("pagination"), "q78Listed": any("Q78" in (row["title"] or "") for row in ugig_rows), "rows": ugig_rows},
        "routes": routes,
        "note": "Taskmarket awardCount is this task's accepted-claim count. Colony decisions are a different venue. A public ugig index that omits Q78 does not prove ugig never accepted it.",
    }
    (EVIDENCE / "predicate.json").write_text(json.dumps(predicate, indent=2) + "\n")
    print("predicate", task.get("status"), "awards", task.get("awardCount"), "submissions", submission_summary["count"], flush=True)

    pin = rpc("eth_getBlockByNumber", ["finalized", False])
    (EVIDENCE / "snapshot.json").write_text(json.dumps(pin) + "\n")
    pin_no = quantity(pin["number"])
    for url in (PRIMARY, SECONDARY):
        if quantity(rpc("eth_chainId", [], url)) != 56:
            raise RuntimeError("unexpected chain")
        alt = rpc("eth_getBlockByNumber", [pin["number"], False], url)
        if alt["hash"].lower() != pin["hash"].lower():
            raise RuntimeError("pin hash mismatch")
    opened = quantity(rpc("eth_getBalance", [TREASURY, "0x1"]))
    if opened != 0:
        raise RuntimeError("historical balance is unavailable: treasury balance at block 1 is nonzero")
    sha = rpc("web3_sha3", ["0x" + b"Transfer(address,address,uint256)".hex()], optional=True)
    if sha is not None and sha.lower() != TRANSFER:
        raise RuntimeError("Transfer topic mismatch")

    def search(target):
        low, high = 1, pin_no
        while low + 1 < high:
            mid = (low + high) // 2
            stamp = quantity(rpc("eth_getBlockByNumber", [hex(mid), False])["timestamp"])
            if stamp < target:
                low = mid
            else:
                high = mid
        return high

    first = search(window["startUnix"])
    next_day = search(window["endUnixExclusive"])
    last = next_day - 1
    headers = {}
    for block_no in (first - 1, first, last, last + 1):
        header = rpc("eth_getBlockByNumber", [hex(block_no), False])
        other = rpc("eth_getBlockByNumber", [hex(block_no), False], SECONDARY)
        if header["hash"].lower() != other["hash"].lower():
            raise RuntimeError("boundary provider mismatch")
        headers[str(block_no)] = {"number": block_no, "hash": header["hash"].lower(), "timestamp": quantity(header["timestamp"])}
    (EVIDENCE / "boundaries.json").write_text(json.dumps({"startUnix": window["startUnix"], "endUnixExclusive": window["endUnixExclusive"], "firstBlock": first, "lastBlock": last, "headers": headers}, indent=2) + "\n")
    print("window", first, last, "pin", pin_no, flush=True)

    for step in (50000, 25000):
        for direction in ("out", "in"):
            scan_logs(rpc, first, last, step, direction)
            print("logs", step, direction, "requests", rpc.live, flush=True)
    publicnode = {"status": "not-run"}
    try:
        from audit import decode_transfer, log_id
        primary_ids = []
        other_ids = []
        for start, end in chunk_ranges(first, last, 50000):
            primary_ids.extend(log_id(decode_transfer(log)) for log in rpc("eth_getLogs", log_query(start, end, "out")))
            other_ids.extend(log_id(decode_transfer(log)) for log in rpc("eth_getLogs", log_query(start, end, "out"), PUBLICNODE))
        if sorted(primary_ids) != sorted(other_ids):
            raise RuntimeError("publicnode log set differs from the primary log set")
        publicnode = {"status": "matched-outflow-logs", "logs": len(primary_ids)}
    except Exception as exc:
        publicnode = {"status": "unavailable", "error": str(exc)[:300]}
        print("publicnode", publicnode, flush=True)

    # Touch every outflow transaction once the offline pass can see the logs.
    # The receipt/block reads happen after a local decode so failed scans stop first.
    from audit import decode_transfer
    coarse = []
    for start, end in chunk_ranges(first, last, 50000):
        coarse.extend(decode_transfer(log) for log in rpc("eth_getLogs", log_query(start, end, "out")))
    seen = set()
    for row in coarse:
        if row["tx"] in seen:
            continue
        seen.add(row["tx"])
        rpc("eth_getTransactionByHash", [row["tx"]])
        rpc("eth_getTransactionReceipt", [row["tx"]])
        rpc("eth_getBlockByNumber", [hex(row["block"]), False])
    if coarse:
        rpc("eth_getTransactionReceipt", [coarse[0]["tx"]], SECONDARY)
    for block_no in (first - 1, last):
        rpc("eth_call", [{"to": TOKEN, "data": "0x70a08231" + TREASURY[2:].rjust(64, "0")}, hex(block_no)])
    rpc("eth_call", [{"to": TOKEN, "data": "0x313ce567"}, hex(last)])
    for start, end in chunk_ranges(first, last, 50000):
        for log in rpc("eth_getLogs", log_query(start, end, "in")):
            item = decode_transfer(log)
            rpc("eth_getTransactionByHash", [item["tx"]])
            rpc("eth_getTransactionReceipt", [item["tx"]])
            rpc("eth_getBlockByNumber", [hex(item["block"]), False])
    asset_rows = token_asset_rows(rpc, first, last)
    (EVIDENCE / "asset-outflows.json").write_text(json.dumps(asset_rows, indent=2) + "\n")
    print("asset rows", len(asset_rows), "log txs", len(seen), flush=True)

    recipients = sorted({row["to"] for row in coarse if row["to"] != TREASURY})
    subjects = [(addr, "recipient") for addr in recipients] + [(TREASURY, "treasury")]
    funders = []
    for address, role in subjects:
        code = rpc("eth_getCode", [address, hex(pin_no)])
        balance, nonce = state_of(rpc, address, pin_no)
        row = {
            "role": role,
            "address": address,
            "coverage": "incomplete",
            "funder": None,
            "funderTx": None,
            "funderBlock": None,
            "funderTxIndex": None,
            "category": None,
            "valueAtoms": None,
            "balanceAtPin": balance,
            "nonceAtPin": nonce,
            "codeBytes": (len(code) - 2) // 2,
            "firstActivityBlock": None,
            "operatorControlProved": False,
            "note": "",
        }
        if code != "0x":
            row["note"] = "code is present at the pin, so an end-state search is not a lifetime first-funder proof"
        elif balance == 0 and nonce == 0:
            row["coverage"] = "absent"
            row["note"] = "empty code, nonce 0, and balance 0 at the pin; an EOA cannot have spent a prior BNB credit without increasing nonce"
        else:
            block = first_activity(rpc, address, pin_no)
            row["firstActivityBlock"] = block
            state_of(rpc, address, block - 1)
            state_of(rpc, address, block)
            full = rpc("eth_getBlockByNumber", [hex(block), True])
            normals = []
            for tx in full["transactions"]:
                if (tx.get("to") or "").lower() != address or quantity(tx["value"]) <= 0:
                    continue
                receipt = rpc("eth_getTransactionReceipt", [tx["hash"]])
                if quantity(receipt["status"]) != 1:
                    continue
                normals.append({
                    "block": block,
                    "tx": tx["hash"].lower(),
                    "txIndex": quantity(tx["transactionIndex"]),
                    "from": tx["from"].lower(),
                    "to": address,
                    "value": quantity(tx["value"]),
                    "status": 1,
                })
            asset = asset_pages(rpc, asset_query(address, block))
            asset_ext = {}
            internal_items = []
            for item in asset:
                if quantity(item["blockNum"]) != block or item.get("to", "").lower() != address:
                    continue
                value = quantity(item["value"])
                if value <= 0 or int(item.get("receiptsStatus", 0)) != 1:
                    continue
                if item.get("category") == "external":
                    asset_ext[item["hash"].lower()] = (item["from"].lower(), value)
                elif item.get("category") == "internal":
                    internal_items.append(item)
            internal_complete = asset_ext == {item["tx"]: (item["from"], item["value"]) for item in normals}
            internals = []
            trace_missing = False
            if internal_complete and internal_items:
                traced = set()
                for item in internal_items:
                    tx_hash = item["hash"].lower()
                    if tx_hash in traced:
                        continue
                    traced.add(tx_hash)
                    tx = rpc("eth_getTransactionByHash", [tx_hash])
                    receipt = rpc("eth_getTransactionReceipt", [tx_hash])
                    if quantity(receipt["status"]) != 1:
                        continue
                    traced_call = rpc("debug_traceTransaction", [tx_hash, TRACE_PARAM], optional=True)
                    if traced_call is None:
                        trace_missing = True
                        break
                    found = []
                    walk_value(traced_call, address, {
                        "block": block,
                        "tx": tx_hash,
                        "txIndex": quantity(tx["transactionIndex"]),
                    }, found, [0])
                    internals.extend(credit for credit in found if credit["category"] != "external")
            if trace_missing:
                coverage, chosen, note = "incomplete", None, "an internal BNB credit was indexed but its call trace was unavailable"
            else:
                coverage, chosen, note = decide_funder(normals, internals, internal_complete and not trace_missing)
            row["coverage"] = coverage
            row["note"] = note
            if chosen:
                row.update({
                    "funder": chosen["from"],
                    "funderTx": chosen["tx"],
                    "funderBlock": chosen["block"],
                    "funderTxIndex": chosen["txIndex"],
                    "category": chosen["category"],
                    "valueAtoms": chosen["value"],
                })
        funders.append(row)
        print(role, address[:10], row["coverage"], row["funder"], flush=True)
    (EVIDENCE / "funders.json").write_text(json.dumps(funders, indent=2) + "\n")
    stats = {
        "seconds": round(time.monotonic() - started, 3),
        "newRequests": rpc.live,
        "publicnode": publicnode,
        "routes": routes,
        "pin": pin_no,
        "firstBlock": first,
        "lastBlock": last,
    }
    (EVIDENCE / "capture-stats.json").write_text(json.dumps(stats, indent=2) + "\n")
    print(json.dumps(stats), flush=True)


if __name__ == "__main__":
    run()
