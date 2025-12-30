"""Orchestration de la génération d'images et de vidéos."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Mapping

from .interfaces import ImageModel, PromptRenderer, VideoModel
from .models import (
    ImageGenerationConfig,
    MediaAsset,
    PromptSpec,
    SceneSpec,
    VideoGenerationConfig,
)


@dataclass
class MediaGenerationOrchestrator:
    """Coordonne la génération de médias avec les modèles branchés."""

    prompt_renderer: PromptRenderer
    image_models: Mapping[str, ImageModel] = field(default_factory=dict)
    video_models: Mapping[str, VideoModel] = field(default_factory=dict)

    def register_image_model(self, name: str, model: ImageModel) -> None:
        """Enregistre un modèle d'image sous un nom."""

        self.image_models = {**self.image_models, name: model}

    def register_video_model(self, name: str, model: VideoModel) -> None:
        """Enregistre un modèle vidéo sous un nom."""

        self.video_models = {**self.video_models, name: model}

    def generate_image(
        self,
        *,
        scene: SceneSpec,
        prompt: PromptSpec,
        config: ImageGenerationConfig,
        model_name: str,
    ) -> MediaAsset:
        """Génère une image à partir d'une scène et d'un prompt."""

        model = self._get_image_model(model_name)
        rendered_prompt = self.prompt_renderer.render(scene, prompt)
        return model.generate(scene=scene, prompt=rendered_prompt, config=config)

    def generate_video(
        self,
        *,
        scene: SceneSpec,
        prompt: PromptSpec,
        config: VideoGenerationConfig,
        model_name: str,
    ) -> MediaAsset:
        """Génère une vidéo à partir d'une scène et d'un prompt."""

        model = self._get_video_model(model_name)
        rendered_prompt = self.prompt_renderer.render(scene, prompt)
        return model.generate(scene=scene, prompt=rendered_prompt, config=config)

    def _get_image_model(self, model_name: str) -> ImageModel:
        if model_name not in self.image_models:
            raise ValueError(
                f"Modèle d'image '{model_name}' introuvable. "
                f"Disponibles: {sorted(self.image_models)}"
            )
        return self.image_models[model_name]

    def _get_video_model(self, model_name: str) -> VideoModel:
        if model_name not in self.video_models:
            raise ValueError(
                f"Modèle vidéo '{model_name}' introuvable. "
                f"Disponibles: {sorted(self.video_models)}"
            )
        return self.video_models[model_name]
