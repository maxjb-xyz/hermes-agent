"""Managed source trees never enter the ordinary update mutation implementation."""
import json
from types import SimpleNamespace

import pytest

from hermes_cli.update_contract import evaluate_update_admission


def test_admission_and_direct_update_refuse_before_mutation(tmp_path, monkeypatch):
    (tmp_path / "managed-runtime.json").write_text(json.dumps({"schema": 1, "mode": "read_only", "allowed_reads": []}))
    refusal = evaluate_update_admission(tmp_path)
    assert refusal.code == "managed-runtime"
    from hermes_cli import update_cmd

    monkeypatch.setattr(update_cmd, "_m", lambda: SimpleNamespace(PROJECT_ROOT=tmp_path))
    with pytest.raises(PermissionError, match="independent controller"):
        update_cmd._cmd_update_impl(SimpleNamespace(), False)


def test_corrupt_managed_metadata_is_a_refusal(tmp_path):
    (tmp_path / "managed-runtime.json").write_text("{broken")
    assert evaluate_update_admission(tmp_path).code == "managed-runtime-invalid"
