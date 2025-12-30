"""Modèles de données pour la génération de médias."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


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


@dataclass(frozen=True)
class VideoGenerationConfig:
    """Paramètres de génération de vidéos."""

    resolution: MediaResolution
    duration_seconds: float
    fps: int = 24
    style: StyleProfile | None = None
    seed: int | None = None
    output_format: str = "mp4"


@dataclass(frozen=True)
class MediaAsset:
    """Sortie générique d'une génération multimédia."""

    uri: str
    mime_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)
