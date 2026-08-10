import argparse,json
from pathlib import Path
from .core import CanonicalStateRevisionReceipt
def main(argv=None):
    p=argparse.ArgumentParser(prog="neuruh-canonical-state-revision-receipt")
    s=p.add_subparsers(dest="cmd",required=True)
    for n in ("validate","digest","inspect"):
        x=s.add_parser(n);x.add_argument("file")
    a=p.parse_args(argv)
    o=CanonicalStateRevisionReceipt.from_mapping(json.loads(Path(a.file).read_text()))
    if a.cmd=="validate":
        print(json.dumps({
            "ok":True,"status":o.status,"lifecycle_ledger_mutated":o.lifecycle_ledger_mutated,
            "canonical_state_revision_authority":o.canonical_state_revision_authority,
            "canonical_state_authority":o.canonical_state_authority,
            "execution_authority":o.execution_authority,
        },sort_keys=True))
    elif a.cmd=="digest":print(o.receipt_digest)
    else:print(json.dumps(o.to_dict(),indent=2,sort_keys=True))
if __name__=="__main__":main()
