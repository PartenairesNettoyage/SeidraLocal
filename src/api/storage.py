from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .models import RenderAsset, RenderJob


class RenderRepository:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(__file__).resolve().parents[2] / "data"
        self.store_path = _resolve_store_path(base_path, "renders.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, object]] = {}
        self._charger()

    def creer(self, *, type_rendu: str, scene: dict[str, object], prompt: dict[str, object],
              configuration: dict[str, object], modele: str) -> RenderJob:
        identifiant = str(uuid4())
        rendu = RenderJob(
            identifiant=identifiant,
            type_rendu=type_rendu,
            scene=scene,
            prompt=prompt,
            configuration=configuration,
            modele=modele,
            statut="en_cours",
        )
        self._enregistrer(rendu)
        return rendu

    def mettre_a_jour(self, rendu: RenderJob) -> RenderJob:
        if rendu.identifiant not in self._cache:
            raise FileNotFoundError(f"Rendu introuvable: {rendu.identifiant}")
        self._enregistrer(rendu)
        return rendu

    def lire(self, identifiant: str) -> RenderJob:
        payload = self._cache.get(identifiant)
        if payload is None:
            raise FileNotFoundError(f"Rendu introuvable: {identifiant}")
        return _rendu_from_dict(payload)

    def lister(self) -> Iterable[RenderJob]:
        for payload in self._cache.values():
            yield _rendu_from_dict(payload)

    def _enregistrer(self, rendu: RenderJob) -> None:
        payload = _rendu_to_dict(rendu)
        self._cache[rendu.identifiant] = payload
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


def _rendu_to_dict(rendu: RenderJob) -> dict[str, object]:
    return asdict(rendu)


def _rendu_from_dict(data: dict[str, object]) -> RenderJob:
    asset_data = data.get("asset")
    asset = RenderAsset(**asset_data) if asset_data else None
    return RenderJob(
        identifiant=data["identifiant"],
        type_rendu=data["type_rendu"],
        scene=data["scene"],
        prompt=data["prompt"],
        configuration=data["configuration"],
        modele=data["modele"],
        statut=data.get("statut", "en_cours"),
        asset=asset,
        cree_le=data.get("cree_le", datetime.utcnow().isoformat()),
        termine_le=data.get("termine_le"),
    )


def _resolve_store_path(base_path: Path, filename: str) -> Path:
    if base_path.suffix == ".json":
        return base_path
    return base_path / filename
