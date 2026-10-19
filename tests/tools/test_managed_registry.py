"""Direct registry calls cannot bypass the managed runtime's required boundary."""
import json

from agent import managed_runtime as managed
from hermes_constants import get_hermes_home
from tools.registry import ToolRegistry


def test_direct_dispatch_denies_missing_context_and_effect_handlers(tmp_path, monkeypatch):
    manifest = tmp_path / "managed-runtime.json"
    manifest.write_text(json.dumps({"schema": 1, "mode": "read_only", "allowed_reads": ["read"]}))
    monkeypatch.setattr(managed, "MANIFEST", manifest)
    calls = []
    registry = ToolRegistry()
    for name in ("read", "send"):
        registry.register(name=name, toolset="test", schema={"name": name, "parameters": {}},
                          handler=lambda args: calls.append(args) or '{"ok":true}')
    assert "error" in json.loads(registry.dispatch("read", {}))
    request = managed.ManagedRequest("max", "max", "c1", str(get_hermes_home()), frozenset({"read"}), True, "max")
    with managed.bind_managed_request(request):
        assert json.loads(registry.dispatch("read", {}))["ok"]
        assert "error" in json.loads(registry.dispatch("send", {}))
    assert calls == [{}]
