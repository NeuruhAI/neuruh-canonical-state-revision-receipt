from pathlib import Path
import sys,json
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from neuruh_canonical_state_revision_receipt import *
H=sha256_ref
r=create_receipt(
 receipt_id="cr1",run_id="run1",action_id="canonical-revise",target_id="t1",actor_id="op1",
 canonical_revision_authorization_digest=H("auth"),reconciliation_proposal_digest=H("proposal"),
 drift_entry_digest=H("drift"),previous_canonical_lifecycle_entry_digest=H("lifecycle-entry"),
 revision_mode="adopt_observed",pre_canonical_stage="pilot",pre_canonical_state_digest=H("canonical"),
 target_canonical_stage="pilot",target_canonical_state_digest=H("observed"),
 canonical_store_write_digest=H("write"),post_canonical_record_digest=H("record"),
 post_canonical_stage="pilot",post_canonical_state_digest=H("observed"),verification_digest=H("verify"),
 status="succeeded",started_at="2026-08-10T02:10:00Z",ended_at="2026-08-10T02:11:00Z")
Path(__file__).with_name("receipt.synthetic.json").write_text(json.dumps(r.to_dict(),indent=2,sort_keys=True)+"\n")
print(r.receipt_digest)
