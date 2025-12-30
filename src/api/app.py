from __future__ import annotations

from collections import defaultdict
from dataclasses import asdict
import os
from pathlib import Path
from typing import Any, Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ..characters.models import (
    CharacterHistory,
    CharacterHistoryEntry,
    CharacterProfile,
    CharacterState,
    CharacterTraits,
)
from ..characters.storage import CharacterRepository
from ..media_generation.models import (
    CharacterProfile as MediaCharacterProfile,
    ImageGenerationConfig,
    MediaAsset,
    MediaResolution,
    PromptSpec,
    SceneSpec,
    StyleProfile,
    VideoGenerationConfig,
)
from ..media_generation.orchestrator import MediaGenerationOrchestrator
from ..media_generation.local import CommandTemplate, LocalImageCommandModel, LocalVideoCommandModel

from .models import RenderAsset, RenderJob
from .storage import RenderRepository

DEFAULT_MODEL_NAME = os.getenv("SEIDRA_DEFAULT_MODEL_NAME", "stub")
LOCAL_IMAGE_COMMAND = os.getenv("SEIDRA_LOCAL_IMAGE_COMMAND")
LOCAL_VIDEO_COMMAND = os.getenv("SEIDRA_LOCAL_VIDEO_COMMAND")
ARTIFACTS_DIR = Path(os.getenv("SEIDRA_ARTIFACTS_DIR", "data/artifacts"))


class CharacterProfilePayload(BaseModel):
    nom: str
    description: str
    voix_narrative: str | None = None
    metadonnees: dict[str, Any] = Field(default_factory=dict)


class CharacterTraitsPayload(BaseModel):
    traits: list[str] = Field(default_factory=list)
    relations: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CharacterHistoryEntryPayload(BaseModel):
    titre: str
    contenu: str
    date: str | None = None


class CharacterHistoryPayload(BaseModel):
    evenements: list[CharacterHistoryEntryPayload] = Field(default_factory=list)


class CharacterStatePayload(BaseModel):
    statut: str
    localisation: str | None = None
    etat_emotionnel: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class CharacterCreateRequest(BaseModel):
    profil: CharacterProfilePayload
    traits: CharacterTraitsPayload | None = None
    historique: CharacterHistoryPayload | None = None
    etat: CharacterStatePayload | None = None


class MediaCharacterProfilePayload(BaseModel):
    identifier: str
    name: str
    description: str
    traits: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class PromptPayload(BaseModel):
    template: str
    variables: dict[str, Any] = Field(default_factory=dict)
    version: str | None = None


class StyleProfilePayload(BaseModel):
    name: str
    description: str | None = None
    tags: list[str] = Field(default_factory=list)


class MediaResolutionPayload(BaseModel):
    width: int
    height: int


class ScenePayload(BaseModel):
    identifier: str
    summary: str
    characters: list[MediaCharacterProfilePayload]
    location: str | None = None
    mood: str | None = None


class ImageConfigPayload(BaseModel):
    resolution: MediaResolutionPayload
    style: StyleProfilePayload | None = None
    steps: int = 30
    guidance_scale: float = 7.5
    seed: int | None = None
    output_format: str = "png"


class VideoConfigPayload(BaseModel):
    resolution: MediaResolutionPayload
    duration_seconds: float
    fps: int = 24
    style: StyleProfilePayload | None = None
    seed: int | None = None
    output_format: str = "mp4"


class RenderRequest(BaseModel):
    type: Literal["image", "video"]
    scene: ScenePayload
    prompt: PromptPayload
    image_config: ImageConfigPayload | None = None
    video_config: VideoConfigPayload | None = None
    model_name: str = DEFAULT_MODEL_NAME


class RenderResponse(BaseModel):
    identifiant: str
    type_rendu: str
    scene: dict[str, Any]
    prompt: dict[str, Any]
    configuration: dict[str, Any]
    modele: str
    statut: str
    asset: dict[str, Any] | None
    cree_le: str
    termine_le: str | None


