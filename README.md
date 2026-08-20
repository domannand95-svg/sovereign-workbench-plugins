# Sovereign Workbench Plugins

Local, hash-bound capability plugins for
[Sovereign Knowledge Workbench](https://github.com/domannand95-svg/sovereign-knowledge-workbench),
[BKI](https://github.com/domannand95-svg/knowledge-infrastructure-bootstrap-kit),
and [Sovereign OS](https://github.com/domannand95-svg/sovereign-os).

Plugins analyze explicitly supplied files and return candidate records. They
have no authority to move, delete, publish, upload, email, promote, or grant
capabilities. Every result binds to the SHA-256 of its input.

## Included plugins

| Plugin | Purpose |
| --- | --- |
| `archive.inspect` | Inspect ZIP membership and flag path traversal without extraction |
| `document.extract` | Extract bounded text from text, PDF, DOCX, PPTX, and HTML |
| `media.metadata` | Read image dimensions and selected EXIF fields |
| `privacy.detect` | Detect sensitive-data candidates for privacy review |
| `research.claims` | Extract DOI, URL, and explicit research-gap candidates |

## Local setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e ".[dev,documents,media]"
.\.venv\Scripts\python.exe -m pytest
.\.venv\Scripts\swp.exe list
```

Run one bounded plugin:

```powershell
.\.venv\Scripts\swp.exe run privacy.detect C:\path\to\document.md
```

## Contract

Every successful response is `sovereign.plugin.result.v1`, has `status` set to
`candidate`, `authority` set to `none`, and includes the exact `input_sha256`.
The CLI rejects symbolic links, unsupported suffixes, oversized inputs, unknown
plugins, duplicate plugin identities, and result-binding violations.

Machine-readable manifest and result contracts are published under `schemas/`
for BKI and Sovereign consumers. Schema compatibility never grants authority.

Optional libraries are grouped by capability so a laptop installs only what it
needs. Network access is denied by every built-in manifest. Future research,
transcription, semantic-search, and dispatch adapters must declare network,
model, and capability requirements explicitly and remain subordinate to
Sovereign authorization.
