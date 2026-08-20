from __future__ import annotations

from ..contracts import PluginManifest, PluginRequest, PluginResult


class MediaMetadata:
    manifest = PluginManifest("media.metadata", "1.0.0", "Read image dimensions and EXIF candidates", (".jpg", ".jpeg", ".png", ".tiff", ".webp"), True)

    def run(self, request: PluginRequest) -> PluginResult:
        result = PluginResult(self.manifest.plugin_id, self.manifest.version, request.input_sha256)
        try:
            from PIL import Image, ExifTags
            with Image.open(request.path) as image:
                result.artifacts.append({"kind": "image_metadata", "format": image.format, "width": image.width, "height": image.height})
                exif = image.getexif()
                for key, value in exif.items():
                    name = ExifTags.TAGS.get(key, str(key))
                    if name in {"DateTime", "DateTimeOriginal", "Make", "Model", "GPSInfo"}:
                        result.findings.append({"kind": "exif", "field": name, "value": str(value)[:500], "privacy_review": name == "GPSInfo"})
        except (OSError, ImportError) as exc:
            result.errors.append(type(exc).__name__)
        return result
