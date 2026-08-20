import json
import zipfile
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from sovereign_plugins.cli import main
from sovereign_plugins.contracts import PluginRequest, hash_file
from sovereign_plugins.registry import PluginRegistry, default_registry


def test_registry_has_unique_candidate_only_plugins():
    manifests = default_registry().manifests()
    assert len(manifests) == 5
    assert all(item.network == "denied" for item in manifests)


def test_duplicate_plugin_identity_fails():
    plugin = default_registry().get("privacy.detect")
    registry = PluginRegistry()
    registry.register(plugin)
    with pytest.raises(ValueError):
        registry.register(plugin)


def test_privacy_result_is_hash_bound(tmp_path: Path):
    path = tmp_path / "note.txt"
    path.write_text("Contact person@example.org", encoding="utf-8")
    digest = hash_file(path)
    result = default_registry().get("privacy.detect").run(PluginRequest(path, digest))
    assert result.input_sha256 == digest
    assert result.status == "candidate"
    assert result.to_dict()["authority"] == "none"


def test_archive_inspection_does_not_extract_zip_slip(tmp_path: Path):
    path = tmp_path / "bad.zip"
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("../../escape.txt", "bad")
    result = default_registry().get("archive.inspect").run(PluginRequest(path, hash_file(path)))
    assert result.findings[0]["unsafe_path"] is True
    assert not (tmp_path.parent / "escape.txt").exists()


def test_cli_rejects_wrong_suffix(tmp_path: Path, capsys):
    path = tmp_path / "image.jpg"
    path.write_bytes(b"fake")
    assert main(["run", "privacy.detect", str(path)]) == 3
    assert "does not accept" in capsys.readouterr().out


def test_claim_plugin_extracts_doi_and_gap(tmp_path: Path):
    path = tmp_path / "paper.md"
    path.write_text("Citation needed. DOI 10.1234/example.1", encoding="utf-8")
    result = default_registry().get("research.claims").run(PluginRequest(path, hash_file(path)))
    kinds = {item["kind"] for item in result.findings}
    assert kinds == {"doi", "research_gap"}


def test_published_schemas_accept_builtin_contracts(tmp_path: Path):
    root = Path(__file__).parents[1]
    manifest_schema = json.loads((root / "schemas/plugin-manifest-v1.schema.json").read_text())
    result_schema = json.loads((root / "schemas/plugin-result-v1.schema.json").read_text())
    registry = default_registry()
    for manifest in registry.manifests():
        Draft202012Validator(manifest_schema).validate(json.loads(json.dumps(manifest.__dict__)))
    path = tmp_path / "note.md"
    path.write_text("Research required", encoding="utf-8")
    result = registry.get("research.claims").run(PluginRequest(path, hash_file(path)))
    Draft202012Validator(result_schema).validate(result.to_dict())
