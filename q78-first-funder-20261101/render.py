#!/usr/bin/env python3
"""Render the public audit from derived/summary.json. No network."""
import json
from pathlib import Path

from audit import PRIMARY, SECONDARY, cot_iso, units

HERE = Path(__file__).resolve().parent


def link_tx(value):
    return f"[`{value}`](https://bscscan.com/tx/{value})"


def link_addr(value):
    return f"[`{value}`](https://bscscan.com/address/{value})"


def table(headers, rows):
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join("---" for _ in headers) + " |"]
    lines.extend("| " + " | ".join(str(cell) for cell in row) + " |" for row in rows)
    return "\n".join(lines)


def bnb_cell(row):
    if isinstance(row.get("valueAtoms"), int):
        return row.get("bnb") or units(row["valueAtoms"])
    return ""


def render(summary):
    window = summary["window"]
    bounds = summary["bounds"]
    headers = bounds["headers"]
    groups = summary["groups"]
    acceptance = summary["acceptance"]
    limits = summary["limits"]
    after_day = [
        row for row in summary["funders"]
        if isinstance(row.get("funderBlock"), int) and row["funderBlock"] > bounds["lastBlock"]
    ]
    lines = [
        "# Q78 treasury outflows for 28 October 2026 COT",
        "",
        "This is a chain receipt audit of FLAPJAX transfers out of one treasury address during one Central offset day. It is a receipt record. It is not a token offer, a price, or a request to buy. The booked escrow below is the listing's locked amount. It is not an award and it is not paid revenue. Nothing in this repository was submitted to the requester.",
        "",
        f"Task [`{summary['taskId']}`](https://api.taskmarket.dev/api/tasks/{summary['taskId']}) (`{summary.get('referenceCode')}`), specification [Colony post cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb](https://thecolony.ai/post/cc0ad06c-be2e-4916-b5c3-7b3a3aa240fb). Token `{summary['token']['address']}` (18 decimals). Treasury `{summary['treasury']}`. BSC chain id 56. The USDC escrow is on Base chain id 8453.",
        "",
        f"The task says 10-28 COT (UTC-5). The task was created {window['year']}-10-29, so the day is 28 October {window['year']}. Inclusive start `{window['startCOT']}` ({window['startUnix']}). Exclusive end `{window['endCOTExclusive']}` ({window['endUnixExclusive']}).",
        "",
        "## Acceptance at capture",
        "",
        f"Taskmarket read at `{acceptance['readAt']}`. Status `{acceptance['taskStatus']}`. Award count `{acceptance['awardCount']}`. Submission count `{acceptance['submissionCount']}`. Stored submissions with `rejectedAt` null: `{acceptance['submissionSummary']['rejectedAtNull']}`. Stored `acceptedAt` values: `{acceptance['submissionSummary']['acceptedAtValues']}`. Acceptance fields present: `{', '.join(acceptance['submissionSummary']['acceptanceFields'])}`. Reward field `{acceptance['rewardBaseUnits']}` base units. Escrow booked `{acceptance['escrowBooked']}` base units. `escrowIsAward` is `{str(acceptance['escrowIsAward']).lower()}`. Expiry `{acceptance['expiryTime']}`.",
        "",
        f"The written 24 hour first-timer reservation ends `{acceptance['firstTimerUntil']}`. This capture is after that instant (`capturedAfterFirstTimerWindow` `{str(acceptance['capturedAfterFirstTimerWindow']).lower()}`). Award count `{acceptance['awardCount']}` means no answer has been accepted on this task. The task text says that if no first-timer qualifies within 24 hours, the slots open to any agent. The stored submission counts do not label which workers are first-timers, so this package does not decide that the opening condition has been met, and it does not mark any submitter `first=yes`.",
        "",
        f"Colony is a separate venue. `{acceptance['colonyCommentCount']}` issuer comments that mention Q78, B583, or B584 are stored in [predicate.json](evidence/predicate.json). Those comments record Colony acceptances and declines, including a treasury first-funding transaction at block 123473817 and transaction `0x5bd8ede5` for recipient `0x2ae18c3b`. The same two transactions were read again from BSC below. The comments do not change this task's award count. The issuer's written rule is one payout per operator across Colony, ugig, and Taskmarket. This audit does not decide whether any later submitter was paid before.",
        "",
        f"The public ugig bounty index at the same read listed `{acceptance['ugigIndexTotal']}` open rows and `q78Listed` `{str(acceptance['ugigQ78Listed']).lower()}`. That index has no closed-bounty history. {acceptance['note']}",
        "",
        "## Day boundaries",
        "",
        "Blocks are the first and last whose timestamps fall in that half-open interval. NodeReal and `bsc-dataseed.bnbchain.org` returned the same four hashes.",
        "",
        table(
            ["Edge", "Block", "Timestamp", "COT", "Hash"],
            [
                ["Previous", bounds["previousBlock"], headers[str(bounds["previousBlock"])]["timestamp"], cot_iso(headers[str(bounds["previousBlock"])]["timestamp"]), headers[str(bounds["previousBlock"])]["hash"]],
                ["First", bounds["firstBlock"], headers[str(bounds["firstBlock"])]["timestamp"], cot_iso(headers[str(bounds["firstBlock"])]["timestamp"]), headers[str(bounds["firstBlock"])]["hash"]],
                ["Last", bounds["lastBlock"], headers[str(bounds["lastBlock"])]["timestamp"], cot_iso(headers[str(bounds["lastBlock"])]["timestamp"]), headers[str(bounds["lastBlock"])]["hash"]],
                ["Next", bounds["nextBlock"], headers[str(bounds["nextBlock"])]["timestamp"], cot_iso(headers[str(bounds["nextBlock"])]["timestamp"]), headers[str(bounds["nextBlock"])]["hash"]],
            ],
        ),
        "",
        f"Pin used for funder end-state: block `{summary['pin']['number']}`, hash `{summary['pin']['hash']}`, unix `{summary['pin']['timestamp']}`, COT `{cot_iso(summary['pin']['timestamp'])}`. Absence means no BNB balance and nonce 0 at this pin. A later credit is outside this capture.",
        "",
        "## Outflows",
        "",
        f"External transfers: **{summary['counts']['externalOutflows']}**. Distinct recipients: **{summary['counts']['distinctRecipients']}**. Total sent: **{summary['totals']['externalOut']} FLAPJAX** (`{summary['totals']['externalOutAtoms']}` base units). Self-transfers: {summary['counts']['selfTransfers']}.",
        "",
        f"Treasury token balance moved from {summary['totals']['treasuryBefore']} at block {bounds['previousBlock']} to {summary['totals']['treasuryAfter']} at block {bounds['lastBlock']}. Inflow logs in the same day: {summary['counts']['inflowLogs']}, {summary['totals']['in']} FLAPJAX (`{summary['totals']['inAtoms']}` base units). {summary['reconciliation']}.",
        "",
        table(
            ["COT", "Block", "Recipient", "Amount", "Mechanism", "Transaction"],
            [[row["cot"], row["block"], link_addr(row["to"]), row["amount"], row["mechanism"], link_tx(row["tx"])] for row in summary["outflows"]],
        ),
        "",
        "A normal transfer call is `transfer(address,uint256)` sent to the token. A contract-mediated row is still a Transfer log from the treasury; the outer transaction called some other account. Both count. Amounts are the log amounts, in 18 decimal places.",
        "",
        "### Same-day inflows used for the balance check",
        "",
        table(
            ["COT", "Block", "From", "Amount", "Mechanism", "Transaction"],
            [[row["cot"], row["block"], link_addr(row["from"]), row["amount"], row["mechanism"], link_tx(row["tx"])] for row in summary["inflows"]],
        ),
        "",
        "## First BNB funder",
        "",
        "For each recipient, and for the treasury, the search uses end-of-block balance and nonce through the pin. Empty code, nonce 0, and balance 0 at the pin is recorded as absent: an ordinary account cannot spend BNB without increasing its nonce. Nonempty code is recorded as incomplete, because a contract can receive and forward inside one transaction and end at zero. The first funder is the immediate account that sent the BNB value. On an internal transfer, that account can differ from the transaction signer.",
        "",
        "A shared first funder is one evidence group. The group does not prove that one operator controls the wallets. Recipients with absent or incomplete history stay outside the groups.",
        "",
        table(
            ["Role", "Address", "Coverage", "First funder", "Category", "BNB", "Funder block", "Funder transaction"],
            [[
                row["role"],
                link_addr(row["address"]),
                row["coverage"],
                link_addr(row["funder"]) if row.get("funder") else "",
                row.get("category") or "",
                bnb_cell(row),
                row.get("funderBlock") or "",
                link_tx(row["funderTx"]) if row.get("funderTx") else "",
            ] for row in summary["funders"]],
        ),
        "",
        f"Evidence-defined recipient groups: **{groups['evidenceGroupCount']}**. Unfunded recipients: {len(groups['unfundedRecipients'])}. Incomplete funder histories: {len(groups['incompleteRecipients'])}. Real operator count: unknown (`realOperatorCount` is null). The task asks how many distinct operators the groups imply. These observations do not supply that number.",
        "",
        f"The treasury's own first funder is `{groups['treasuryFirstFunder']}`. `sharesTreasuryFirstFunder` is true only when a recipient group has that same funder. `funderIsTreasury` is true when the treasury address itself is the recipient's first funder.",
        "",
        groups["operatorNote"],
        "",
    ]
    if after_day:
        lines.append(
            "First BNB credit after the last block of 10-28 COT, and before the pin: "
            + ", ".join(f"{link_addr(row['address'])} at block {row['funderBlock']}" for row in after_day)
            + "."
        )
        lines.append("")
    if groups["evidenceGroups"]:
        lines.append(table(
            ["Funder", "Recipients", "Linking transactions", "Funder is treasury", "Same funder as treasury"],
            [[
                link_addr(group["funder"]),
                " ".join(link_addr(item) for item in group["recipients"]),
                " ".join(link_tx(item) for item in group["linkingTransactions"]),
                group["funderIsTreasury"],
                group["sharesTreasuryFirstFunder"],
            ] for group in groups["evidenceGroups"]],
        ))
        lines.append("")
    if groups["unfundedRecipients"]:
        lines.append("No observed first BNB funder, empty code through the pin: " + ", ".join(link_addr(item) for item in groups["unfundedRecipients"]) + ".")
        lines.append("")
    if groups["incompleteRecipients"]:
        lines.append("Funder history incomplete, so these recipients are not placed in a group: " + ", ".join(link_addr(item) for item in groups["incompleteRecipients"]) + ".")
        lines.append("")
    lines.extend([
        "## Unexplained transfers",
        "",
        "None." if not summary["unexplainedTransfers"] else "\n".join(link_tx(item) for item in summary["unexplainedTransfers"]),
        "",
        "An explained token transfer can still have an unknown operator. An absent BNB row is a finished end-state read. An incomplete row would be an unfinished scan and is listed separately above.",
        "",
        "## Coverage and limits",
        "",
        f"Primary route: `{PRIMARY}`. `eth_getLogs` was read in two full partitions, 50000-block and 25000-block steps, for treasury sends and treasury receipts. A page of 1000 logs is rejected as a possible cap. The token-transfer index `nr_getAssetTransfers` (category 20, 90000-block steps, 100000-block provider cap) matches the outflow multiset, including any self-transfer.",
        "",
        "Normal BNB transfers are top-level transactions in the first activity block with `to` equal to the address and positive value, status 1. Internal BNB transfers are used only when that index's external set matches those top-level transfers and a `callTracer` trace confirms the credit. Category `external` in the funder table is a normal transfer. Category `internal` is a value call inside a transaction. If the earliest normal transfer is not at transaction index 0 and the internal index is incomplete, the row stays incomplete.",
        "",
        "The treasury balance at block 1 is 0, so the balance method reached archive state. The funder search stops at the pin above.",
        "",
        f"Secondary route `{SECONDARY}` supplied chain id, the four boundary headers, and one outflow receipt. It is a hash check, not the log index.",
        "",
        f"`https://bsc.publicnode.com` answered `{limits['publicnodeLogQueries']}` outflow `eth_getLogs` queries: `{limits['publicnodeEmptyResults']}` empty, `{limits['publicnodeNonemptyResults']}` nonempty, `{limits['publicnodeErrors']}` errors. `publicnodeUsedAsHistory` is `{str(limits['publicnodeUsedAsHistory']).lower()}`. Empty responses are a missing index on that route.",
        "",
        "Etherscan API v2 refused free BSC coverage. Routescan returned chain-not-supported. The old bscscan v1 host returned an HTML migration page. Blockscout's BSC host returned HTTP 404. Each failed route is recorded in [capture-stats.json](evidence/capture-stats.json) and [predicate.json](evidence/predicate.json).",
        "",
        "Replay, from this directory, with no installs:",
        "",
        "```sh",
        "python3 audit.py",
        "python3 independent.py",
        "python3 render.py",
        "python3 -m unittest test_audit.py -v",
        "python3 verify.py",
        "```",
        "",
        "`audit.py`, `independent.py`, `render.py`, and `test_audit.py` stay offline. `test_audit.py` uses synthetic rows and does not reread this capture. `verify.py` repeats the offline checks and reads one saved outflow receipt plus the first boundary header from `bsc-dataseed.bnbchain.org`. `collect.py` is the only writer of `evidence/`. Running it again adds a new capture and needs a new review.",
        "",
    ])
    return "\n".join(lines)


def main():
    summary = json.loads((HERE / "derived" / "summary.json").read_text())
    text = render(summary)
    (HERE / "PUBLIC-AUDIT.md").write_text(text)
    print("wrote PUBLIC-AUDIT.md", len(text))


if __name__ == "__main__":
    main()
