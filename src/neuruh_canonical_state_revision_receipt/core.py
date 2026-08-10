from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json,re
from typing import Any,Mapping

SCHEMA_VERSION="neuruh.canonical-state-revision-receipt.v0.1"
STAGES=("sandbox","canary","pilot","production")
STATUSES={"succeeded","failed"}
REVISION_MODE="adopt_observed"
HEX64=re.compile(r"^[0-9a-f]{64}$")

class CanonicalRevisionReceiptError(ValueError):
    """Fail-closed refusal for malformed, contradictory, or tampered canonical revision evidence."""

def canonical_json(v:Any)->str:
    return json.dumps(v,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)

def sha256_ref(v:str|bytes)->str:
    if isinstance(v,str):v=v.encode("utf-8")
    return "sha256:"+sha256(v).hexdigest()

def _nonempty(v:Any,n:str)->str:
    if not isinstance(v,str) or not v.strip():
        raise CanonicalRevisionReceiptError(f"{n} must be a non-empty string")
    return v

def _sha(v:Any,n:str)->str:
    v=_nonempty(v,n)
    if not v.startswith("sha256:") or not HEX64.fullmatch(v[7:]):
        raise CanonicalRevisionReceiptError(f"{n} must be sha256:<64 lowercase hex>")
    return v

def _time(v:Any,n:str):
    v=_nonempty(v,n)
    try:dt=datetime.fromisoformat(v.replace("Z","+00:00"))
    except ValueError as exc:
        raise CanonicalRevisionReceiptError(f"{n} must be RFC3339/ISO-8601") from exc
    if dt.tzinfo is None:
        raise CanonicalRevisionReceiptError(f"{n} must include a timezone")
    return dt.astimezone(timezone.utc)

