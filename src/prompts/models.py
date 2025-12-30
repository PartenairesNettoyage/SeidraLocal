from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from string import Formatter
from typing import Any


def _extraire_variables(template: str) -> set[str]:
    variables = set()
    for _, field_name, _, _ in Formatter().parse(template):
        if not field_name:
            continue
        racine = field_name.split(".")[0].split("[")[0]
        if racine:
            variables.add(racine)
    return variables


def valider_template(template: str) -> None:
    if not template or not template.strip():
        raise ValueError("Le template du prompt doit être renseigné.")


def valider_variables(template: str, variables: dict[str, Any]) -> None:
    for cle in variables.keys():
        if not isinstance(cle, str) or not cle.strip():
            raise ValueError("Chaque variable doit avoir une clé de type chaîne non vide.")
    manquantes = _extraire_variables(template) - set(variables.keys())
    if manquantes:
        raise ValueError(
            "Variables manquantes pour le template: "
            + ", ".join(sorted(manquantes))
        )


@dataclass(frozen=True)
class PromptVersion:
    template: str
    variables: dict[str, Any] = field(default_factory=dict)
    version: int = 1
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass(frozen=True)
class PromptExecution:
    identifiant: str
    version: int
    contexte: dict[str, Any] = field(default_factory=dict)
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())


@dataclass(frozen=True)
class Prompt:
    identifiant: str
    nom: str
    versions: list[PromptVersion] = field(default_factory=list)
    executions: list[PromptExecution] = field(default_factory=list)
    cree_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    modifie_le: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    version_schema: int = 1

    def derniere_version(self) -> PromptVersion:
        if not self.versions:
            raise ValueError("Le prompt ne contient aucune version.")
        return self.versions[-1]
