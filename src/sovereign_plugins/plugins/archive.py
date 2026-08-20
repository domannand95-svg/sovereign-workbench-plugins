from __future__ import annotations

import zipfile

from ..contracts import PluginManifest, PluginRequest, PluginResult


class ArchiveInspector:
    manifest = PluginManifest("archive.inspect", "1.0.0", "Inspect ZIP members without extraction", (".zip",), True)

    def run(self, request: PluginRequest) -> PluginResult:
        result = PluginResult(self.manifest.plugin_id, self.manifest.version, request.input_sha256)
        try:
            with zipfile.ZipFile(request.path) as archive:
                total = 0
                for member in archive.infolist():
                    normalized = member.filename.replace("\\", "/")
                    unsafe = normalized.startswith("/") or ".." in normalized.split("/")
                    total += member.file_size
                    result.findings.append({"member": normalized, "size": member.file_size, "unsafe_path": unsafe})
                result.artifacts.append({"kind": "archive_manifest", "members": len(archive.infolist()), "expanded_bytes": total})
        except (OSError, zipfile.BadZipFile) as exc:
            result.errors.append(type(exc).__name__)
        return result
