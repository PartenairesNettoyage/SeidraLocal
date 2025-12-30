"""Modèles de données pour la génération de médias."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence

IMAGE_MIME_TYPES_BY_FORMAT = {
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
}
VIDEO_MIME_TYPES_BY_FORMAT = {
    "mp4": "video/mp4",
    "webm": "video/webm",
}

MAX_IMAGE_SIZE_BYTES = 10 * 1024 * 1024
MAX_VIDEO_SIZE_BYTES = 100 * 1024 * 1024


def _normalize_format(output_format: str) -> str:
    return output_format.strip().lower()


def get_image_mime_type(output_format: str) -> str:
    normalized = _normalize_format(output_format)
    if normalized not in IMAGE_MIME_TYPES_BY_FORMAT:
        raise ValueError(
            "Format d'image non supporté. "
            f"Reçu: {output_format}. Autorisés: {sorted(IMAGE_MIME_TYPES_BY_FORMAT)}"
        )
    return IMAGE_MIME_TYPES_BY_FORMAT[normalized]


def get_video_mime_type(output_format: str) -> str:
    normalized = _normalize_format(output_format)
    if normalized not in VIDEO_MIME_TYPES_BY_FORMAT:
        raise ValueError(
            "Format vidéo non supporté. "
            f"Reçu: {output_format}. Autorisés: {sorted(VIDEO_MIME_TYPES_BY_FORMAT)}"
        )
    return VIDEO_MIME_TYPES_BY_FORMAT[normalized]


def validate_max_size(size_bytes: int, max_size_bytes: int, *, media_label: str) -> None:
    if size_bytes > max_size_bytes:
        raise ValueError(
            f"Taille {media_label} trop grande: {size_bytes} octets. "
            f"Maximum: {max_size_bytes} octets."
        )


@dataclass(frozen=True)
class CharacterProfile:
    """Représente un personnage utilisé dans la génération de médias."""

    identifier: str
    name: str
    description: str
    traits: Sequence[str] = field(default_factory=tuple)
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class PromptSpec:
    """Spécification de prompt avec variables et versionnage."""

    template: str
    variables: Mapping[str, Any] = field(default_factory=dict)
    version: str | None = None


@dataclass(frozen=True)
class StyleProfile:
    """Style visuel ou narratif appliqué à une génération."""

    name: str
    description: str | None = None
    tags: Sequence[str] = field(default_factory=tuple)


@dataclass(frozen=True)
class SceneSpec:
    """Décrit une scène impliquant un ou plusieurs personnages."""

    identifier: str
    summary: str
    characters: Sequence[CharacterProfile]
    location: str | None = None
    mood: str | None = None


@dataclass(frozen=True)
class MediaResolution:
    """Résolution cible pour la génération."""

    width: int
    height: int


@dataclass(frozen=True)
class ImageGenerationConfig:
    """Paramètres de génération d'images."""

    resolution: MediaResolution
    style: StyleProfile | None = None
    steps: int = 30
    guidance_scale: float = 7.5
    seed: int | None = None
    output_format: str = "png"
    max_size_bytes: int = MAX_IMAGE_SIZE_BYTES

    def __post_init__(self) -> None:
        get_image_mime_type(self.output_format)
        if self.max_size_bytes <= 0:
            raise ValueError("max_size_bytes doit être un entier positif.")


@dataclass(frozen=True)
class VideoGenerationConfig:
    """Paramètres de génération de vidéos."""

    resolution: MediaResolution
    duration_seconds: float
    fps: int = 24
    style: StyleProfile | None = None
    seed: int | None = None
    output_format: str = "mp4"
    max_size_bytes: int = MAX_VIDEO_SIZE_BYTES

    def __post_init__(self) -> None:
        get_video_mime_type(self.output_format)
        if self.max_size_bytes <= 0:
            raise ValueError("max_size_bytes doit être un entier positif.")


@dataclass(frozen=True)
class MediaAsset:
    """Sortie générique d'une génération multimédia."""

    uri: str
    mime_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
