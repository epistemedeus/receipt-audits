import copy
import json
from pathlib import Path
import socket
import unittest
from unittest.mock import patch
import q33
from sources import ledger
HERE=Path(__file__).resolve().parent
class Q33Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records=[json.loads(l) for l in (HERE/'evidence/rpc.jsonl').read_text().splitlines()]
        cls.old=q33.load_capture(HERE/'q35-reuse/evidence/rpc.jsonl')
        cls.result=q33.analyse(old=cls.old,records=cls.records)
    def analyse(self,records):return q33.analyse(old=self.old,records=records)
    def rejected(self,mutate,pattern):
        r=copy.deepcopy(self.records);mutate(r)
        with self.assertRaisesRegex((ValueError,KeyError,TypeError),pattern):self.analyse(r)
        self.assertEqual(self.analyse(self.records)['holderIndex']['gapAtoms'],'0')
    def test_real_cold_reproduction(self):
        with patch('socket.socket',side_effect=AssertionError('offline replay attempted network')):
            s=self.analyse(self.records)
        self.assertEqual(sum(int(h['atoms']) for h in s['holders']),int(s['token']['supplyAtoms']))
        self.assertEqual(s,self.result)
    def test_supply_gap_is_not_complete(self):
        def m(r):
            x=next(x for x in r if x['request']['method']=='nr_getTokenHolders' and 'result' in x['response']);x['response']['result']['details'].pop()
        self.rejected(m,'balance/supply gap')
    def test_duplicate_holder_is_rejected(self):
        def m(r):
            x=next(x for x in r if x['request']['method']=='nr_getTokenHolders' and 'result' in x['response']);x['response']['result']['details'][1]=copy.deepcopy(x['response']['result']['details'][0])
        self.rejected(m,'duplicate holder')
    def test_missing_terminal_page_is_unavailable(self):
        self.rejected(lambda r:r.__setitem__(slice(None),[x for x in r if not (x['request']['method']=='nr_getTokenHolders' and x['request']['params'][2] and 'result' in x['response'] and not x['response']['result'].get('pageKey'))]),'absent saved source')
    def test_missing_balance_never_becomes_zero(self):
        a=self.result['holders'][-1]['address'];data='0x70a08231'+a[2:].rjust(64,'0')
        self.rejected(lambda r:r.__setitem__(slice(None),[x for x in r if not (x['request']['method']=='eth_call' and x['request']['params'][0]['data']==data)]),'absent saved source')
    def test_missing_extension_query(self):
        def m(r):
            for i,x in enumerate(r):
                if x['request']['method']=='eth_getLogs' and 'result' in x['response']:r.pop(i);return
        self.rejected(m,'absent saved source')
    def test_duplicate_extension_log(self):
        def m(r):
            x=next(x for x in r if x['request']['method']=='eth_getLogs' and x['response'].get('result'));x['response']['result'].append(copy.deepcopy(x['response']['result'][0]))
        self.rejected(m,'duplicate log')
    def test_truncated_partition(self):
        def m(r):
            x=next(x for x in r if x['request']['method']=='eth_getLogs' and x['response'].get('result'));x['response']['result'].pop()
        self.rejected(m,'partition mismatch')
    def test_wrong_chain_and_decimals(self):
        for method in ('eth_chainId','eth_call'):
            def m(r):
                x=next(x for x in r if x['request']['method']==method and (method=='eth_chainId' or x['request']['params'][0]['data']=='0x313ce567') and 'result' in x['response']);x['response']['result']='0x1'
            self.rejected(m,'wrong chain|decimals')
    def test_conflicting_repeat_rpc(self):
        def m(r):
            x=copy.deepcopy(next(x for x in r if x['request']['method']=='eth_chainId'));x['response']['result']='0x1';r.append(x)
        self.rejected(m,'contradictory')
    def test_receipt_failure(self):
        def m(r):
            x=next(x for x in r if x['request']['method']=='eth_getTransactionReceipt' and x['url']==q33.PRIMARY and 'result' in x['response']);x['response']['result']['status']='0x0'
        self.rejected(m,'failed or mismatched')
    def test_retention_exact_aggregation_and_fungibility(self):
        p=[{'to':'a','atoms':'7'},{'to':'a','atoms':'3'},{'to':'b','atoms':'5'}]
        s=q33.retention(p,{'a':10,'b':4});self.assertEqual((s['recipients'],s['retained']),(2,1))
        # No assertion that the same units were never transferred: replenishment
        # remains compatible with balance >= cumulative payouts.
        self.assertTrue(s['rows'][0]['holdsAtLeastPayout'])
        with self.assertRaisesRegex(ValueError,'unavailable'):q33.retention(p,{'a':10})
    def test_zero_mint_burn_self_transfer_and_integers(self):
        a='0x'+'1'*40;b='0x'+'2'*40
        def log(src,dst,v,i):return {'address':q33.FJ,'topics':[q33.TRANSFER,'0x'+src[2:].rjust(64,'0'),'0x'+dst[2:].rjust(64,'0')],'data':'0x'+hex(v)[2:].rjust(64,'0'),'blockNumber':'0x1','transactionIndex':'0x0','logIndex':hex(i),'blockHash':'0x'+'3'*64,'transactionHash':'0x'+'4'*64}
        logs=[log(q33.ZERO,a,100,0),log(a,b,40,1),log(b,q33.ZERO,10,2),log(b,b,5,3),log(a,b,0,4)]
        balances,mint,burn=q33.reduce_transfers(logs);self.assertEqual((balances[a],balances[b],mint,burn),(60,30,100,10));self.assertNotIn(q33.ZERO,balances)
        self.assertEqual(q33.units(10**18+1),'1.000000000000000001')
        self.assertEqual(q33.fraction(1,3)['numerator'],'100');self.assertEqual(q33.fraction(1,3)['denominator'],'3')
    def test_ties_have_stable_address_order(self):self.assertEqual(q33.ranking({'b':7,'a':7,'c':0}),[('a',7),('b',7)])
    def test_classification_uses_runtime_and_factory(self):
        for h in self.result['top10']:
            if h['runtimeBytes']==0:self.assertNotIn('pool',h['role'])
            if 'factory-bound' in h['role']:self.assertGreater(h['runtimeBytes'],0);self.assertIn('factory ',h['role'])
        self.assertTrue(any(h['runtimeBytes']>0 and 'Sourcify-verified Vault' in h['role'] for h in self.result['top10']))
    def test_ledger_uses_actual_receipt_labels(self):
        rows=ledger((HERE/'evidence/flapjax.html').read_text());self.assertTrue(rows)
        self.assertTrue(any('withheld' in r['displayAmount'] for r in rows))
        with self.assertRaisesRegex(ValueError,'missing public ledger'):ledger('<html></html>')
        self.assertGreaterEqual(self.result['retentionAllOutflows']['payouts'],self.result['retentionQuickTaskLabels']['payouts'])
        self.assertGreaterEqual(self.result['retentionQuickTaskLabels']['payouts'],self.result['retentionQ21to32']['payouts'])
        nested=next(r for r in rows if r['tx']=='0x0dd0de5c542d7ce26a716bd93df10ebcdc21898258596b03ff2f31e8b325c462')
        self.assertEqual((nested['date'],nested['label']),('2026-10-14','custom TSK-9NYE79E0'))
    def test_missing_independent_payout_receipt(self):
        h=self.result['ledgerDatedQuickPayouts'][0]['tx']
        self.rejected(lambda r:r.__setitem__(slice(None),[x for x in r if not (x['url']==q33.SECONDARY and x['request']['method']=='eth_getTransactionReceipt' and x['request']['params']==[h])]),'absent saved source')
    def test_missing_counterexample_receipt(self):
        h=self.result['counterexample']['tx']
        self.rejected(lambda r:r.__setitem__(slice(None),[x for x in r if not (x['url']==q33.SECONDARY and x['request']['method']=='eth_getTransactionReceipt' and x['request']['params']==[h])]),'absent saved source')
    def test_vault_source_must_match_runtime(self):
        a='0x238a358808379702088667322f80ac48bad5e6c4'
        def m(r):
            x=next(x for x in r if x['url']==q33.PRIMARY and x['request']['method']=='eth_getCode' and x['request']['params'][0]==a and 'result' in x['response']);x['response']['result']='0x01'
        self.rejected(m,'verified runtime differs')
    def test_nonzero_opening_treasury_is_not_omitted(self):
        self.assertGreater(int(self.result['treasury']['openingAtoms']),0)
        self.assertEqual(self.result['treasury']['conservationGapAtoms'],'0')
    def test_unavailable_independent_state_is_explicit(self):
        self.assertTrue(self.result['independentStateChecks'])
        self.assertFalse(any(x['independentResultAvailable'] for x in self.result['independentStateChecks']))
if __name__=='__main__':unittest.main(verbosity=2)
