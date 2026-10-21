#!/usr/bin/env python3
"""Focused real-capture refusal/recovery plus hand-calculated arithmetic controls."""
import copy
from fractions import Fraction
import json
import pathlib
import tempfile
import unittest
from unittest.mock import patch
import audit

HERE=pathlib.Path(__file__).resolve().parent
class AuditTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.original=audit.load_capture(HERE/'evidence/rpc.jsonl')
    def sample(self):return copy.deepcopy(self.original)
    def rejected(self,mutate,pattern):
        d=self.sample();mutate(d)
        with self.assertRaisesRegex((ValueError,KeyError,TypeError),pattern):audit.analyse(d)
        # Recovery always reuses the unchanged saved evidence, without another RPC.
        self.assertGreater(audit.analyse(self.original)['totals']['buys'],0)
    def test_exact_arithmetic_hand_controls(self):
        self.assertEqual(audit.units(1000000000000000001),'1.000000000000000001')
        self.assertEqual(audit.units(-1),'-0.000000000000000001')
        p=audit.price(3*10**16,2*10**18)
        self.assertEqual(Fraction(int(p['numerator']),int(p['denominator'])),Fraction(3,200))
        self.assertEqual(audit.signed((1<<256)-7),-7)
        # Independent conversion of the first receipt's raw hex, including its low digits.
        self.assertEqual(int('13e56b7d07d20d725a6618',16),24052995308271524768278040)
    def test_real_cold_journal_and_evidence(self):
        with patch('socket.socket',side_effect=AssertionError('network forbidden in cold replay')):
            s=audit.analyse(self.original)
            self.assertGreater(audit.verify_journal(self.original,HERE/'evidence/rpc.jsonl'),0)
        self.assertEqual(sum(int(b['FJ_atoms']) for b in s['buys']),int(s['totals']['FJ_atoms']))
        self.assertEqual(s['verdicts']['October23_makeup'],'UNKNOWN (future promise)')
    def test_wrong_network_asset_pool_and_event(self):
        mutations=[(lambda d:d.update(chainId=1),'network'),(lambda d:d['metadata'].update(token0='0x'+'0'*64),'token0'),(lambda d:d['metadata'].update(factoryPool='0x'+'0'*64),'factory pool'),(lambda d:d['metadata'][audit.FJ].update(decimals='0x6'),'decimals'),(lambda d:d['metadata']['eventTopics'].update(Swap='0xc420'),'event topics'),(lambda d:d['scans']['pool']['50000']['logs'][0].update(address=audit.FJ),'issuer')]
        for mutate,pattern in mutations:
            with self.subTest(pattern=pattern):self.rejected(mutate,pattern)
    def test_duplicate_log(self):
        def mutate(d):
            p=d['scans']['token']['50000'];l=p['logs'][0];p['logs'].append(copy.deepcopy(l))
            for r in p['ranges']:
                if r[0]<=audit.n(l['blockNumber'])<=r[1]:r[2]+=1
        self.rejected(mutate,'duplicate')
    def test_missing_log_partition(self):
        def mutate(d):
            p=d['scans']['token']['25000'];l=p['logs'].pop(0)
            for r in p['ranges']:
                if r[0]<=audit.n(l['blockNumber'])<=r[1]:r[2]-=1
        self.rejected(mutate,'partition mismatch')
    def test_truncated_or_gapped_ranges(self):
        for mutate in [lambda d:d['scans']['pool']['50000']['ranges'].pop(),lambda d:d['scans']['token']['25000']['ranges'][1].__setitem__(0,d['scans']['token']['25000']['ranges'][1][0]+1)]:
            self.rejected(mutate,'range')
    def test_failed_receipt_and_absent_receipt(self):
        h=next(iter(self.original['receipts']))
        self.rejected(lambda d:d['receipts'][h].update(status='0x0'),'receipt failed')
        self.rejected(lambda d:d['receipts'].pop(h),'absent transaction/receipt')
    def test_independent_route_disagreement(self):
        h=next(iter(self.original['secondaryReads']))
        self.rejected(lambda d:d['secondaryReads'][h]['receipt'].update(blockHash='0x'+'0'*64),'independent receipt')
    def test_bad_utc_boundary(self):
        key='2026-10-09T00:00:00Z'
        self.rejected(lambda d:d['boundaries'].update({key:d['boundaries'][key]+1}),'UTC boundary')
    def test_silent_both_partition_omission_is_caught_by_journal(self):
        d=self.sample();l=d['scans']['token']['50000']['logs'][0]
        for p in d['scans']['token'].values():
            p['logs']=[x for x in p['logs'] if audit.log_id(x)!=audit.log_id(l)]
            for r in p['ranges']:
                if r[0]<=audit.n(l['blockNumber'])<=r[1]:r[2]-=1
        with self.assertRaisesRegex(ValueError,'journal evidence'):
            audit.verify_journal(d,HERE/'evidence/rpc.jsonl')
    def test_absent_rpc_record(self):
        lines=(HERE/'evidence/rpc.jsonl').read_text().splitlines()
        with tempfile.TemporaryDirectory() as tmp:
            p=pathlib.Path(tmp)/'rpc.jsonl';p.write_text('\n'.join(l for l in lines if json.loads(l)['request']['method']!='eth_getTransactionReceipt')+'\n')
            with self.assertRaisesRegex(ValueError,'journal evidence'):
                audit.verify_journal(self.original,p)

if __name__=='__main__':unittest.main(verbosity=2)
