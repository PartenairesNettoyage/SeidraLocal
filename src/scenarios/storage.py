from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .models import Acte, Scene, Scenario, valider_scenario


class ScenarioRepository:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(__file__).resolve().parents[2] / "data"
        self.store_path = _resolve_store_path(base_path, "scenarios.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, object]] = {}
        self._charger()

    def creer(self, titre: str, *, description: str | None = None, actes: list[Acte]) -> Scenario:
        identifiant = str(uuid4())
        scenario = Scenario(
            identifiant=identifiant,
            titre=titre,
            description=description,
            actes=actes,
        )
        valider_scenario(scenario)
        self._enregistrer(scenario)
        return scenario

    def lire(self, identifiant: str) -> Scenario:
        payload = self._cache.get(identifiant)
        if payload is None:
            raise FileNotFoundError(f"Scénario introuvable: {identifiant}")
        return _scenario_from_dict(payload)

    def lister(self) -> Iterable[Scenario]:
        for payload in self._cache.values():
            yield _scenario_from_dict(payload)

    def mettre_a_jour(self, scenario: Scenario) -> Scenario:
        if scenario.identifiant not in self._cache:
            raise FileNotFoundError(
                f"Impossible de mettre à jour un scénario inexistant: {scenario.identifiant}"
            )
        valider_scenario(scenario)
        scenario = scenario.mettre_a_jour_timestamp()
        self._enregistrer(scenario)
        return scenario

    def _enregistrer(self, scenario: Scenario) -> None:
        payload = _scenario_to_dict(scenario)
        self._cache[scenario.identifiant] = payload
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


def _scenario_to_dict(scenario: Scenario) -> dict[str, object]:
    return asdict(scenario)


def _scenario_from_dict(data: dict[str, object]) -> Scenario:
    actes_data = data.get("actes", [])
    actes = []
    for acte_data in actes_data:
        scenes_data = acte_data.get("scenes", [])
        scenes = [Scene(**scene_data) for scene_data in scenes_data]
        actes.append(
            Acte(
                identifiant=acte_data["identifiant"],
                titre=acte_data["titre"],
                scenes=scenes,
                metadonnees=acte_data.get("metadonnees", {}),
            )
        )
    return Scenario(
        identifiant=data["identifiant"],
        titre=data["titre"],
        description=data.get("description"),
        actes=actes,
        cree_le=data.get("cree_le", datetime.utcnow().isoformat()),
        modifie_le=data.get("modifie_le", datetime.utcnow().isoformat()),
        version_schema=data.get("version_schema", 1),
    )


def _resolve_store_path(base_path: Path, filename: str) -> Path:
    if base_path.suffix == ".json":
        return base_path
    return base_path / filename
