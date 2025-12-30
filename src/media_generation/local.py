"""Modèles locaux basés sur l'exécution de commandes."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
import subprocess

from .models import (
    ImageGenerationConfig,
    MediaAsset,
    SceneSpec,
    VideoGenerationConfig,
    get_image_mime_type,
    get_video_mime_type,
    validate_max_size,
)


@dataclass(frozen=True)
class CommandTemplate:
    """Template de commande shell."""

    template: str

    def render(self, variables: dict[str, object]) -> str:
        return self.template.format_map(defaultdict(str, variables))


class LocalImageCommandModel:
    """Exécute une commande locale pour générer une image."""

    def __init__(self, base_path: Path, template: CommandTemplate) -> None:
        self.base_path = base_path
        self.template = template

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: ImageGenerationConfig,
    ) -> MediaAsset:
        self.base_path.mkdir(parents=True, exist_ok=True)
        filename = f"image_{scene.identifier}.{config.output_format}"
        output_path = self.base_path / filename
        command = self.template.render(
            {
                "prompt": prompt,
                "output_path": output_path,
                "width": config.resolution.width,
                "height": config.resolution.height,
                "steps": config.steps,
                "guidance_scale": config.guidance_scale,
                "seed": config.seed or "",
                "scene_identifier": scene.identifier,
                "style_name": config.style.name if config.style else "",
                "style_tags": ",".join(config.style.tags) if config.style else "",
            }
        )
        _run_command(command)
        _ensure_output_exists(output_path, command)
        size_bytes = output_path.stat().st_size
        validate_max_size(size_bytes, config.max_size_bytes, media_label="image")
        return MediaAsset(
            uri=output_path.as_uri(),
            mime_type=get_image_mime_type(config.output_format),
            metadata={
                "mode": "local_command",
                "command": command,
                "format": config.output_format,
                "size_bytes": size_bytes,
            },
        )


class LocalVideoCommandModel:
    """Exécute une commande locale pour générer une vidéo."""

    def __init__(self, base_path: Path, template: CommandTemplate) -> None:
        self.base_path = base_path
        self.template = template

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: VideoGenerationConfig,
    ) -> MediaAsset:
        self.base_path.mkdir(parents=True, exist_ok=True)
        filename = f"video_{scene.identifier}.{config.output_format}"
        output_path = self.base_path / filename
        command = self.template.render(
            {
                "prompt": prompt,
                "output_path": output_path,
                "width": config.resolution.width,
                "height": config.resolution.height,
                "duration_seconds": config.duration_seconds,
                "fps": config.fps,
                "seed": config.seed or "",
                "scene_identifier": scene.identifier,
                "style_name": config.style.name if config.style else "",
                "style_tags": ",".join(config.style.tags) if config.style else "",
            }
        )
        _run_command(command)
        _ensure_output_exists(output_path, command)
        size_bytes = output_path.stat().st_size
        validate_max_size(size_bytes, config.max_size_bytes, media_label="video")
        return MediaAsset(
            uri=output_path.as_uri(),
            mime_type=get_video_mime_type(config.output_format),
            metadata={
                "mode": "local_command",
                "command": command,
                "format": config.output_format,
                "size_bytes": size_bytes,
            },
        )


def _run_command(command: str) -> None:
    subprocess.run(command, shell=True, check=True)


def _ensure_output_exists(path: Path, command: str) -> None:
    if not path.exists():
        raise RuntimeError(
            "La commande locale n'a pas produit de fichier. "
            f"Attendu: {path}. Commande: {command}"
        )
