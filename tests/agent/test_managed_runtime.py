"""Read-only bootstrap must fail closed across owner/profile boundaries."""
import json

import pytest

from agent import managed_runtime as managed
from hermes_constants import get_hermes_home


def test_required_owner_binding_and_read_only_policy(tmp_path, monkeypatch):
    manifest = tmp_path / "managed-runtime.json"
    manifest.write_text(json.dumps({"schema": 1, "mode": "read_only", "allowed_reads": ["calendar"]}))
    monkeypatch.setattr(managed, "MANIFEST", manifest)
    with pytest.raises(PermissionError):
        managed.enforce_tool("calendar")
    request = managed.ManagedRequest("max", "max", "c1", str(get_hermes_home()), frozenset({"calendar"}), True, "max")
    with managed.bind_managed_request(request):
        managed.enforce_tool("calendar")
        with pytest.raises(PermissionError):
            managed.enforce_tool("terminal")
    contact = managed.ManagedRequest("max", "jordan", "c1", str(get_hermes_home()), frozenset({"calendar"}), False, "max")
    with managed.bind_managed_request(contact), pytest.raises(PermissionError):
        managed.enforce_tool("calendar")


def test_invalid_manifest_never_degrades_to_unmanaged(tmp_path, monkeypatch):
    manifest = tmp_path / "managed-runtime.json"
    manifest.write_text("not json")
    monkeypatch.setattr(managed, "MANIFEST", manifest)
    with pytest.raises(PermissionError):
        managed.enforce_tool("terminal")
    with pytest.raises(PermissionError):
        managed.refuse_managed_update(tmp_path)
    manifest.write_text('\ufeff' + json.dumps({'schema':1,'mode':'read_only','allowed_reads':[]}))
    assert managed.read_manifest()['mode'] == 'read_only'