class BasicPromptRenderer:
    def render(self, scene: SceneSpec, prompt: PromptSpec) -> str:
        variables = defaultdict(
            str,
            {
                **prompt.variables,
                "scene_summary": scene.summary,
                "scene_location": scene.location or "",
                "scene_mood": scene.mood or "",
                "characters": ", ".join(character.name for character in scene.characters),
            },
        )
        return prompt.template.format_map(variables)


class StubImageModel:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: ImageGenerationConfig,
    ) -> MediaAsset:
        self.base_path.mkdir(parents=True, exist_ok=True)
        filename = f"image_{scene.identifier}.{config.output_format}"
        path = self.base_path / filename
        contenu = (
            f"Rendu image pour {scene.identifier}\n"
            f"Prompt: {prompt}\n"
            f"Resolution: {config.resolution.width}x{config.resolution.height}\n"
        )
        path.write_text(contenu, encoding="utf-8")
        return MediaAsset(
            uri=path.as_uri(),
            mime_type=f"image/{config.output_format}",
            metadata={"mode": "stub", "format": config.output_format},
        )


class StubVideoModel:
    def __init__(self, base_path: Path) -> None:
        self.base_path = base_path

    def generate(
        self,
        *,
        scene: SceneSpec,
        prompt: str,
        config: VideoGenerationConfig,
    ) -> MediaAsset:
        self.base_path.mkdir(parents=True, exist_ok=True)
        filename = f"video_{scene.identifier}.{config.output_format}"
        path = self.base_path / filename
        contenu = (
            f"Rendu video pour {scene.identifier}\n"
            f"Prompt: {prompt}\n"
            f"Resolution: {config.resolution.width}x{config.resolution.height}\n"
            f"Duree: {config.duration_seconds}s\n"
        )
        path.write_text(contenu, encoding="utf-8")
        return MediaAsset(
            uri=path.as_uri(),
            mime_type=f"video/{config.output_format}",
            metadata={"mode": "stub", "format": config.output_format},
        )


app = FastAPI(title="SeidraLocal API", version="0.1.0")
character_repo = CharacterRepository()
render_repo = RenderRepository()

orchestrator = MediaGenerationOrchestrator(prompt_renderer=BasicPromptRenderer())
asset_base_path = Path(__file__).resolve().parents[2] / ARTIFACTS_DIR
orchestrator.register_image_model("stub", StubImageModel(asset_base_path))
orchestrator.register_video_model("stub", StubVideoModel(asset_base_path))
if LOCAL_IMAGE_COMMAND:
    orchestrator.register_image_model(
        "local",
        LocalImageCommandModel(
            asset_base_path,
            CommandTemplate(LOCAL_IMAGE_COMMAND),
        ),
    )
if LOCAL_VIDEO_COMMAND:
    orchestrator.register_video_model(
        "local",
        LocalVideoCommandModel(
            asset_base_path,
            CommandTemplate(LOCAL_VIDEO_COMMAND),
        ),
    )


@app.post("/characters", status_code=201)
def creer_personnage(payload: CharacterCreateRequest) -> dict[str, Any]:
    profil = CharacterProfile(**payload.profil.model_dump())
    traits = CharacterTraits(**payload.traits.model_dump()) if payload.traits else None
    historique = (
        CharacterHistory(
            evenements=[
                CharacterHistoryEntry(**entry.model_dump())
                for entry in payload.historique.evenements
            ]
        )
        if payload.historique
        else None
    )
    etat = CharacterState(**payload.etat.model_dump()) if payload.etat else None
    character = character_repo.creer(
        profil,
        traits=traits,
        historique=historique,
        etat=etat,
    )
    return _character_to_payload(character)


@app.get("/characters")
def lister_personnages() -> list[dict[str, Any]]:
    return [_character_to_payload(character) for character in character_repo.lister()]


@app.get("/characters/{identifiant}")
def lire_personnage(identifiant: str) -> dict[str, Any]:
    try:
        character = character_repo.lire(identifiant)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _character_to_payload(character)


