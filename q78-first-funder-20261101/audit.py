#!/usr/bin/env python3
"""Offline Q78 audit. Integer amounts, explicit coverage, no peer totals."""
import csv
import datetime as dt
import json
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
E18 = 10**18
COT = dt.timezone(dt.timedelta(hours=-5))
TOKEN = "0x90c8889f428f9ebb77bb8f15cad3a50a9ac680df"
TREASURY = "0x7c34e9e21ee28a49ff0b84b61774119e6633359f"
TRANSFER = "0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef"
PRIMARY = "https://bsc-mainnet.nodereal.io/v1/64a9df0874fb4a93b9d0a3849de012d3"
SECONDARY = "https://bsc-dataseed.bnbchain.org"
TASK_ID = "0x8c14b4bc3e4017d3aac82de9eb59bb9a1fa53c331a23845274ff435eea936ec6"
TRACE_PARAM = {"tracer": "callTracer", "timeout": "10s"}
# Block-boundary code cannot prove an ordinary-account lifetime. EIP-6780
# specification item 2 keeps SELFDESTRUCT deletion when the contract was
# created in the same transaction, so create, fund, and delete can finish
# between samples. This is a limit, not a captured-recipient finding and
# not a BSC fork-version claim.
END_OF_BLOCK_CODE_LIMIT = (
    "End-of-block code does not prove ordinary-account history, even when every sampled block is empty and the map has no gaps. "
    "A contract can be created, funded, and SELFDESTRUCT in one transaction. "
    "EIP-6780 specification item 2 preserves deletion when that contract is created in the same transaction, so code, nonce, and balance can be empty at every sampled block boundary. "
    "Account creation in that EIP begins at a create transaction or at the start of a CREATE-series operation. "
    "This limit is not a claim that a captured recipient used that pattern, and it is not a BSC fork-version claim."
)
TASK_PHRASES = (
    "0x7C34E9e21eE28A49Ff0b84B61774119E6633359f",
    "0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df",
    "10-28 COT (UTC-5)",
    "first sent it BNB",
    "One new receipt per claim",
    "Up to 2 answers accepted",
)


class AuditError(ValueError):
    pass


def need(condition, message):
    if not condition:
        raise AuditError(message)


def n(value):
    return int(value, 16)


def units(atoms, decimals=18):
    need(isinstance(atoms, int), "amount is not an integer")
    sign = "-" if atoms < 0 else ""
    whole, frac = divmod(abs(atoms), 10**decimals)
    return f"{sign}{whole}.{frac:0{decimals}d}"


def parse_units(text, decimals=18):
    need(isinstance(text, str) and text.count(".") == 1, "amount is not 18-decimal text")
    whole, frac = text.split(".")
    need(whole.lstrip("-").isdigit() and frac.isdigit() and len(frac) == decimals, "amount scale")
    sign = -1 if whole.startswith("-") else 1
    return sign * (int(whole.lstrip("-")) * 10**decimals + int(frac))


def cot_iso(timestamp):
    return dt.datetime.fromtimestamp(int(timestamp), COT).isoformat()


def bind_window(created_at, description):
    """Bind 10-28 COT (UTC-5) from the task clock. Do not scan a different year."""
    for phrase in TASK_PHRASES:
        need(phrase in description, "task text no longer contains " + phrase)
    created = dt.datetime.fromisoformat(created_at.replace("Z", "+00:00"))
    need(created.year == 2026 and created.month == 10, "createdAt does not place 10-28 in October 2026")
    start = dt.datetime(created.year, 10, 28, 0, 0, tzinfo=COT)
    end = start + dt.timedelta(days=1)
    return {
        "year": created.year,
        "startCOT": start.isoformat(),
        "endCOTExclusive": end.isoformat(),
        "startUnix": int(start.timestamp()),
        "endUnixExclusive": int(end.timestamp()),
        "firstTimerUntil": (created + dt.timedelta(hours=24)).isoformat(),
    }


def in_window(timestamp, window):
    return window["startUnix"] <= int(timestamp) < window["endUnixExclusive"]


def chunk_ranges(first, last, step):
    need(first <= last and step > 0, "bad chunk bounds")
    out = []
    cursor = first
    while cursor <= last:
        end = min(cursor + step - 1, last)
        out.append((cursor, end))
        cursor = end + 1
    return out


def topic_address(topic):
    need(isinstance(topic, str) and topic.startswith("0x") and len(topic) == 66, "bad address topic")
    need(topic[2:26] == "0" * 24, "topic is not a padded address")
    return "0x" + topic[-40:].lower()


def pad_address(address):
    need(isinstance(address, str) and len(address) == 42 and address.startswith("0x"), "bad address")
    return "0x" + address[2:].lower().rjust(64, "0")


