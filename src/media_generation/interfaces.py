"""Interfaces pour brancher des modèles de génération."""

from __future__ import annotations

from typing import Protocol

from .models import (
    ImageGenerationConfig,
    MediaAsset,
    PromptSpec,
    SceneSpec,
    VideoGenerationConfig,
)


class PromptRenderer(Protocol):
    """Construit un prompt final à partir des éléments narratifs."""

    def render(self, scene: SceneSpec, prompt: PromptSpec) -> str:
        """Retourne le texte de prompt final."""


class ImageModel(Protocol):
    """Interface pour un modèle de diffusion d'images."""

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: ImageGenerationConfig,
    ) -> MediaAsset:
        """Génère une image à partir d'une scène et d'un prompt."""


class VideoModel(Protocol):
    """Interface pour un modèle de génération vidéo."""

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: VideoGenerationConfig,
    ) -> MediaAsset:
        """Génère une vidéo à partir d'une scène et d'un prompt."""
