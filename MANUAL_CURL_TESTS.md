# Tests manuels rapides (curl)

Ces exemples supposent que l'API tourne sur `http://localhost:8000`.

## Personnages

### Create
```bash
curl -sS -X POST http://localhost:8000/characters \
  -H "Content-Type: application/json" \
  -d '{
    "profil": {
      "nom": "Aline",
      "description": "Exploratrice",
      "voix_narrative": "calme",
      "metadonnees": {"origine": "Seidra"}
    },
    "traits": {"traits": ["curieuse"], "relations": [], "tags": ["test"]},
    "historique": {"evenements": [{"titre": "Arrivée", "contenu": "Débarque en ville"}]},
    "etat": {"statut": "actif", "localisation": "port", "etat_emotionnel": "sereine"}
  }'
```

### List
```bash
curl -sS http://localhost:8000/characters
```

### Get
```bash
curl -sS http://localhost:8000/characters/{identifiant}
```

### Update
```bash
curl -sS -X PATCH http://localhost:8000/characters/{identifiant} \
  -H "Content-Type: application/json" \
  -d '{
    "profil": {"nom": "Aline", "description": "Exploratrice aguerrie"},
    "traits": {"traits": ["curieuse", "prudente"]}
  }'
```

### Delete
```bash
curl -sS -X DELETE http://localhost:8000/characters/{identifiant}
```

## Rendus

### Create
```bash
curl -sS -X POST http://localhost:8000/renders \
  -H "Content-Type: application/json" \
  -d '{
    "type": "image",
    "scene": {
      "identifier": "scene-1",
      "summary": "Une place au crépuscule",
      "characters": [],
      "location": "place centrale",
      "mood": "paisible"
    },
    "prompt": {
      "template": "Décris {scene_summary}",
      "variables": {}
    },
    "image_config": {
      "resolution": {"width": 1024, "height": 768},
      "style": {"name": "cinematographique"},
      "seed": 42,
      "output_format": "png"
    },
    "model_name": "stub"
  }'
```

### List
```bash
curl -sS http://localhost:8000/renders
```

### Get
```bash
curl -sS http://localhost:8000/renders/{identifiant}
```

### Update
```bash
curl -sS -X PATCH http://localhost:8000/renders/{identifiant} \
  -H "Content-Type: application/json" \
  -d '{
    "statut": "termine",
    "asset": {
      "uri": "file://data/artifacts/exemple.png",
      "mime_type": "image/png",
      "metadata": {"source": "manuel"}
    }
  }'
```

### Delete
```bash
curl -sS -X DELETE http://localhost:8000/renders/{identifiant}
```
