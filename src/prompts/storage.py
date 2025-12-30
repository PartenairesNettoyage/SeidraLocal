from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Iterable
from uuid import uuid4

from .models import Prompt, PromptExecution, PromptVersion, valider_template, valider_variables


class PromptRepository:
    def __init__(self, base_path: Path | None = None) -> None:
        if base_path is None:
            base_path = Path(__file__).resolve().parents[2] / "data"
        self.store_path = _resolve_store_path(base_path, "prompts.json")
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[str, dict[str, object]] = {}
        self._charger()

    def creer(self, nom: str, *, template: str, variables: dict[str, object] | None = None) -> Prompt:
        if not nom or not nom.strip():
            raise ValueError("Le nom du prompt est obligatoire.")
        variables = dict(variables or {})
        valider_template(template)
        valider_variables(template, variables)
        identifiant = str(uuid4())
        version = PromptVersion(template=template, variables=variables, version=1)
        prompt = Prompt(
            identifiant=identifiant,
            nom=nom,
            versions=[version],
        )
        self._enregistrer(prompt)
        return prompt

    def lire(self, identifiant: str) -> Prompt:
        payload = self._cache.get(identifiant)
        if payload is None:
            raise FileNotFoundError(f"Prompt introuvable: {identifiant}")
        return _prompt_from_dict(payload)

    def lister(self) -> Iterable[Prompt]:
        for payload in self._cache.values():
            yield _prompt_from_dict(payload)

    def mettre_a_jour(
        self,
        identifiant: str,
        *,
        template: str,
        variables: dict[str, object] | None = None,
    ) -> Prompt:
        prompt = self.lire(identifiant)
        variables = dict(variables or {})
        valider_template(template)
        valider_variables(template, variables)
        nouvelle_version = PromptVersion(
            template=template,
            variables=variables,
            version=prompt.derniere_version().version + 1,
        )
        prompt = Prompt(
            identifiant=prompt.identifiant,
            nom=prompt.nom,
            versions=[*prompt.versions, nouvelle_version],
            executions=list(prompt.executions),
            cree_le=prompt.cree_le,
            modifie_le=datetime.utcnow().isoformat(),
            version_schema=prompt.version_schema,
        )
        self._enregistrer(prompt)
        return prompt

    def enregistrer_execution(
        self,
        identifiant: str,
        *,
        version: int | None = None,
        contexte: dict[str, object] | None = None,
    ) -> PromptExecution:
        prompt = self.lire(identifiant)
        cible_version = version or prompt.derniere_version().version
        if all(entree.version != cible_version for entree in prompt.versions):
            raise ValueError(
                f"Version de prompt inconnue: {cible_version} pour {identifiant}."
            )
        execution = PromptExecution(
            identifiant=str(uuid4()),
            version=cible_version,
            contexte=dict(contexte or {}),
        )
        prompt = Prompt(
            identifiant=prompt.identifiant,
            nom=prompt.nom,
            versions=list(prompt.versions),
            executions=[*prompt.executions, execution],
            cree_le=prompt.cree_le,
            modifie_le=datetime.utcnow().isoformat(),
            version_schema=prompt.version_schema,
        )
        self._enregistrer(prompt)
        return execution

    def _enregistrer(self, prompt: Prompt) -> None:
        payload = _prompt_to_dict(prompt)
        self._cache[prompt.identifiant] = payload
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


def _prompt_to_dict(prompt: Prompt) -> dict[str, object]:
    return asdict(prompt)


def _prompt_from_dict(data: dict[str, object]) -> Prompt:
    versions_data = data.get("versions", [])
    versions = [PromptVersion(**version) for version in versions_data]
    executions_data = data.get("executions", [])
    executions = [PromptExecution(**execution) for execution in executions_data]
    return Prompt(
        identifiant=data["identifiant"],
        nom=data["nom"],
        versions=versions,
        executions=executions,
        cree_le=data.get("cree_le", datetime.utcnow().isoformat()),
        modifie_le=data.get("modifie_le", datetime.utcnow().isoformat()),
        version_schema=data.get("version_schema", 1),
    )


def _resolve_store_path(base_path: Path, filename: str) -> Path:
    if base_path.suffix == ".json":
        return base_path
    return base_path / filename