def decode_transfer(log):
    need(log["address"].lower() == TOKEN, "wrong token")
    need(log["topics"][0].lower() == TRANSFER and len(log["topics"]) == 3, "not a Transfer")
    data = log["data"]
    need(isinstance(data, str) and data.startswith("0x") and len(data) == 66, "Transfer data is not one word")
    return {
        "tx": log["transactionHash"].lower(),
        "logIndex": n(log["logIndex"]),
        "block": n(log["blockNumber"]),
        "blockHash": log["blockHash"].lower(),
        "from": topic_address(log["topics"][1]),
        "to": topic_address(log["topics"][2]),
        "atoms": n(data),
    }


def log_id(row):
    return (row["blockHash"], row["tx"], row["logIndex"])


def canonical(row):
    return (row["block"], row["blockHash"], row["tx"], row["logIndex"], row["from"], row["to"], row["atoms"])


def reconcile_partitions(left, right):
    a = {log_id(row): canonical(row) for row in left}
    b = {log_id(row): canonical(row) for row in right}
    need(len(a) == len(left) and len(b) == len(right), "duplicate log in a partition")
    need(a.keys() == b.keys(), "log partitions cover different transfers")
    need(list(a.values()) == [b[k] for k in a], "log partitions disagree on a transfer body")
    return list(a.values())


def select_first_credit(credits):
    """Earliest successful positive BNB credit. Order is block, tx index, trace order."""
    good = []
    for credit in credits:
        need("status" in credit and "value" in credit, "credit is missing status or value")
        if int(credit["status"]) != 1 or int(credit["value"]) <= 0:
            continue
        need(all(k in credit for k in ("block", "txIndex", "order", "tx", "from", "to", "category")), "incomplete credit")
        good.append(credit)
    if not good:
        return None
    good.sort(key=lambda c: (int(c["block"]), int(c["txIndex"]), int(c["order"]), c["tx"], c["category"]))
    return good[0]


def group_recipients(funders, treasury=TREASURY):
    """Group candidate senders. A group is not a proved lifetime first funder.

    `lifetimeUnknownRecipients` lists every recipient whose coverage is
    `lifetime-unknown`, including rows that still have a candidate sender.
    `candidateMissingRecipients` is the subset with no candidate. Legacy
    `treasuryFirstFunder` is that candidate sender, not a proved lifetime first.
    An empty `incompleteRecipients` list does not mean lifetime history is known.
    """
    treasury_row = next(r for r in funders if r["address"] == treasury and r["role"] == "treasury")
    treasury_funder = treasury_row.get("funder")
    groups = {}
    unfunded = []
    incomplete = []
    unknown = []
    candidate_missing = []
    for row in funders:
        if row["role"] != "recipient":
            continue
        if row["coverage"] == "lifetime-unknown":
            unknown.append(row["address"])
            if not row.get("funder"):
                candidate_missing.append(row["address"])
                continue
            groups.setdefault(row["funder"], []).append(row)
            continue
        if row["coverage"] == "incomplete":
            incomplete.append(row["address"])
            continue
        if row["coverage"] == "absent" or not row.get("funder"):
            unfunded.append(row["address"])
            continue
        groups.setdefault(row["funder"], []).append(row)
    evidence = []
    for funder, members in sorted(groups.items(), key=lambda item: (item[0],)):
        members = sorted(members, key=lambda r: r["address"])
        evidence.append({
            "funder": funder,
            "recipients": [m["address"] for m in members],
            "linkingTransactions": [m["funderTx"] for m in members],
            "funderIsTreasury": funder == treasury,
            "sharesTreasuryFirstFunder": bool(treasury_funder) and funder == treasury_funder,
            "operatorControlProved": False,
            "lifetimeFirstProved": False,
        })
    return {
        "evidenceGroups": evidence,
        "evidenceGroupCount": len(evidence),
        "unfundedRecipients": sorted(unfunded),
        "incompleteRecipients": sorted(incomplete),
        "lifetimeUnknownRecipients": sorted(unknown),
        "candidateMissingRecipients": sorted(candidate_missing),
        "treasuryFirstFunder": treasury_funder,
        "treasuryLifetimeFirstProved": False,
        "realOperatorCount": None,
        "operatorNote": (
            "A shared candidate sender is an evidence group. It is not a proved lifetime first funder and it is not proved common operator control. "
            "lifetimeUnknownRecipients counts every lifetime-unknown recipient, including rows that have a candidate sender. "
            "candidateMissingRecipients is the subset with no saved candidate. "
            "An empty incompleteRecipients list is not a completed lifetime history. "
            + END_OF_BLOCK_CODE_LIMIT
            + " Real operator count is unknown."
        ),
    }


