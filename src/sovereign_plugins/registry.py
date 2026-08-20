from __future__ import annotations

from .contracts import Plugin
from .plugins.archive import ArchiveInspector
from .plugins.claims import ClaimResearchAnalyzer
from .plugins.document import DocumentExtractor
from .plugins.media import MediaMetadata
from .plugins.privacy import PrivacyDetector


class PluginRegistry:
    def __init__(self) -> None:
        self._plugins: dict[str, Plugin] = {}

    def register(self, plugin: Plugin) -> None:
        plugin_id = plugin.manifest.plugin_id
        if plugin_id in self._plugins:
            raise ValueError(f"Duplicate plugin identity: {plugin_id}")
        self._plugins[plugin_id] = plugin

    def get(self, plugin_id: str) -> Plugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise ValueError(f"Unknown plugin: {plugin_id}") from exc

    def manifests(self):
        return [self._plugins[key].manifest for key in sorted(self._plugins)]


def default_registry() -> PluginRegistry:
    registry = PluginRegistry()
    for plugin in (ArchiveInspector(), ClaimResearchAnalyzer(), DocumentExtractor(), MediaMetadata(), PrivacyDetector()):
        registry.register(plugin)
    return registry
