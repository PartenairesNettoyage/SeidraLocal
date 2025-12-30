from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .models import (
    Character,
    CharacterHistory,
    CharacterHistoryEntry,
    CharacterProfile,
    CharacterState,
    CharacterTraits,
)


class CharacterRepository:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(__file__).resolve().parents[2] / "data" / "characters"
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

    def creer(self, profil: CharacterProfile, *, traits: CharacterTraits | None = None,
              historique: CharacterHistory | None = None,
              etat: CharacterState | None = None) -> Character:
        identifiant = str(uuid4())
        character = Character(
            identifiant=identifiant,
            profil=profil,
            traits=traits or CharacterTraits(),
            historique=historique or CharacterHistory(),
            etat=etat,
        )
        self._enregistrer(character)
        return character

    def lire(self, identifiant: str) -> Character:
        chemin = self._chemin_latest(identifiant)
        if not chemin.exists():
            raise FileNotFoundError(f"Personnage introuvable: {identifiant}")
        return self._charger_depuis_fichier(chemin)

    def mettre_a_jour(self, character: Character) -> Character:
        if not self._chemin_personnage(character.identifiant).exists():
            raise FileNotFoundError(
                f"Impossible de mettre à jour un personnage inexistant: {character.identifiant}"
            )
        character = character.mettre_a_jour_timestamp()
        self._enregistrer(character)
        return character

    def supprimer(self, identifiant: str) -> None:
        dossier = self._chemin_personnage(identifiant)
        if not dossier.exists():
            raise FileNotFoundError(f"Personnage introuvable: {identifiant}")
        for chemin in dossier.rglob("*"):
            if chemin.is_file():
                chemin.unlink()
        for chemin in sorted(dossier.rglob("*"), reverse=True):
            if chemin.is_dir():
                chemin.rmdir()
        dossier.rmdir()

    def lister(self) -> Iterable[Character]:
        for dossier in sorted(self.base_path.iterdir()):
            if dossier.is_dir():
                latest = dossier / "latest.json"
                if latest.exists():
                    yield self._charger_depuis_fichier(latest)

    def _enregistrer(self, character: Character) -> None:
        dossier = self._chemin_personnage(character.identifiant)
        versions = dossier / "versions"
        versions.mkdir(parents=True, exist_ok=True)

        horodatage = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        version_path = versions / f"{horodatage}.json"
        latest_path = dossier / "latest.json"

        payload = _character_to_dict(character)
        version_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _chemin_personnage(self, identifiant: str) -> Path:
        return self.base_path / identifiant

    def _chemin_latest(self, identifiant: str) -> Path:
        return self._chemin_personnage(identifiant) / "latest.json"

    def _charger_depuis_fichier(self, chemin: Path) -> Character:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
        return _character_from_dict(contenu)


def _character_to_dict(character: Character) -> dict[str, object]:
    return asdict(character)


def _character_from_dict(data: dict[str, object]) -> Character:
    profil = CharacterProfile(**data["profil"])
    traits = CharacterTraits(**data.get("traits", {}))
    historique_data = data.get("historique", {})
    historique = CharacterHistory(
        evenements=[CharacterHistoryEntry(**entry) for entry in historique_data.get("evenements", [])]
    )
    etat_data = data.get("etat")
    etat = CharacterState(**etat_data) if etat_data else None
    return Character(
        identifiant=data["identifiant"],
        profil=profil,
        traits=traits,
        historique=historique,
        etat=etat,
        cree_le=data.get("cree_le", datetime.utcnow().isoformat()),
        modifie_le=data.get("modifie_le", datetime.utcnow().isoformat()),
        version_schema=data.get("version_schema", 1),
    )
