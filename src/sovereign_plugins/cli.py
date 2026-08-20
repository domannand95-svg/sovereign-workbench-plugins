from __future__ import annotations

import argparse
import json
from dataclasses import asdict
from pathlib import Path

from .contracts import PluginRequest, canonical_json, hash_file
from .registry import default_registry


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="swp")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    run = sub.add_parser("run")
    run.add_argument("plugin_id")
    run.add_argument("path", type=Path)
    run.add_argument("--max-bytes", type=int, default=100 * 1024 * 1024)
    args = parser.parse_args(argv)
    registry = default_registry()
    try:
        if args.command == "list":
            print(json.dumps([asdict(item) for item in registry.manifests()], sort_keys=True))
            return 0
        digest = hash_file(args.path, args.max_bytes)
        plugin = registry.get(args.plugin_id)
        if plugin.manifest.accepted_suffixes and args.path.suffix.casefold() not in plugin.manifest.accepted_suffixes:
            raise ValueError("Plugin does not accept this file type")
        result = plugin.run(PluginRequest(args.path.resolve(), digest))
        if result.input_sha256 != digest or result.status != "candidate":
            raise ValueError("Plugin violated result binding")
        print(canonical_json(result.to_dict()))
        return 0 if not result.errors else 2
    except (OSError, ValueError) as exc:
        print(json.dumps({"contract_version": "sovereign.plugin.error.v1", "error": str(exc)}))
        return 3


if __name__ == "__main__":
    raise SystemExit(main())
