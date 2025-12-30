# SeidraLocal

## Point d'entrée API (REST)

Une API REST minimale permet de :

- créer des personnages,
- lancer des rendus (image/vidéo) via un modèle factice (`stub`),
- consulter la liste des rendus et leurs résultats.

### Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install fastapi uvicorn "pydantic>=2"
```

### Lancer l'API

Depuis la racine du dépôt :

```bash
uvicorn src.api.app:app --reload
```

L'API est disponible sur `http://127.0.0.1:8000` et la documentation interactive sur
`http://127.0.0.1:8000/docs`.

### Mode 100 % local (CPU/GPU)

Le backend peut exécuter des commandes locales pour générer des images/vidéos sans
appels externes. Définissez les variables d'environnement suivantes :

- `SEIDRA_LOCAL_IMAGE_COMMAND` : commande shell pour la génération d'images.
- `SEIDRA_LOCAL_VIDEO_COMMAND` : commande shell pour la génération de vidéos.
- `SEIDRA_DEFAULT_MODEL_NAME` : modèle par défaut (`local` recommandé).
- `SEIDRA_ARTIFACTS_DIR` : dossier de sortie des artefacts (optionnel).

La commande peut utiliser les variables suivantes :
`{prompt}`, `{output_path}`, `{width}`, `{height}`, `{steps}`, `{guidance_scale}`,
`{seed}`, `{duration_seconds}`, `{fps}`, `{scene_identifier}`, `{style_name}`,
`{style_tags}`.

Exemple (image) :

```bash
export SEIDRA_LOCAL_IMAGE_COMMAND='python ./scripts/generate_image.py --prompt "{prompt}" --out "{output_path}" --width {width} --height {height} --steps {steps} --guidance {guidance_scale}'
export SEIDRA_DEFAULT_MODEL_NAME=local
```

## Exemples d'appels

### Créer un personnage

```bash
curl -X POST http://127.0.0.1:8000/characters \
  -H "Content-Type: application/json" \
  -d ' {
    "profil": {
      "nom": "Lyra",
      "description": "Exploratrice interstellaire",
      "voix_narrative": "Voix posée et curieuse",
      "metadonnees": {"origine": "Colonie Aurore"}
    },
    "traits": {
      "traits": ["audacieuse", "stratégique"],
      "relations": ["Capitaine Nova"],
      "tags": ["protagoniste"]
    },
    "etat": {
      "statut": "en mission",
      "localisation": "Orbites de Kepler-62",
      "etat_emotionnel": "déterminée",
      "variables": {"energie": 82}
    }
  }'
```

### Lister les personnages

```bash
curl http://127.0.0.1:8000/characters
```

### Mettre à jour un personnage (remplacement)

```bash
curl -X PUT http://127.0.0.1:8000/characters/<identifiant> \
  -H "Content-Type: application/json" \
  -d ' {
    "profil": {
      "nom": "Lyra",
      "description": "Exploratrice interstellaire",
      "voix_narrative": "Voix posée et curieuse",
      "metadonnees": {"origine": "Colonie Aurore"}
    },
    "traits": {
      "traits": ["audacieuse", "stratégique"],
      "relations": ["Capitaine Nova"],
      "tags": ["protagoniste"]
    },
    "etat": {
      "statut": "en mission",
      "localisation": "Orbites de Kepler-62",
      "etat_emotionnel": "déterminée",
      "variables": {"energie": 82}
    }
  }'
```

### Mettre à jour un personnage (partiel)

```bash
curl -X PATCH http://127.0.0.1:8000/characters/<identifiant> \
  -H "Content-Type: application/json" \
  -d ' {
    "etat": {
      "statut": "au repos",
      "localisation": "Base Aurore",
      "etat_emotionnel": "soulagée",
      "variables": {"energie": 95}
    }
  }'
```

### Supprimer un personnage

```bash
curl -X DELETE http://127.0.0.1:8000/characters/<identifiant>
```

### Lancer un rendu image

```bash
curl -X POST http://127.0.0.1:8000/renders \
  -H "Content-Type: application/json" \
  -d ' {
    "type": "image",
    "model_name": "stub",
    "scene": {
      "identifier": "scene-001",
      "summary": "Lyra observe une planète luminescente.",
      "location": "Pont d\'observation",
      "mood": "émerveillée",
      "characters": [
        {
          "identifier": "char-lyra",
          "name": "Lyra",
          "description": "Exploratrice interstellaire",
          "traits": ["audacieuse", "stratégique"],
          "metadata": {"role": "protagoniste"}
        }
      ]
    },
    "prompt": {
      "template": "{characters} dans {scene_location} avec une ambiance {scene_mood}.",
      "variables": {"eclairage": "bioluminescent"},
      "version": "v1"
    },
    "image_config": {
      "resolution": {"width": 1024, "height": 768},
      "style": {"name": "cinématique", "tags": ["sci-fi", "brume"]},
      "steps": 28,
      "guidance_scale": 7.0,
      "output_format": "png"
    }
  }'
```

### Lancer un rendu vidéo

```bash
curl -X POST http://127.0.0.1:8000/renders \
  -H "Content-Type: application/json" \
  -d ' {
    "type": "video",
    "model_name": "stub",
    "scene": {
      "identifier": "scene-002",
      "summary": "Lyra active les moteurs de la navette.",
      "location": "Hangar",
      "mood": "tendue",
      "characters": [
        {
          "identifier": "char-lyra",
          "name": "Lyra",
          "description": "Exploratrice interstellaire",
          "traits": ["audacieuse"],
          "metadata": {"role": "protagoniste"}
        }
      ]
    },
    "prompt": {
      "template": "{characters} se prépare dans {scene_location}.",
      "variables": {"tempo": "rapide"},
      "version": "v1"
    },
    "video_config": {
      "resolution": {"width": 1280, "height": 720},
      "duration_seconds": 6.5,
      "fps": 24,
      "style": {"name": "dramatique", "tags": ["contraste", "motion"]},
      "output_format": "mp4"
    }
  }'
```

### Consulter les rendus

```bash
curl http://127.0.0.1:8000/renders
```

### Consulter un rendu précis

```bash
curl http://127.0.0.1:8000/renders/<identifiant>
```
