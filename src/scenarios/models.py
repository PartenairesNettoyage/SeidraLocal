from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


def _valider_texte(champ: str, valeur: str) -> None:
    if not valeur or not valeur.strip():
        raise ValueError(f"Le champ '{champ}' doit être renseigné.")


def valider_personnages_ids(personnages_ids: list[str]) -> None:
    for identifiant in personnages_ids:
        if not isinstance(identifiant, str) or not identifiant.strip():
            raise ValueError("Chaque identifiant de personnage doit être une chaîne non vide.")


def valider_scene(scene: Scene) -> None:
    _valider_texte("titre", scene.titre)
    _valider_texte("resume", scene.resume)
    valider_personnages_ids(scene.personnages_ids)


def valider_acte(acte: Acte) -> None:
    _valider_texte("titre", acte.titre)
    if not acte.scenes:
        raise ValueError("Chaque acte doit contenir au moins une scène.")
    for scene in acte.scenes:
        valider_scene(scene)


def valider_scenario(scenario: Scenario) -> None:
    _valider_texte("titre", scenario.titre)
    if not scenario.actes:
        raise ValueError("Le scénario doit contenir au moins un acte.")
    for acte in scenario.actes:
        valider_acte(acte)


@dataclass(frozen=True)
class Scene:
    identifiant: str
    titre: str
    resume: str
    personnages_ids: list[str] = field(default_factory=list)
    metadonnees: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Acte:
    identifiant: str
    titre: str
    scenes: list[Scene] = field(default_factory=list)
    metadonnees: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class Scenario:
    identifiant: str
    titre: str
    description: str | None = None
    actes: list[Acte] = field(default_factory=list)
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    modifie_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version_schema: int = 1

    def mettre_a_jour_timestamp(self) -> "Scenario":
        return Scenario(
            identifiant=self.identifiant,
            titre=self.titre,
            description=self.description,
            actes=self.actes,
            cree_le=self.cree_le,
            modifie_le=datetime.utcnow().isoformat(),
            version_schema=self.version_schema,
        )
