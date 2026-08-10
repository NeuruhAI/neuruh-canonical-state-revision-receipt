import unittest
from neuruh_canonical_state_revision_receipt import *
H=sha256_ref
def r(**kw):
 d=dict(receipt_id="r1",run_id="run1",action_id="revise1",target_id="t1",actor_id="op1",
  canonical_revision_authorization_digest=H("a"),reconciliation_proposal_digest=H("p"),drift_entry_digest=H("d"),
  previous_canonical_lifecycle_entry_digest=H("le"),revision_mode="adopt_observed",
  pre_canonical_stage="pilot",pre_canonical_state_digest=H("c"),
  target_canonical_stage="pilot",target_canonical_state_digest=H("o"),
  canonical_store_write_digest=H("w"),post_canonical_record_digest=H("record"),
  post_canonical_stage="pilot",post_canonical_state_digest=H("o"),verification_digest=H("v"),
  status="succeeded",started_at="2026-08-10T02:10:00Z",ended_at="2026-08-10T02:11:00Z")
 d.update(kw);return create_receipt(**d)
class T(unittest.TestCase):
 def bad(self,fn):
  with self.assertRaises(CanonicalRevisionReceiptError):fn()
 def test_valid(self):r().validate()
 def test_roundtrip(self):self.assertEqual(CanonicalStateRevisionReceipt.from_mapping(r().to_dict()),r())
 def test_success_exact(self):self.assertEqual(r().post_canonical_state_digest,H("o"))
 def test_success_wrong_stage(self):self.bad(lambda:r(post_canonical_stage="production"))
 def test_success_wrong_state(self):self.bad(lambda:r(post_canonical_state_digest=H("x")))
 def test_failed_can_differ(self):r(status="failed",post_canonical_state_digest=H("x")).validate()
 def test_actual_change_required(self):self.bad(lambda:r(target_canonical_state_digest=H("c"),post_canonical_state_digest=H("c")))
 def test_lifecycle_mutated_false(self):self.assertFalse(r().lifecycle_ledger_mutated)
 def test_lifecycle_mutated_true(self):self.bad(lambda:r(lifecycle_ledger_mutated=True))
 def test_revision_authority_false(self):self.assertFalse(r().canonical_state_revision_authority)
 def test_canonical_authority_false(self):self.assertFalse(r().canonical_state_authority)
 def test_execution_false(self):self.assertFalse(r().execution_authority)
 def test_deployment_false(self):self.assertFalse(r().deployment_authority)
 def test_reconciliation_false(self):self.assertFalse(r().reconciliation_authority)
 def test_revision_authority_true(self):self.bad(lambda:r(canonical_state_revision_authority=True))
 def test_canonical_authority_true(self):self.bad(lambda:r(canonical_state_authority=True))
 def test_execution_true(self):self.bad(lambda:r(execution_authority=True))
 def test_deployment_true(self):self.bad(lambda:r(deployment_authority=True))
 def test_reconciliation_true(self):self.bad(lambda:r(reconciliation_authority=True))
 def test_bad_mode(self):self.bad(lambda:r(revision_mode="restore_canonical"))
 def test_bad_status(self):self.bad(lambda:r(status="pending"))
 def test_bad_chronology(self):self.bad(lambda:r(ended_at="2026-08-10T02:09:00Z"))
 def test_bad_hash(self):self.bad(lambda:r(canonical_store_write_digest="bad"))
 def test_use_index_one(self):self.bad(lambda:r(authorization_use_index=1))
 def test_tamper(self):
  x=r().to_dict();x["post_canonical_state_digest"]=H("x");self.bad(lambda:CanonicalStateRevisionReceipt.from_mapping(x))
 def test_unknown_field(self):
  x=r().to_dict();x["mutate_026"]=True;self.bad(lambda:CanonicalStateRevisionReceipt.from_mapping(x))
 def test_verify_valid(self):self.assertTrue(verify_receipt(r(),target_id="t1",target_canonical_state_digest=H("o"),lifecycle_ledger_mutated=False))
 def test_verify_mismatch(self):self.bad(lambda:verify_receipt(r(),target_id="other"))