def coverage_label(balance, nonce, code_size, credits, archive_ok, premise_justified=False):
    """Label lifetime BNB provenance from samples this package can use.

    This function does not return `absent`. Empty code, balance, and nonce
    stay `lifetime-unknown`. `lifetime_premise_justified` never reports an
    end-of-block code map as justified, so that map cannot select `observed`.
    `balance` and `nonce` stay in the signature for callers that still pass
    the pin sample; they do not prove absence.
    """
    if not archive_ok or code_size > 0:
        return "incomplete"
    if premise_justified and credits:
        return "observed"
    return "lifetime-unknown"


def lifetime_premise_justified(code_by_block):
    """Return False. No end-of-block code map justifies ordinary-account history.

    `code_by_block` is the caller's block-boundary samples. A missing map, a
    pin sample, a gap, nonempty code, and a gapless map of `0x` from block 0
    are the same result. See `END_OF_BLOCK_CODE_LIMIT`. This function does
    not build a trace index and does not invent historical coverage.
    """
    if isinstance(code_by_block, dict):
        return False
    return False


def assemble_block_credits(transactions, receipts_by_hash, traces_by_hash, address, block):
    """Credits visible in the supplied block body, receipts, and call traces.

    Completeness does not look at an asset-transfer index. Equal external sets,
    including two empty sets, do not mean earlier internal credits were indexed.
    A successful transaction without a call trace leaves coverage incomplete.
    Top-level value transfers with a successful receipt stay in `credits` as
    observed candidates either way.
    """
    credits = []
    limits = []
    if not isinstance(transactions, list):
        return {"complete": False, "credits": [], "limits": ["block transaction list is missing"]}
    if not transactions:
        return {
            "complete": True,
            "credits": [],
            "limits": ["the block contains no transactions; an empty asset index for a nonempty block is a different claim"],
        }
    complete = True
    for tx in transactions:
        if not isinstance(tx, dict) or not tx.get("hash"):
            complete = False
            limits.append("a block transaction object is missing")
            continue
        tx_hash = tx["hash"].lower()
        if tx_hash not in receipts_by_hash:
            complete = False
            limits.append("a transaction receipt is missing")
            continue
        if int(receipts_by_hash[tx_hash]) != 1:
            continue
        trace = traces_by_hash.get(tx_hash)
        if trace is None:
            complete = False
            limits.append("a successful transaction has no call trace")
            if (tx.get("to") or "").lower() == address.lower() and quantity(tx.get("value", "0x0")) > 0:
                credits.append({
                    "block": block,
                    "tx": tx_hash,
                    "txIndex": quantity(tx["transactionIndex"]),
                    "order": 0,
                    "from": (tx.get("from") or "").lower(),
                    "to": address.lower(),
                    "value": quantity(tx.get("value", "0x0")),
                    "status": 1,
                    "category": "external",
                })
            continue
        found = []
        walk_value(trace, address.lower(), {
            "block": block,
            "tx": tx_hash,
            "txIndex": quantity(tx["transactionIndex"]),
        }, found, [0])
        credits.extend(found)
    if not complete and not any(item.startswith("a ") for item in limits):
        limits.append("internal coverage of the block is incomplete")
    if complete:
        limits.append("every successful transaction in this block has a call trace")
    return {"complete": complete, "credits": credits, "limits": limits}


def asset_query(address, block, page_key=None):
    query = {
        "category": ["external", "internal"],
        "fromBlock": hex(block),
        "toBlock": hex(block + 1),
        "toAddress": address,
        "order": "asc",
        "excludeZeroValue": True,
        "maxCount": "0x64",
    }
    if page_key:
        query["pageKey"] = page_key
    return [query]


def decide_funder(normals, internals, internal_complete):
    """Pick the earliest supplied credit inside one block.

    `internal_complete` is meaningful only when `assemble_block_credits`
    produced it from full call traces. Equality of external index rows is
    not that producer. This helper does not decide lifetime absence.
    """
    credits = []
    for item in normals:
        need(int(item["value"]) > 0 and int(item["status"]) == 1, "normal credit is not a successful positive transfer")
        credits.append({**item, "category": "external", "order": 0})
    if internals and not internal_complete:
        raise AuditError("internal credits require complete block coverage")
    if internal_complete:
        for item in internals:
            need(item["category"] in ("internal", "create"), "internal list contains a normal transfer")
            need(int(item["value"]) > 0 and int(item["status"]) == 1, "internal credit is not successful")
            credits.append(item)
    chosen = select_first_credit(credits)
    if chosen is None:
        return "incomplete", None, "no positive BNB credit was found in the first end-state activity block"
    if not internal_complete and int(chosen["txIndex"]) != 0:
        return "incomplete", None, "earlier transactions in the block have no internal-transfer coverage"
    kind = "normal transfer" if chosen["category"] == "external" else chosen["category"] + " transfer"
    return "observed", chosen, "block-local credit only; " + kind


