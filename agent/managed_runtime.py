"""Fail-closed read-only bootstrap boundary for controller-owned runtimes.

The source-tree manifest belongs to the independently sealed release, not a profile's
mutable preferences. No effect authorization is implemented by this bootstrap contract.
"""
from __future__ import annotations

import json
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from pathlib import Path

MANIFEST = Path(__file__).resolve().parents[1] / "managed-runtime.json"


@dataclass(frozen=True)
class ManagedRequest:
    owner_id: str
    actor_id: str
    conversation_id: str
    profile_home: str
    allowed_reads: frozenset[str]
    owner_direct: bool
    owner_person_id: str


_REQUEST: ContextVar[ManagedRequest | None] = ContextVar("managed_request", default=None)


@contextmanager
def bind_managed_request(request: ManagedRequest):
    token = _REQUEST.set(request)
    try:
        yield
    finally:
        _REQUEST.reset(token)


def read_manifest(root: Path | None = None) -> dict | None:
    path = MANIFEST if root is None else root / MANIFEST.name
    try:
        manifest = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        return None
    except (OSError, ValueError) as exc:
        raise PermissionError("managed runtime manifest unavailable") from exc
    if (not isinstance(manifest, dict) or manifest.get("schema") != 1
            or manifest.get("mode") != "read_only"
            or not isinstance(manifest.get("allowed_reads"), list)
            or not all(isinstance(name, str) for name in manifest["allowed_reads"])):
        raise PermissionError("invalid managed runtime manifest")
    return manifest


def enforce_tool(name: str) -> None:
    manifest = read_manifest()
    if manifest is None:
        return
    from hermes_constants import get_hermes_home

    request = _REQUEST.get()
    if (request is None or not request.owner_id or not request.conversation_id
            or not request.owner_direct or request.actor_id != request.owner_person_id
            or Path(request.profile_home).resolve() != get_hermes_home().resolve()
            or name not in request.allowed_reads or name not in manifest["allowed_reads"]):
        raise PermissionError("managed runtime denies unbound, non-owner or effect tool call")


def refuse_managed_update(root: Path) -> None:
    if read_manifest(root) is not None:
        raise PermissionError("Updates are integrated and deployed by the independent controller.")
