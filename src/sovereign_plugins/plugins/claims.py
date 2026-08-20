from __future__ import annotations

import re

from ..contracts import PluginManifest, PluginRequest, PluginResult


DOI = re.compile(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", re.I)
URL = re.compile(r"https?://[^\s)>\]}]+")
CUES = ("citation needed", "research required", "verify source", "open question")


class ClaimResearchAnalyzer:
    manifest = PluginManifest("research.claims", "1.0.0", "Extract citation identifiers and explicit research gaps", (".txt", ".md"), True)

    def run(self, request: PluginRequest) -> PluginResult:
        result = PluginResult(self.manifest.plugin_id, self.manifest.version, request.input_sha256)
        try:
            text = request.path.read_text(encoding="utf-8", errors="strict")
            for doi in sorted(set(DOI.findall(text))):
                result.findings.append({"kind": "doi", "value": doi})
            for url in sorted(set(URL.findall(text))):
                result.findings.append({"kind": "url", "value": url})
            for number, line in enumerate(text.splitlines(), 1):
                if any(cue in line.casefold() for cue in CUES):
                    result.findings.append({"kind": "research_gap", "line": number, "text": line.strip()[:500]})
        except (OSError, UnicodeDecodeError) as exc:
            result.errors.append(type(exc).__name__)
        return result