def walk_value(frame, address, meta, out, state, depth=0, failed=False):
    if not isinstance(frame, dict):
        return
    failed = failed or bool(frame.get("error"))
    if not failed:
        to = (frame.get("to") or "").lower()
        raw = frame.get("value") or "0x0"
        value = n(raw) if isinstance(raw, str) else int(raw)
        if to == address and value > 0:
            kind = "create" if str(frame.get("type", "")).upper().startswith("CREATE") else ("external" if depth == 0 else "internal")
            out.append({
                "block": meta["block"],
                "tx": meta["tx"],
                "txIndex": meta["txIndex"],
                "order": state[0],
                "from": (frame.get("from") or "").lower(),
                "to": to,
                "value": value,
                "status": 1,
                "category": kind,
            })
    state[0] += 1
    if failed:
        return
    for child in frame.get("calls") or []:
        walk_value(child, address, meta, out, state, depth + 1, False)


def quantity(value):
    if isinstance(value, str) and value.startswith("0x"):
        return n(value)
    return int(value)


def saved_asset_transfers(good, address, block):
    found = []
    page = None
    for _ in range(8):
        result = saved_get(good, PRIMARY, "nr_getAssetTransfers", asset_query(address, block, page))
        need(isinstance(result, dict) and isinstance(result.get("transfers"), list), "asset transfer result is not a page")
        found.extend(result["transfers"])
        page = result.get("pageKey")
        if not page:
            return found
    raise AuditError("asset transfer pagination did not finish")


def qualifying_increment(predicate, outflow_count):
    """Cross-venue accepted coverage. Award count 0 is not an uncovered receipt."""
    comments = predicate.get("colonyIssuerDecisions") or []
    found = {
        "treasuryFundingAccepted": False,
        "dayTransfersAndFourFundersCovered": False,
        "postCutoffFunderAccepted": False,
    }
    ids = {key: None for key in found}
    for item in comments:
        body = item.get("body") or ""
        comment_id = item.get("id")
        if "Accepted, Q78" in body and "0xe0f7aeee" in body:
            found["treasuryFundingAccepted"] = True
            ids["treasuryFundingAccepted"] = comment_id
        if "17 transfers" in body and "4 first-funder" in body and "already covered" in body:
            found["dayTransfersAndFourFundersCovered"] = True
            ids["dayTransfersAndFourFundersCovered"] = comment_id
        if "Q78 accepted" in body and "0x5bd8ede5" in body:
            found["postCutoffFunderAccepted"] = True
            ids["postCutoffFunderAccepted"] = comment_id
    proved_uncovered = []
    parts = []
    if found["treasuryFundingAccepted"]:
        parts.append("an acceptance comment names treasury funding 0xe0f7aeee")
    if found["dayTransfersAndFourFundersCovered"]:
        parts.append("an issuer comment says the 17 transfers and 4 first-funder transactions in that claim were already covered; this capture counts %s token outflows and the comment does not list those hashes" % outflow_count)
    if found["postCutoffFunderAccepted"]:
        parts.append("an acceptance comment names post-cutoff 0x5bd8ede5")
    if not parts:
        parts.append("the saved comments do not identify an uncovered receipt")
    reason = "; ".join(parts) + ". Taskmarket awardCount is a separate venue and does not prove an uncovered receipt. No saved receipt is provably outside the accepted coverage."
    reason = reason[:1].upper() + reason[1:]
    return {
        "qualifyingIncrementEstablished": bool(proved_uncovered),
        "doNotSubmit": not bool(proved_uncovered),
        "taskmarketAwardCount": predicate.get("awardCount"),
        "taskmarketAwardCountProvesUncoveredReceipt": False,
        "issuerStatements": found,
        "issuerStatementIds": ids,
        "outflowCount": outflow_count,
        "provedUncoveredReceipts": proved_uncovered,
        "reason": reason,
    }


def journal_has(good, url, method, params):
    return json.dumps([url, method, params], sort_keys=True) in good


def funder_from_journal(good, address, block):
    """Recompute block credits from saved receipts and traces.

    The asset-transfer index is not a completeness proof and is not read here.
    Missing traces leave the assessment incomplete and keep any credit the
    saved receipt or trace actually shows.
    """
    full = saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(block), True])
    need(n(full["number"]) == block, "full block number mismatch")
    need(isinstance(full.get("transactions"), list), "full block did not include transaction objects")
    receipts = {}
    traces = {}
    for tx in full["transactions"]:
        if not isinstance(tx, dict) or not tx.get("hash"):
            continue
        tx_hash = tx["hash"].lower()
        for params in ([tx["hash"]], [tx_hash]):
            if journal_has(good, PRIMARY, "eth_getTransactionReceipt", params):
                receipt = saved_get(good, PRIMARY, "eth_getTransactionReceipt", params)
                receipts[tx_hash] = quantity(receipt["status"])
                break
        for params in ([tx["hash"], TRACE_PARAM], [tx_hash, TRACE_PARAM]):
            key = json.dumps([PRIMARY, "debug_traceTransaction", params], sort_keys=True)
            if key in good:
                traces[tx_hash] = good[key]
                break
    return assemble_block_credits(full["transactions"], receipts, traces, address, block)


