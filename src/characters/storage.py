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
            base_path = Path(__file__).resolve().parents[2] / "data"
        self.store_path = _resolve_store_path(base_path, "characters.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, object]] = {}
        self._charger()

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
        payload = self._cache.get(identifiant)
        if payload is None:
            raise FileNotFoundError(f"Personnage introuvable: {identifiant}")
        return _character_from_dict(payload)

    def mettre_a_jour(self, character: Character) -> Character:
        if character.identifiant not in self._cache:
            raise FileNotFoundError(
                f"Impossible de mettre à jour un personnage inexistant: {character.identifiant}"
            )
        character = character.mettre_a_jour_timestamp()
        self._enregistrer(character)
        return character

    def supprimer(self, identifiant: str) -> None:
        if identifiant not in self._cache:
            raise FileNotFoundError(f"Personnage introuvable: {identifiant}")
        del self._cache[identifiant]
        self._sauvegarder()

    def lister(self) -> Iterable[Character]:
        for payload in self._cache.values():
            yield _character_from_dict(payload)

    def _enregistrer(self, character: Character) -> None:
        payload = _character_to_dict(character)
        self._cache[character.identifiant] = payload
        self._sauvegarder()

    def _charger(self) -> None:
        if not self.store_path.exists():
            self._cache = {}
            return
        contenu = json.loads(self.store_path.read_text(encoding="utf-8"))
        if isinstance(contenu, dict):
            items = contenu.get("items", contenu)
            if isinstance(items, dict):
                self._cache = dict(items)
                return
        self._cache = {}

    def _sauvegarder(self) -> None:
        payload = {"items": self._cache}
        self.store_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )


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


def _resolve_store_path(base_path: Path, filename: str) -> Path:
    if base_path.suffix == ".json":
        return base_path
    return base_path / filename
