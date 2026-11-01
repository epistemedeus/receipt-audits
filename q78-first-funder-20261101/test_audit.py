#!/usr/bin/env python3
"""Fixture checks. These rows are synthetic and are not the October 28 capture."""
import unittest

from audit import (
    TREASURY,
    AuditError,
    bind_window,
    chunk_ranges,
    coverage_label,
    decide_funder,
    group_recipients,
    route_limits,
    in_window,
    parse_units,
    reconcile_partitions,
    select_first_credit,
    units,
)

DESCRIPTION = (
    "treasury 0x7C34E9e21eE28A49Ff0b84B61774119E6633359f token "
    "0x90c8889f428F9Ebb77BB8f15CAD3a50a9aC680df during 10-28 COT (UTC-5). "
    "first sent it BNB. One new receipt per claim. Up to 2 answers accepted."
)


def credit(block, tx_index, order, value, status=1, category="external", frm="0x" + "a" * 40, tx="0x" + "b" * 64):
    return {
        "block": block,
        "txIndex": tx_index,
        "order": order,
        "value": value,
        "status": status,
        "from": frm,
        "to": "0x" + "c" * 40,
        "tx": tx,
        "category": category,
    }


class SyntheticAudit(unittest.TestCase):
    def test_eighteen_decimals_round_trip(self):
        atoms = 2480000 * 10**18 + 1
        text = units(atoms)
        self.assertEqual(text, "2480000.000000000000000001")
        self.assertEqual(parse_units(text), atoms)
        self.assertEqual(units(0), "0.000000000000000000")

    def test_window_binds_2026_and_rejects_a_changed_task(self):
        window = bind_window("2026-10-29T14:29:16.673Z", DESCRIPTION)
        self.assertEqual(window["startUnix"], 1793163600)
        self.assertEqual(window["endUnixExclusive"], 1793250000)
        self.assertTrue(in_window(window["startUnix"], window))
        self.assertFalse(in_window(window["endUnixExclusive"], window))
        self.assertFalse(in_window(window["startUnix"] - 1, window))
        with self.assertRaises(AuditError):
            bind_window("2025-10-29T00:00:00Z", DESCRIPTION)
        with self.assertRaises(AuditError):
            bind_window("2026-10-29T00:00:00Z", DESCRIPTION.replace("One new receipt per claim", "changed"))

    def test_chunks_cover_the_day_without_overlap(self):
        first, last = 130221520, 130413457
        for step in (50000, 25000):
            ranges = chunk_ranges(first, last, step)
            self.assertEqual(ranges[0][0], first)
            self.assertEqual(ranges[-1][1], last)
            for (a, b), (c, d) in zip(ranges, ranges[1:]):
                self.assertEqual(b + 1, c)
                self.assertLessEqual(b - a + 1, step)

    def test_duplicate_and_disagreement_fail(self):
        def row(atoms):
            return {"block": 1, "blockHash": "0x" + "a" * 64, "tx": "0x" + "b" * 64, "logIndex": 0, "from": TREASURY, "to": "0x" + "c" * 40, "atoms": atoms}
        with self.assertRaises(AuditError):
            reconcile_partitions([row(5)], [row(5), row(5)])
        with self.assertRaises(AuditError):
            reconcile_partitions([row(5)], [row(6)])

    def test_credit_order_ignores_failed_and_zero(self):
        chosen = select_first_credit([
            credit(9, 1, 0, 0),
            credit(9, 1, 0, 5, status=0),
            credit(8, 4, 1, 2, frm="0x" + "d" * 40, tx="0x" + "e" * 64),
            credit(8, 3, 0, 9, frm="0x" + "1" * 40, tx="0x" + "2" * 64),
        ])
        self.assertEqual(chosen["tx"], "0x" + "2" * 64)

    def test_missing_internal_history_is_not_absence(self):
        normal = credit(4, 3, 0, 10, frm="0x" + "1" * 40, tx="0x" + "2" * 64)
        coverage, chosen, note = decide_funder([normal], [], False)
        self.assertEqual(coverage, "incomplete")
        self.assertIsNone(chosen)
        self.assertIn("internal", note)
        coverage, chosen, _note = decide_funder([dict(normal, txIndex=0)], [], False)
        self.assertEqual(coverage, "observed")
        self.assertEqual(chosen["from"], "0x" + "1" * 40)

    def test_shared_funder_is_not_proved_control(self):
        shared = "0x" + "a" * 40
        other = "0x" + "b" * 40
        rows = [
            {"role": "treasury", "address": TREASURY, "funder": other, "coverage": "observed"},
            {"role": "recipient", "address": "0x" + "1" * 40, "funder": shared, "funderTx": "0x" + "8" * 64, "coverage": "observed"},
            {"role": "recipient", "address": "0x" + "2" * 40, "funder": shared, "funderTx": "0x" + "9" * 64, "coverage": "observed"},
            {"role": "recipient", "address": "0x" + "3" * 40, "funder": TREASURY, "funderTx": "0x" + "7" * 64, "coverage": "observed"},
            {"role": "recipient", "address": "0x" + "4" * 40, "funder": None, "coverage": "absent"},
            {"role": "recipient", "address": "0x" + "5" * 40, "funder": None, "coverage": "incomplete"},
        ]
        grouped = group_recipients(rows)
        self.assertEqual(grouped["evidenceGroupCount"], 2)
        self.assertIsNone(grouped["realOperatorCount"])
        self.assertEqual(grouped["unfundedRecipients"], ["0x" + "4" * 40])
        self.assertEqual(grouped["incompleteRecipients"], ["0x" + "5" * 40])
        by = {group["funder"]: group for group in grouped["evidenceGroups"]}
        self.assertEqual(by[shared]["recipients"], ["0x" + "1" * 40, "0x" + "2" * 40])
        self.assertFalse(by[shared]["operatorControlProved"])
        self.assertTrue(by[TREASURY]["funderIsTreasury"])
        self.assertFalse(any(group["operatorControlProved"] for group in grouped["evidenceGroups"]))

    def test_internal_credit_beats_a_later_normal(self):
        normal = credit(5, 4, 0, 1, frm="0x" + "1" * 40, tx="0x" + "2" * 64)
        internal = credit(5, 1, 2, 7, frm="0x" + "e" * 40, tx="0x" + "f" * 64, category="internal")
        coverage, chosen, _note = decide_funder([normal], [internal], True)
        self.assertEqual(coverage, "observed")
        self.assertEqual(chosen["category"], "internal")
        self.assertEqual(chosen["from"], "0x" + "e" * 40)

    def test_absence_and_incomplete_labels_stay_distinct(self):
        self.assertEqual(coverage_label(0, 0, 0, [], True), "absent")
        self.assertEqual(coverage_label(0, 0, 1, [], True), "incomplete")
        self.assertEqual(coverage_label(0, 0, 0, [], False), "incomplete")

    def test_empty_third_route_is_not_history(self):
        limits = route_limits([
            {"url": "https://bsc.publicnode.com", "status": 200, "request": {"method": "eth_getLogs"}, "response": {"result": []}},
            {"url": "https://bsc.publicnode.com", "status": 200, "request": {"method": "eth_getLogs"}, "response": {"result": [{"address": "0x1"}]}},
            {"url": "https://bsc.publicnode.com", "status": 429, "request": {"method": "eth_getLogs"}, "response": {}},
            {"url": "https://bsc-dataseed.bnbchain.org", "status": 200, "request": {"method": "eth_getLogs"}, "response": {"result": []}},
        ])
        self.assertEqual(limits["publicnodeLogQueries"], 3)
        self.assertEqual(limits["publicnodeEmptyResults"], 1)
        self.assertEqual(limits["publicnodeNonemptyResults"], 1)
        self.assertEqual(limits["publicnodeErrors"], 1)
        self.assertFalse(limits["publicnodeUsedAsHistory"])


if __name__ == "__main__":
    unittest.main()