@app.post("/renders", response_model=RenderResponse, status_code=201)
def lancer_rendu(payload: RenderRequest) -> RenderResponse:
    if payload.type == "image":
        if payload.image_config is None:
            raise HTTPException(status_code=400, detail="image_config manquant pour un rendu image")
        config = _build_image_config(payload.image_config)
    else:
        if payload.video_config is None:
            raise HTTPException(status_code=400, detail="video_config manquant pour un rendu video")
        config = _build_video_config(payload.video_config)

    scene = _build_scene(payload.scene)
    prompt = _build_prompt(payload.prompt)
    rendu = render_repo.creer(
        type_rendu=payload.type,
        scene=payload.scene.model_dump(),
        prompt=payload.prompt.model_dump(),
        configuration=(payload.image_config or payload.video_config).model_dump(),
        modele=payload.model_name,
    )

    try:
        if payload.type == "image":
            asset = orchestrator.generate_image(
                scene=scene,
                prompt=prompt,
                config=config,
                model_name=payload.model_name,
            )
        else:
            asset = orchestrator.generate_video(
                scene=scene,
                prompt=prompt,
                config=config,
                model_name=payload.model_name,
            )
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    rendu_termine = rendu.terminer(_media_asset_to_render_asset(asset))
    render_repo.mettre_a_jour(rendu_termine)
    return _render_to_response(rendu_termine)


@app.get("/renders")
def lister_rendus() -> list[RenderResponse]:
    return [_render_to_response(rendu) for rendu in render_repo.lister()]


@app.get("/renders/{identifiant}")
def lire_rendu(identifiant: str) -> RenderResponse:
    try:
        rendu = render_repo.lire(identifiant)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return _render_to_response(rendu)


def _character_to_payload(character: Any) -> dict[str, Any]:
    return asdict(character)


def _build_scene(payload: ScenePayload) -> SceneSpec:
    characters = [
        MediaCharacterProfile(**profile.model_dump()) for profile in payload.characters
    ]
    return SceneSpec(
        identifier=payload.identifier,
        summary=payload.summary,
        characters=characters,
        location=payload.location,
        mood=payload.mood,
    )


def _build_prompt(payload: PromptPayload) -> PromptSpec:
    return PromptSpec(**payload.model_dump())


def _build_image_config(payload: ImageConfigPayload) -> ImageGenerationConfig:
    return ImageGenerationConfig(
        resolution=MediaResolution(**payload.resolution.model_dump()),
        style=_build_style(payload.style),
        steps=payload.steps,
        guidance_scale=payload.guidance_scale,
        seed=payload.seed,
        output_format=payload.output_format,
    )


def _build_video_config(payload: VideoConfigPayload) -> VideoGenerationConfig:
    return VideoGenerationConfig(
        resolution=MediaResolution(**payload.resolution.model_dump()),
        duration_seconds=payload.duration_seconds,
        fps=payload.fps,
        style=_build_style(payload.style),
        seed=payload.seed,
        output_format=payload.output_format,
    )


def _build_style(payload: StyleProfilePayload | None) -> StyleProfile | None:
    if payload is None:
        return None
    return StyleProfile(**payload.model_dump())


def _media_asset_to_render_asset(asset: MediaAsset) -> RenderAsset:
    return RenderAsset(uri=asset.uri, mime_type=asset.mime_type, metadata=asset.metadata)


def _render_to_response(rendu: RenderJob) -> RenderResponse:
    asset_payload = asdict(rendu.asset) if rendu.asset else None
    return RenderResponse(
        identifiant=rendu.identifiant,
        type_rendu=rendu.type_rendu,
        scene=dict(rendu.scene),
        prompt=dict(rendu.prompt),
        configuration=dict(rendu.configuration),
        modele=rendu.modele,
        statut=rendu.statut,
        asset=asset_payload,
        cree_le=rendu.cree_le,
        termine_le=rendu.termine_le,
    )
