from importlib.metadata import PackageNotFoundError, version as _metadata_version

from .core import (
    REVISION_MODE,
    SCHEMA_VERSION,
    STAGES,
    STATUSES,
    CanonicalRevisionReceiptError,
    CanonicalStateRevisionReceipt,
    canonical_json,
    create_receipt,
    sha256_ref,
    verify_receipt,
)

__all__ = [
    "REVISION_MODE",
    "SCHEMA_VERSION",
    "STAGES",
    "STATUSES",
    "CanonicalRevisionReceiptError",
    "CanonicalStateRevisionReceipt",
    "canonical_json",
    "create_receipt",
    "sha256_ref",
    "verify_receipt",
]

try:
    __version__ = _metadata_version("neuruh-canonical-state-revision-receipt")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "unknown"
