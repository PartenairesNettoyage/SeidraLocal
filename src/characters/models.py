from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class CharacterProfile:
    nom: str
    description: str
    voix_narrative: str | None = None
    metadonnees: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CharacterTraits:
    traits: list[str] = field(default_factory=list)
    relations: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CharacterHistoryEntry:
    titre: str
    contenu: str
    date: str | None = None


@dataclass(frozen=True)
class CharacterHistory:
    evenements: list[CharacterHistoryEntry] = field(default_factory=list)


@dataclass(frozen=True)
class CharacterState:
    statut: str
    localisation: str | None = None
    etat_emotionnel: str | None = None
    variables: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Character:
    identifiant: str
    profil: CharacterProfile
    traits: CharacterTraits = field(default_factory=CharacterTraits)
    historique: CharacterHistory = field(default_factory=CharacterHistory)
    etat: CharacterState | None = None
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    modifie_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version_schema: int = 1

    def mettre_a_jour_timestamp(self) -> "Character":
        return Character(
            identifiant=self.identifiant,
            profil=self.profil,
            traits=self.traits,
            historique=self.historique,
            etat=self.etat,
            cree_le=self.cree_le,
            modifie_le=datetime.utcnow().isoformat(),
            version_schema=self.version_schema,
        )