@dataclass(frozen=True)
class CanonicalStateRevisionReceipt:
    receipt_id:str
    run_id:str
    action_id:str
    target_id:str
    actor_id:str

    canonical_revision_authorization_digest:str
    reconciliation_proposal_digest:str
    drift_entry_digest:str
    previous_canonical_lifecycle_entry_digest:str

    revision_mode:str
    pre_canonical_stage:str
    pre_canonical_state_digest:str
    target_canonical_stage:str
    target_canonical_state_digest:str

    canonical_store_write_digest:str
    post_canonical_record_digest:str
    post_canonical_stage:str
    post_canonical_state_digest:str
    verification_digest:str

    status:str
    started_at:str
    ended_at:str
    authorization_use_index:int=0

    lifecycle_ledger_mutated:bool=False
    canonical_state_revision_authority:bool=False
    canonical_state_authority:bool=False
    execution_authority:bool=False
    deployment_authority:bool=False
    reconciliation_authority:bool=False
    receipt_digest:str|None=None

    def body_dict(self):
        return {
            "schema_version":SCHEMA_VERSION,
            "receipt_id":self.receipt_id,"run_id":self.run_id,"action_id":self.action_id,
            "target_id":self.target_id,"actor_id":self.actor_id,
            "canonical_revision_authorization_digest":self.canonical_revision_authorization_digest,
            "reconciliation_proposal_digest":self.reconciliation_proposal_digest,
            "drift_entry_digest":self.drift_entry_digest,
            "previous_canonical_lifecycle_entry_digest":self.previous_canonical_lifecycle_entry_digest,
            "revision_mode":self.revision_mode,
            "pre_canonical_stage":self.pre_canonical_stage,
            "pre_canonical_state_digest":self.pre_canonical_state_digest,
            "target_canonical_stage":self.target_canonical_stage,
            "target_canonical_state_digest":self.target_canonical_state_digest,
            "canonical_store_write_digest":self.canonical_store_write_digest,
            "post_canonical_record_digest":self.post_canonical_record_digest,
            "post_canonical_stage":self.post_canonical_stage,
            "post_canonical_state_digest":self.post_canonical_state_digest,
            "verification_digest":self.verification_digest,
            "status":self.status,"started_at":self.started_at,"ended_at":self.ended_at,
            "authorization_use_index":0,
            "lifecycle_ledger_mutated":False,
            "canonical_state_revision_authority":False,
            "canonical_state_authority":False,
            "execution_authority":False,
            "deployment_authority":False,
            "reconciliation_authority":False,
        }

    def calculated_digest(self):return sha256_ref(canonical_json(self.body_dict()))

    def validate(self,check_digest:bool=True):
        for v,n in [
            (self.receipt_id,"receipt_id"),(self.run_id,"run_id"),(self.action_id,"action_id"),
            (self.target_id,"target_id"),(self.actor_id,"actor_id")
        ]:_nonempty(v,n)
        for v,n in [
            (self.canonical_revision_authorization_digest,"canonical_revision_authorization_digest"),
            (self.reconciliation_proposal_digest,"reconciliation_proposal_digest"),
            (self.drift_entry_digest,"drift_entry_digest"),
            (self.previous_canonical_lifecycle_entry_digest,"previous_canonical_lifecycle_entry_digest"),
            (self.pre_canonical_state_digest,"pre_canonical_state_digest"),
            (self.target_canonical_state_digest,"target_canonical_state_digest"),
            (self.canonical_store_write_digest,"canonical_store_write_digest"),
            (self.post_canonical_record_digest,"post_canonical_record_digest"),
            (self.post_canonical_state_digest,"post_canonical_state_digest"),
            (self.verification_digest,"verification_digest"),
        ]:_sha(v,n)
        for v,n in [
            (self.pre_canonical_stage,"pre_canonical_stage"),(self.target_canonical_stage,"target_canonical_stage"),
            (self.post_canonical_stage,"post_canonical_stage")
        ]:
            if v not in STAGES:raise CanonicalRevisionReceiptError(f"{n} must be a known lifecycle stage")
        if self.revision_mode!=REVISION_MODE:
            raise CanonicalRevisionReceiptError("v0.1 supports adopt_observed only")
        if self.target_canonical_stage != self.pre_canonical_stage:
            raise CanonicalRevisionReceiptError("canonical state revision receipt cannot evidence a lifecycle-stage change")
        if self.status not in STATUSES:
            raise CanonicalRevisionReceiptError("unknown status")
        if self.pre_canonical_stage==self.target_canonical_stage and self.pre_canonical_state_digest==self.target_canonical_state_digest:
            raise CanonicalRevisionReceiptError("canonical revision receipt requires an actual canonical change")
        if _time(self.ended_at,"ended_at")<_time(self.started_at,"started_at"):
            raise CanonicalRevisionReceiptError("ended_at cannot precede started_at")
        if isinstance(self.authorization_use_index,bool) or not isinstance(self.authorization_use_index,int) or self.authorization_use_index!=0:
            raise CanonicalRevisionReceiptError("v0.1 single-use revision requires authorization_use_index=0")
        if self.status=="succeeded":
            if self.post_canonical_stage!=self.target_canonical_stage:
                raise CanonicalRevisionReceiptError("successful revision must exactly match target canonical stage")
            if self.post_canonical_state_digest!=self.target_canonical_state_digest:
                raise CanonicalRevisionReceiptError("successful revision must exactly match target canonical state")
        if self.lifecycle_ledger_mutated is not False:
            raise CanonicalRevisionReceiptError("v0.1 receipt must not claim Release 026 lifecycle ledger mutation")
        if any(v is not False for v in (
            self.canonical_state_revision_authority,self.canonical_state_authority,self.execution_authority,
            self.deployment_authority,self.reconciliation_authority
        )):
            raise CanonicalRevisionReceiptError("receipt is evidence only and cannot carry authority")
        if check_digest:
            _sha(self.receipt_digest,"receipt_digest")
            if self.receipt_digest!=self.calculated_digest():
                raise CanonicalRevisionReceiptError("receipt_digest mismatch")

    def seal(self):
        self.validate(False)
        obj=CanonicalStateRevisionReceipt(**{
            **self.__dict__,"authorization_use_index":0,"lifecycle_ledger_mutated":False,
            "canonical_state_revision_authority":False,"canonical_state_authority":False,
            "execution_authority":False,"deployment_authority":False,"reconciliation_authority":False,
            "receipt_digest":self.calculated_digest(),
        })
        obj.validate();return obj

    def to_dict(self):
        o=self.seal();d=o.body_dict();d["receipt_digest"]=o.receipt_digest;return d

    @classmethod
    def from_mapping(cls,raw:Mapping[str,Any]):
        expected=set(cls.__dataclass_fields__)|{"schema_version"}
        if set(raw)!=expected:raise CanonicalRevisionReceiptError("unknown or missing fields")
        if raw["schema_version"]!=SCHEMA_VERSION:raise CanonicalRevisionReceiptError("unsupported schema_version")
        obj=cls(**{k:raw[k] for k in cls.__dataclass_fields__});obj.validate();return obj

def create_receipt(**kw):return CanonicalStateRevisionReceipt(**kw).seal()

def verify_receipt(r:CanonicalStateRevisionReceipt,**expected)->bool:
    r.validate()
    for f,v in expected.items():
        if not hasattr(r,f) or getattr(r,f)!=v:
            raise CanonicalRevisionReceiptError(f"receipt binding mismatch: {f}")
    return True