def route_limits(rows):
    """Count a third log route. Empty responses stay out of the history."""
    empty = nonempty = errors = 0
    for row in rows:
        if row.get("url") != "https://bsc.publicnode.com":
            continue
        if row.get("request", {}).get("method") != "eth_getLogs":
            continue
        response = row.get("response") or {}
        result = response.get("result")
        if row.get("status") != 200 or "result" not in response:
            errors += 1
        elif isinstance(result, list) and len(result) == 0:
            empty += 1
        elif isinstance(result, list):
            nonempty += 1
        else:
            errors += 1
    return {
        "publicnodeLogQueries": empty + nonempty + errors,
        "publicnodeEmptyResults": empty,
        "publicnodeNonemptyResults": nonempty,
        "publicnodeErrors": errors,
        "publicnodeUsedAsHistory": False,
    }


def load_journal(path):
    rows = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    good = {}
    for row in rows:
        if row.get("status") != 200 or "result" not in row.get("response", {}):
            continue
        method = row["request"]["method"]
        params = row["request"]["params"]
        if method == "eth_getBlockByNumber" and params and params[0] in ("latest", "finalized", "pending"):
            continue
        key = json.dumps([row["url"], method, params], sort_keys=True)
        value = row["response"]["result"]
        need(key not in good or good[key] == value, "contradictory saved response for " + method)
        good[key] = value
    return rows, good


def saved_get(good, url, method, params):
    key = json.dumps([url, method, params], sort_keys=True)
    need(key in good, "missing evidence " + method)
    return good[key]


