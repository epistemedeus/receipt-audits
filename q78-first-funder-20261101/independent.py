#!/usr/bin/env python3
"""Second total check. Reads the CSV text, not the audit objects."""
import csv
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent


def atoms_from_text(text):
    whole, frac = text.split(".")
    if len(frac) != 18 or not frac.isdigit() or not whole.isdigit():
        raise SystemExit("amount is not an 18-decimal field: " + text)
    return int(whole) * 10**18 + int(frac)


def main():
    derived = HERE / "derived"
    total = 0
    recipients = set()
    seen = set()
    with (derived / "outflows.csv").open() as handle:
        for row in csv.DictReader(handle):
            key = (row["tx"], row["logIndex"])
            if key in seen:
                raise SystemExit("duplicate outflow row")
            seen.add(key)
            parsed = atoms_from_text(row["amount"])
            if parsed != int(row["atoms"]):
                raise SystemExit("amount text does not match atoms")
            total += int(row["atoms"])
            recipients.add(row["to"])
    summary = json.loads((derived / "summary.json").read_text())
    if str(total) != summary["totals"]["externalOutAtoms"]:
        raise SystemExit("csv total does not match summary")
    if len(recipients) != summary["counts"]["distinctRecipients"]:
        raise SystemExit("recipient count does not match summary")
    if len(seen) != summary["counts"]["externalOutflows"]:
        raise SystemExit("row count does not match summary")
    print(json.dumps({"rows": len(seen), "recipients": len(recipients), "atoms": str(total)}))


if __name__ == "__main__":
    main()
