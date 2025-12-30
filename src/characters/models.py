from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class CharacterProfile(BaseModel):
    model_config = ConfigDict(frozen=True)
    nom: str
    description: str
    voix_narrative: str | None = None
    metadonnees: dict[str, Any] = Field(default_factory=dict)


class CharacterTraits(BaseModel):
    model_config = ConfigDict(frozen=True)
    traits: list[str] = Field(default_factory=list)
    relations: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


class CharacterHistoryEntry(BaseModel):
    model_config = ConfigDict(frozen=True)
    titre: str
    contenu: str
    date: str | None = None


class CharacterHistory(BaseModel):
    model_config = ConfigDict(frozen=True)
    evenements: list[CharacterHistoryEntry] = Field(default_factory=list)


class CharacterState(BaseModel):
    model_config = ConfigDict(frozen=True)
    statut: str
    localisation: str | None = None
    etat_emotionnel: str | None = None
    variables: dict[str, Any] = Field(default_factory=dict)


class Character(BaseModel):
    model_config = ConfigDict(frozen=True)
    identifiant: str
    profil: CharacterProfile
    traits: CharacterTraits = Field(default_factory=CharacterTraits)
    historique: CharacterHistory = Field(default_factory=CharacterHistory)
    etat: CharacterState | None = None
    cree_le: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    modifie_le: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    version_schema: int = 1

    def mettre_a_jour_timestamp(self) -> "Character":
        return self.model_copy(update={"modifie_le": datetime.utcnow().isoformat()})