def analyse(evidence_dir=None):
    evidence = Path(evidence_dir or HERE / "evidence")
    task = json.loads((evidence / "task-current.json").read_text())["task"]
    window = bind_window(task["createdAt"], task["description"])
    boundaries = json.loads((evidence / "boundaries.json").read_text())
    need(boundaries["startUnix"] == window["startUnix"], "boundary file does not match the task window")
    first, last = boundaries["firstBlock"], boundaries["lastBlock"]
    rows, good = load_journal(evidence / "rpc.jsonl")
    pin = json.loads((evidence / "snapshot.json").read_text())
    need(n(saved_get(good, PRIMARY, "eth_chainId", [])) == 56, "primary chain is not BSC")
    need(n(saved_get(good, SECONDARY, "eth_chainId", [])) == 56, "secondary chain is not BSC")
    for block_no in (first - 1, first, last, last + 1):
        header = saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(block_no), False])
        alt = saved_get(good, SECONDARY, "eth_getBlockByNumber", [hex(block_no), False])
        need(n(header["number"]) == block_no, "saved header number mismatch")
        need(header["hash"].lower() == alt["hash"].lower() == boundaries["headers"][str(block_no)]["hash"].lower(), "boundary hash mismatch")
        need(int(boundaries["headers"][str(block_no)]["timestamp"]) == n(header["timestamp"]) == n(alt["timestamp"]), "boundary time mismatch")
    need(in_window(n(saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(first), False])["timestamp"]), window), "first block is outside the day")
    need(not in_window(n(saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(first - 1), False])["timestamp"]), window), "previous block is inside the day")
    need(in_window(n(saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(last), False])["timestamp"]), window), "last block is outside the day")
    need(not in_window(n(saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(last + 1), False])["timestamp"]), window), "next block is inside the day")

    def logs_for(step, direction):
        found = []
        for start, end in chunk_ranges(first, last, step):
            topics = [TRANSFER, pad_address(TREASURY), None] if direction == "out" else [TRANSFER, None, pad_address(TREASURY)]
            params = [{"address": TOKEN, "topics": topics, "fromBlock": hex(start), "toBlock": hex(end)}]
            result = saved_get(good, PRIMARY, "eth_getLogs", params)
            need(isinstance(result, list) and len(result) < 1000, "log response is capped or invalid")
            found.extend(decode_transfer(log) for log in result)
        return found

    out_coarse = logs_for(50000, "out")
    out_fine = logs_for(25000, "out")
    in_coarse = logs_for(50000, "in")
    in_fine = logs_for(25000, "in")
    reconcile_partitions(out_coarse, out_fine)
    reconcile_partitions(in_coarse, in_fine)
    outflows = [dict(zip(("block", "blockHash", "tx", "logIndex", "from", "to", "atoms"), row)) for row in reconcile_partitions(out_coarse, out_fine)]
    inflows = [dict(zip(("block", "blockHash", "tx", "logIndex", "from", "to", "atoms"), row)) for row in reconcile_partitions(in_coarse, in_fine)]
    for row in outflows + inflows:
        receipt = saved_get(good, PRIMARY, "eth_getTransactionReceipt", [row["tx"]])
        need(n(receipt["status"]) == 1, "transfer receipt failed")
        need(n(receipt["blockNumber"]) == row["block"], "receipt block mismatch")
        matched = [decode_transfer(log) for log in receipt["logs"] if log["address"].lower() == TOKEN and log["topics"] and log["topics"][0].lower() == TRANSFER]
        need(any(item["logIndex"] == row["logIndex"] and item["atoms"] == row["atoms"] and item["to"] == row["to"] and item["from"] == row["from"] for item in matched), "receipt is missing the transfer")
        header = saved_get(good, PRIMARY, "eth_getBlockByNumber", [hex(row["block"]), False])
        need(header["hash"].lower() == row["blockHash"], "block hash mismatch")
        row["timestamp"] = n(header["timestamp"])
        row["cot"] = cot_iso(row["timestamp"])
        need(in_window(row["timestamp"], window), "transfer is outside the COT day")
        tx = saved_get(good, PRIMARY, "eth_getTransactionByHash", [row["tx"]])
        selector = tx["input"][2:10] if isinstance(tx.get("input"), str) and len(tx["input"]) >= 10 else ""
        if (tx.get("to") or "").lower() == TOKEN and selector == "a9059cbb":
            row["mechanism"] = "normal-transfer-call"
        elif (tx.get("to") or "").lower() == TOKEN and selector == "23b872dd":
            row["mechanism"] = "normal-transferFrom-call"
        else:
            row["mechanism"] = "contract-mediated-transfer-event"
        row["amount"] = units(row["atoms"])
    outflows.sort(key=lambda r: (r["block"], r["logIndex"], r["tx"]))
    inflows.sort(key=lambda r: (r["block"], r["logIndex"], r["tx"]))
    external = [r for r in outflows if r["to"] != TREASURY]
    self_transfers = [r for r in outflows if r["to"] == TREASURY]
    need(len({log_id(r) for r in outflows}) == len(outflows), "duplicate outflow")
    decimals = n(saved_get(good, PRIMARY, "eth_call", [{"to": TOKEN, "data": "0x313ce567"}, hex(last)]))
    need(decimals == 18, "token decimals are not 18")
    before = n(saved_get(good, PRIMARY, "eth_call", [{"to": TOKEN, "data": "0x70a08231" + TREASURY[2:].rjust(64, "0")}, hex(first - 1)]))
    after = n(saved_get(good, PRIMARY, "eth_call", [{"to": TOKEN, "data": "0x70a08231" + TREASURY[2:].rjust(64, "0")}, hex(last)]))
    outflow_atoms = sum(r["atoms"] for r in outflows)
    inflow_atoms = sum(r["atoms"] for r in inflows)
    need(after - before == inflow_atoms - outflow_atoms, "treasury token balance does not reconcile with Transfer logs")
    asset = json.loads((evidence / "asset-outflows.json").read_text())
    asset_counter = Counter((item["tx"], item["from"], item["to"], int(item["atoms"])) for item in asset)
    log_counter = Counter((r["tx"], r["from"], r["to"], r["atoms"]) for r in outflows)
    need(asset_counter == log_counter, "asset-transfer index does not match Transfer logs")
    if external:
        sample = saved_get(good, SECONDARY, "eth_getTransactionReceipt", [external[0]["tx"]])
        need(n(sample["status"]) == 1 and n(sample["blockNumber"]) == external[0]["block"], "secondary receipt sample mismatch")

    funder_doc = json.loads((evidence / "funders.json").read_text())
    need(any(r["role"] == "treasury" and r["address"] == TREASURY for r in funder_doc), "missing treasury funder row")
    recipients = sorted({r["to"] for r in external})
    seen = [r["address"] for r in funder_doc if r["role"] == "recipient"]
    need(seen == recipients, "funder rows do not match outflow recipients")
    pin_no = n(pin["number"])
    need(quantity(saved_get(good, PRIMARY, "eth_getBalance", [TREASURY, "0x1"])) == 0, "block 1 balance is not an archive read")
    for row in funder_doc:
        addr = row["address"]
        need(row["operatorControlProved"] is False, "funder row claims proved control")
        bal = quantity(saved_get(good, PRIMARY, "eth_getBalance", [addr, hex(pin_no)]))
        nonce = quantity(saved_get(good, PRIMARY, "eth_getTransactionCount", [addr, hex(pin_no)]))
        code = saved_get(good, PRIMARY, "eth_getCode", [addr, hex(pin_no)])
        need(bal == row["balanceAtPin"] and nonce == row["nonceAtPin"], "pin state does not match the funder row")
        need(code.startswith("0x") and (len(code) - 2) // 2 == row["codeBytes"], "code size does not match the funder row")
        row["captureCoverage"] = row["coverage"]
        row["lifetimePremiseJustified"] = lifetime_premise_justified({pin_no: code})
        row["lifetimeFirstProved"] = False
        row["lifetimeAbsenceProved"] = False
        row["blockCoverageComplete"] = False
        if code != "0x":
            row["coverage"] = "incomplete"
            row["candidateLimit"] = "nonempty code at the pin; an end-state search is not a proved lifetime first funder"
            row["note"] = row["candidateLimit"]
            need(row["funder"] is None, "nonempty code row invented a lifetime funder")
            continue
        if bal == 0 and nonce == 0:
            row["coverage"] = "lifetime-unknown"
            row["candidateLimit"] = "No candidate transfer was saved. Empty code, balance, and nonce at the pin do not prove lifetime absence. " + END_OF_BLOCK_CODE_LIMIT
            row["note"] = row["candidateLimit"]
            need(row["funder"] is None, "empty pin row invented a lifetime funder")
            continue
        fb = row["firstActivityBlock"]
        need(isinstance(fb, int) and fb > 0, "missing first activity block")
        need(quantity(saved_get(good, PRIMARY, "eth_getBalance", [addr, hex(fb - 1)])) == 0, "balance before the recorded crossing is not zero")
        need(quantity(saved_get(good, PRIMARY, "eth_getTransactionCount", [addr, hex(fb - 1)])) == 0, "nonce before the recorded crossing is not zero")
        at_bal = quantity(saved_get(good, PRIMARY, "eth_getBalance", [addr, hex(fb)]))
        at_nonce = quantity(saved_get(good, PRIMARY, "eth_getTransactionCount", [addr, hex(fb)]))
        need(at_bal > 0 or at_nonce > 0, "recorded crossing block has no end-state activity")
        assessment = funder_from_journal(good, addr, fb)
        row["blockCoverageComplete"] = assessment["complete"]
        row["coverage"] = "lifetime-unknown"
        matches = [
            credit for credit in assessment["credits"]
            if credit["tx"] == row["funderTx"]
            and credit["from"] == row["funder"]
            and credit["category"] == row["category"]
            and credit["value"] == int(row["valueAtoms"])
            and credit["txIndex"] == row["funderTxIndex"]
            and credit["block"] == row["funderBlock"] == fb
        ]
        need(matches, "recorded candidate is not among the credits saved for the crossing block")
        row["candidateLimit"] = "Candidate sender only. This is not a proved lifetime first funder. " + END_OF_BLOCK_CODE_LIMIT + " " + "; ".join(assessment["limits"])
        row["note"] = row["candidateLimit"]
        if isinstance(row.get("valueAtoms"), int):
            row["bnb"] = units(row["valueAtoms"])
    groups = group_recipients(funder_doc)
    predicate = json.loads((evidence / "predicate.json").read_text())
    need(predicate["escrowIsAward"] is False, "predicate file treats escrow as an award")
    need(predicate["taskStatus"] == task["status"], "predicate status does not match the task capture")
    need(predicate["awardCount"] == task["awardCount"], "predicate award count does not match the task capture")
    unexplained = []
    for row in external:
        if row["mechanism"] not in ("normal-transfer-call", "normal-transferFrom-call", "contract-mediated-transfer-event"):
            unexplained.append(row["tx"])
    summary = {
        "taskId": task["id"],
        "referenceCode": task.get("referenceCode"),
        "window": window,
        "bounds": {
            "firstBlock": first,
            "lastBlock": last,
            "previousBlock": first - 1,
            "nextBlock": last + 1,
            "headers": boundaries["headers"],
        },
        "pin": {"number": n(pin["number"]), "hash": pin["hash"], "timestamp": n(pin["timestamp"])},
        "token": {"address": TOKEN, "decimals": 18},
        "treasury": TREASURY,
        "counts": {
            "outflowLogs": len(outflows),
            "externalOutflows": len(external),
            "selfTransfers": len(self_transfers),
            "inflowLogs": len(inflows),
            "distinctRecipients": len(recipients),
        },
        "totals": {
            "externalOutAtoms": str(sum(r["atoms"] for r in external)),
            "externalOut": units(sum(r["atoms"] for r in external)),
            "allOutAtoms": str(outflow_atoms),
            "allOut": units(outflow_atoms),
            "inAtoms": str(inflow_atoms),
            "in": units(inflow_atoms),
            "treasuryBefore": units(before),
            "treasuryAfter": units(after),
            "balanceDeltaAtoms": str(after - before),
        },
        "reconciliation": "treasury token balance change equals token inflow logs minus token outflow logs, to the base unit. This identity does not prove lifetime BNB provenance.",
        "groups": groups,
        "eligibility": qualifying_increment(predicate, len(external)),
        "unexplainedTransfers": unexplained,
        "limits": route_limits(rows),
        "acceptance": {
            "readAt": predicate["readAt"],
            "taskStatus": predicate["taskStatus"],
            "awardCount": predicate["awardCount"],
            "submissionCount": predicate["submissionCount"],
            "rewardBaseUnits": predicate["rewardBaseUnits"],
            "escrowBooked": predicate["escrowBooked"],
            "escrowIsAward": False,
            "expiryTime": predicate["expiryTime"],
            "capturedAfterFirstTimerWindow": predicate["capturedAfterFirstTimerWindow"],
            "firstTimerUntil": predicate["window"]["firstTimerUntil"],
            "submissionSummary": predicate["submissionSummary"],
            "ugigQ78Listed": predicate["ugigPublicIndex"]["q78Listed"],
            "ugigIndexTotal": predicate["ugigPublicIndex"]["pagination"]["total"],
            "colonyCommentCount": len(predicate["colonyIssuerDecisions"]),
            "note": predicate["note"],
        },
        "outflows": external,
        "selfTransfers": self_transfers,
        "inflows": inflows,
        "funders": funder_doc,
        "journalRows": len(rows),
    }
    return summary


def write_derived(summary, out_dir=None):
    out = Path(out_dir or HERE / "derived")
    out.mkdir(parents=True, exist_ok=True)
    public = {k: v for k, v in summary.items()}
    (out / "summary.json").write_text(json.dumps(public, indent=2) + "\n")

    def dump(name, rows, fields):
        with (out / name).open("w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)

    dump("outflows.csv", summary["outflows"], ["tx", "logIndex", "block", "timestamp", "cot", "to", "atoms", "amount", "mechanism", "blockHash"])
    dump("inflows.csv", summary["inflows"], ["tx", "logIndex", "block", "timestamp", "cot", "from", "atoms", "amount", "mechanism"])
    dump("funders.csv", summary["funders"], ["role", "address", "coverage", "captureCoverage", "lifetimeFirstProved", "lifetimeAbsenceProved", "lifetimePremiseJustified", "blockCoverageComplete", "funder", "funderTx", "funderBlock", "funderTxIndex", "category", "valueAtoms", "bnb", "balanceAtPin", "nonceAtPin", "codeBytes", "candidateLimit"])
    group_rows = []
    for group in summary["groups"]["evidenceGroups"]:
        group_rows.append({
            "funder": group["funder"],
            "recipients": " ".join(group["recipients"]),
            "linkingTransactions": " ".join(group["linkingTransactions"]),
            "funderIsTreasury": group["funderIsTreasury"],
            "sharesTreasuryFirstFunder": group["sharesTreasuryFirstFunder"],
            "operatorControlProved": group["operatorControlProved"],
            "lifetimeFirstProved": group["lifetimeFirstProved"],
        })
    dump("groups.csv", group_rows, ["funder", "recipients", "linkingTransactions", "funderIsTreasury", "sharesTreasuryFirstFunder", "operatorControlProved", "lifetimeFirstProved"])
    with (out / "rows.jsonl").open("w") as handle:
        by = {r["address"]: r for r in summary["funders"] if r["role"] == "recipient"}
        for row in summary["outflows"]:
            funder = by[row["to"]]
            handle.write(json.dumps({
                "tx": row["tx"],
                "logIndex": row["logIndex"],
                "block": row["block"],
                "cot": row["cot"],
                "recipient": row["to"],
                "atoms": str(row["atoms"]),
                "amount": row["amount"],
                "mechanism": row["mechanism"],
                "funderCoverage": funder["coverage"],
                "lifetimeFirstProved": funder.get("lifetimeFirstProved"),
                "candidateFunder": funder.get("funder"),
                "candidateFunderTx": funder.get("funderTx"),
                "candidateCategory": funder.get("category"),
            }, separators=(",", ":")) + "\n")
    return out


def main():
    summary = analyse()
    write_derived(summary)
    print(json.dumps({"external": summary["counts"]["externalOutflows"], "recipients": summary["counts"]["distinctRecipients"], "total": summary["totals"]["externalOut"], "groups": summary["groups"]["evidenceGroupCount"], "unexplained": len(summary["unexplainedTransfers"])}, indent=2))


if __name__ == "__main__":
    main()
