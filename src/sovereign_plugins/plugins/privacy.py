from __future__ import annotations

import re

from ..contracts import PluginManifest, PluginRequest, PluginResult


PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(r"(?<!\d)(?:\+?61|0)[2-478](?:[ -]?\d){8}(?!\d)"),
    "payment_card_candidate": re.compile(r"\b(?:\d[ -]*?){13,19}\b"),
}


class PrivacyDetector:
    manifest = PluginManifest("privacy.detect", "1.0.0", "Detect sensitive-data candidates locally", (".txt", ".md", ".csv", ".json"), True)

    def run(self, request: PluginRequest) -> PluginResult:
        result = PluginResult(self.manifest.plugin_id, self.manifest.version, request.input_sha256)
        try:
            text = request.path.read_text(encoding="utf-8", errors="strict")
            for kind, pattern in PATTERNS.items():
                count = len(pattern.findall(text))
                if count:
                    result.findings.append({"kind": kind, "count": count, "route": "privacy-review"})
        except (OSError, UnicodeDecodeError) as exc:
            result.errors.append(type(exc).__name__)
        return result
