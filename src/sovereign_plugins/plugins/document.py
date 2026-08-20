from __future__ import annotations

import hashlib

from ..contracts import PluginManifest, PluginRequest, PluginResult


class DocumentExtractor:
    manifest = PluginManifest("document.extract", "1.0.0", "Bounded local text extraction", (".pdf", ".docx", ".pptx", ".html", ".md", ".txt"), False)

    def run(self, request: PluginRequest) -> PluginResult:
        result = PluginResult(self.manifest.plugin_id, self.manifest.version, request.input_sha256)
        max_chars = min(int(request.options.get("max_chars", 200_000)), 1_000_000)
        try:
            if request.path.suffix.casefold() in {".txt", ".md", ".html"}:
                text = request.path.read_text(encoding="utf-8", errors="strict")[:max_chars]
            elif request.path.suffix.casefold() == ".pdf":
                from pypdf import PdfReader
                text = "\n".join(page.extract_text() or "" for page in PdfReader(request.path).pages)[:max_chars]
            else:
                from docling.document_converter import DocumentConverter
                text = DocumentConverter().convert(request.path).document.export_to_markdown()[:max_chars]
            encoded = text.encode("utf-8")
            result.artifacts.append({"kind": "extracted_text", "sha256": hashlib.sha256(encoded).hexdigest(), "characters": len(text), "content": text})
        except (OSError, UnicodeDecodeError, ImportError, Exception) as exc:
            result.errors.append(type(exc).__name__)
        return result
