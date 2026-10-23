import copy,json,unittest
import q41 as a
class Q41Tests(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.rows=a.records();cls.result=a.analyse(cls.rows);cls.task=json.loads((a.HERE/'evidence/task-current.json').read_text());cls.linked=(a.HERE/'evidence/colony-linked.txt').read_text()
 def run_rows(self,rows):return a.analyse(rows,verify_old=False)
 def alter(self,predicate,change):
  rows=copy.deepcopy(self.rows)
  for r in rows:
   if predicate(r):change(r)
  return rows
 def rejects(self,rows):
  with self.assertRaises(ValueError):self.run_rows(rows)
 def test_real_atomic_controls(self):
  s=self.result
  self.assertEqual(s['totals']['WBNB_atoms'],'120000000000000000')
  self.assertEqual(s['totals']['FJ_atoms'],'284418120150881746565276184')
  self.assertEqual(s['totals']['gasAtoms'],'76458500000000')
  self.assertEqual(s['totals']['programDaysAudited'],13)
  self.assertEqual(s['missedDays'],['2026-10-15'])
  self.assertEqual(s['buys'][5]['FJ_atoms'],'23691113109537150143912753')
  self.assertEqual(min(int(b['postTransactionBalanceAtoms']) for b in s['buys']),36158610033772485)
 def test_integer_formulas(self):
  self.assertEqual(a.units(1230000000000000001),'1.230000000000000001')
  self.assertEqual(a.rational(2**192,2**192)['decimal'],'1.000000000000000000E+0')
  self.assertEqual(a.atomic('0.025'),25000000000000000)
  with self.assertRaises(ValueError):a.atomic('0.0000000000000000001')
 def test_exact_calendar_edges(self):
  t=a.timestamp(a.START);e=a.timestamp(a.END)
  self.assertFalse(a.selected(t-1));self.assertTrue(a.selected(t));self.assertTrue(a.selected(e-1));self.assertFalse(a.selected(e))
  self.assertEqual(a.cot(t),'2026-10-09T00:00:00-05:00')
  self.assertEqual(a.cot(a.timestamp('2026-10-17T02:00:51Z'))[:10],'2026-10-16')
 def test_wrong_network(self):
  self.rejects(self.alter(lambda r:r['request']['method']=='eth_chainId',lambda r:r['response'].update(result='0x2105')))
 def test_wrong_token_order_and_decimals(self):
  for selector,value in [('0x0dfe1681','0x'+'0'*24+a.WBNB[2:]),('0x313ce567','0x6')]:
   self.rejects(self.alter(lambda r:r['request']['method']=='eth_call' and r['request']['params'][0]['data']==selector,lambda r:r['response'].update(result=value)))
 def test_wrong_pool_issuer(self):
  rows=copy.deepcopy(self.rows)
  for r in rows:
   if r['request']['method']=='eth_getLogs' and r['request']['params'][0]['address']==a.POOL and r['response'].get('result'):
    r['response']['result'][0]['address']=a.FJ;break
  self.rejects(rows)
 def test_duplicate_log(self):
  rows=copy.deepcopy(self.rows)
  for r in rows:
   if r['request']['method']=='eth_getLogs' and r['response'].get('result'):
    r['response']['result'].append(copy.deepcopy(r['response']['result'][0]));break
  self.rejects(rows)
 def test_missing_log_partition(self):
  rows=copy.deepcopy(self.rows)
  for r in rows:
   if r['request']['method']=='eth_getLogs' and r['response'].get('result'):
    r['response']['result'].pop();break
  self.rejects(rows)
 def test_both_partition_pool_omission_hits_receipt(self):
  h=self.result['buys'][-1]['tx']
  rows=self.alter(lambda r:r['request']['method']=='eth_getLogs' and r['request']['params'][0]['address']==a.POOL and isinstance(r['response'].get('result'),list),lambda r:r['response'].update(result=[l for l in r['response']['result'] if l['transactionHash']!=h]))
  self.rejects(rows)
 def test_missing_range(self):
  rows=[r for r in self.rows if not (r['request']['method']=='eth_getLogs' and r['request']['params'][0]['fromBlock']==hex(128867610))]
  self.rejects(rows)
 def test_range_cap(self):
  rows=copy.deepcopy(self.rows)
  for r in rows:
   if r['request']['method']=='eth_getLogs' and r['response'].get('result'):
    r['response']['result']=[r['response']['result'][0]]*1000;break
  self.rejects(rows)
 def test_failed_or_absent_receipt(self):
  h=self.result['buys'][-1]['tx']
  self.rejects(self.alter(lambda r:r['request']['method']=='eth_getTransactionReceipt' and r['request']['params']==[h],lambda r:r['response']['result'].update(status='0x0')))
  self.rejects([r for r in self.rows if not(r['request']['method']=='eth_getTransactionReceipt' and r['request']['params']==[h])])
 def test_missing_secondary(self):
  h=self.result['buys'][-1]['tx']
  self.rejects([r for r in self.rows if not(r['url']==a.SECONDARY and r['request']['method']=='eth_getTransactionReceipt' and r['request']['params']==[h])])
 def test_bad_boundary(self):
  b=self.result['window']['firstBlock']
  rows=self.alter(lambda r:r['url']==a.PRIMARY and r['request']['method']=='eth_getBlockByNumber' and r['request']['params']==[hex(b),False],lambda r:r['response']['result'].update(timestamp=hex(a.timestamp(a.START)-1)))
  self.rejects(rows)
 def test_absent_historical_state_is_unknown(self):
  h=self.result['buys'][-1]['tx'];bn=self.result['buys'][-1]['block']
  rows=[r for r in self.rows if not ((r['request']['method']=='debug_traceTransaction' and r['request']['params']==[h,a.TRACE]) or (r['request']['method']=='eth_call' and r['request']['params']==[{'to':a.POOL,'data':'0x3850c7bd'},hex(bn-1)]))]
  s=self.run_rows(rows)
  self.assertEqual(s['verdicts']['skip_if_under_floor'],'UNKNOWN');self.assertIsNone(s['buys'][-1]['blockBeforePrice']);self.assertEqual(s['totals']['buys'],12)
 def test_changed_rule_requires_new_verdict(self):
  t=copy.deepcopy(self.task);text=self.linked.replace('under 0.025 BNB','under 0.04 BNB');t['description']=t['description'].replace('under 0.025 BNB','under 0.04 BNB')
  s=a.analyse(self.rows,task=t,linked=text,verify_old=False);self.assertEqual(s['verdicts']['skip_if_under_floor'],'BROKEN')
  t=copy.deepcopy(self.task);t['description']=t['description'].replace('each buy spends 0.01 BNB','each buy spends 0.02 BNB')
  s=a.analyse(self.rows,task=t,linked=self.linked.replace('each buy spends 0.01 BNB','each buy spends 0.02 BNB'),verify_old=False);self.assertEqual(s['verdicts']['each_buy_0_01_BNB'],'BROKEN')
 def test_conflicting_task_rules(self):
  t=copy.deepcopy(self.task);t['description']=t['description'].replace('under 0.025 BNB','under 0.04 BNB')
  with self.assertRaises(ValueError):a.analyse(self.rows,task=t,verify_old=False)
 def test_changed_rule_wording(self):
  with self.assertRaises(ValueError):a.rules(self.task['description'].replace('counted in COT','counted in UTC'))
 def test_prestate_wrong_nonce(self):
  h=self.result['buys'][-1]['tx']
  self.rejects(self.alter(lambda r:r['request']['method']=='debug_traceTransaction' and r['request']['params']==[h,a.TRACE] and 'result' in r['response'],lambda r:r['response']['result'][a.TREASURY].update(nonce=0)))
 def test_native_refunds_and_reverted_frames(self):
  tx={'from':a.TREASURY,'to':a.POOL,'value':'0x10'}
  trace={'type':'CALL','from':a.TREASURY,'to':a.POOL,'value':'0x10','calls':[{'type':'CALL','from':a.POOL,'to':a.TREASURY,'value':'0x3'},{'type':'CALL','from':a.POOL,'to':a.TREASURY,'value':'0x7','error':'revert'},{'type':'DELEGATECALL','from':a.TREASURY,'to':a.POOL,'value':'0x10'}]}
  self.assertEqual(a.native_flows(trace,tx),(3,0))
  trace['value']='0x20'
  with self.assertRaises(ValueError):a.native_flows(trace,tx)
 def test_ordered_block_identity(self):
  b=self.result['buys'][-1];rows=self.alter(lambda r:r['url']==a.PRIMARY and r['request']['method']=='eth_getBlockByNumber' and r['request']['params']==[hex(b['block']),True],lambda r:r['response']['result']['transactions'][b['transactionIndex']].update(hash='0x'+'0'*64))
  self.rejects(rows)
 def test_positive_recovery_after_omission(self):
  self.test_missing_range();self.assertEqual(self.run_rows(self.rows)['verdicts']['buy_only_named_pool'],'KEPT')
if __name__=='__main__':unittest.main()
