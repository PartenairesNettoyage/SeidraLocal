from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Mapping


@dataclass(frozen=True)
class RenderAsset:
    uri: str
    mime_type: str
    metadata: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class RenderJob:
    identifiant: str
    type_rendu: str
    scene: Mapping[str, Any]
    prompt: Mapping[str, Any]
    configuration: Mapping[str, Any]
    modele: str
    statut: str
    asset: RenderAsset | None = None
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    termine_le: str | None = None

    def terminer(self, asset: RenderAsset) -> "RenderJob":
        return RenderJob(
            identifiant=self.identifiant,
            type_rendu=self.type_rendu,
            scene=self.scene,
            prompt=self.prompt,
            configuration=self.configuration,
            modele=self.modele,
            statut="termine",
            asset=asset,
            cree_le=self.cree_le,
            termine_le=datetime.utcnow().isoformat(),
        )
