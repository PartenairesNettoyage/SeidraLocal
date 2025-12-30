from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping

from pydantic import BaseModel, ConfigDict, Field


class RenderAsset(BaseModel):
    model_config = ConfigDict(frozen=True)
    uri: str
    mime_type: str
    metadata: Mapping[str, Any] = Field(default_factory=dict)


class RenderJob(BaseModel):
    model_config = ConfigDict(frozen=True)
    identifiant: str
    type_rendu: str
    scene: Mapping[str, Any]
    prompt: Mapping[str, Any]
    configuration: Mapping[str, Any]
    modele: str
    statut: str
    asset: RenderAsset | None = None
    cree_le: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    termine_le: str | None = None

    def terminer(self, asset: RenderAsset) -> "RenderJob":
        return self.model_copy(
            update={
                "statut": "termine",
                "asset": asset,
                "termine_le": datetime.utcnow().isoformat(),
            }
        )
