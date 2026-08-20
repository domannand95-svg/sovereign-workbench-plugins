from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass(frozen=True)
class PluginManifest:
    plugin_id: str
    version: str
    description: str
    accepted_suffixes: tuple[str, ...]
    deterministic: bool
    network: str = "denied"
    requested_capabilities: tuple[str, ...] = ("filesystem.read",)


@dataclass(frozen=True)
class PluginRequest:
    path: Path
    input_sha256: str
    options: dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginResult:
    plugin_id: str
    plugin_version: str
    input_sha256: str
    status: str = "candidate"
    findings: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    requested_actions: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {"contract_version": "sovereign.plugin.result.v1", "authority": "none", **asdict(self)}


class Plugin(Protocol):
    manifest: PluginManifest
    def run(self, request: PluginRequest) -> PluginResult: ...


def hash_file(path: Path, max_bytes: int = 100 * 1024 * 1024) -> str:
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be a regular non-link file")
    if path.stat().st_size > max_bytes:
        raise ValueError("Input exceeds configured size limit")
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
