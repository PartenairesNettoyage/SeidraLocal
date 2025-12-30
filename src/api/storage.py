from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .models import RenderAsset, RenderJob


class RenderRepository:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(__file__).resolve().parents[2] / "data" / "renders"
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)

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
        if not self._chemin_rendu(rendu.identifiant).exists():
            raise FileNotFoundError(f"Rendu introuvable: {rendu.identifiant}")
        self._enregistrer(rendu)
        return rendu

    def lire(self, identifiant: str) -> RenderJob:
        chemin = self._chemin_latest(identifiant)
        if not chemin.exists():
            raise FileNotFoundError(f"Rendu introuvable: {identifiant}")
        return self._charger_depuis_fichier(chemin)

    def lister(self) -> Iterable[RenderJob]:
        for dossier in sorted(self.base_path.iterdir()):
            if dossier.is_dir():
                latest = dossier / "latest.json"
                if latest.exists():
                    yield self._charger_depuis_fichier(latest)

    def _enregistrer(self, rendu: RenderJob) -> None:
        dossier = self._chemin_rendu(rendu.identifiant)
        versions = dossier / "versions"
        versions.mkdir(parents=True, exist_ok=True)

        horodatage = datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        version_path = versions / f"{horodatage}.json"
        latest_path = dossier / "latest.json"

        payload = _rendu_to_dict(rendu)
        version_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        latest_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def _chemin_rendu(self, identifiant: str) -> Path:
        return self.base_path / identifiant

    def _chemin_latest(self, identifiant: str) -> Path:
        return self._chemin_rendu(identifiant) / "latest.json"

    def _charger_depuis_fichier(self, chemin: Path) -> RenderJob:
        contenu = json.loads(chemin.read_text(encoding="utf-8"))
        return _rendu_from_dict(contenu)


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
