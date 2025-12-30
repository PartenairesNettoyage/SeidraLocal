# Spécifications fonctionnelles

## Objectif
Décrire les exigences fonctionnelles et non fonctionnelles pour la création et la gestion de contenus narratifs multimédias autour de personnages, avec persistance et génération guidée par prompts.

## Périmètre
- Création de personnages (fiches, attributs, relations).
- Persistance des données (stockage et récupération).
- Gestion des prompts (modèles, variables, versioning).
- Scénarisation (structure narrative, arcs, scènes).
- Entrées/sorties multimédias (images, vidéos).

## Cas d’usage
### 1) Création de personnages
- En tant qu’utilisateur, je peux créer un personnage avec un nom, une description, des traits, une voix narrative et des métadonnées.
- En tant qu’utilisateur, je peux modifier ou supprimer un personnage.

**Critères d’acceptation**
- La création valide la présence d’un nom et d’une description minimale.
- Les champs optionnels (traits, relations, tags) sont persistés correctement.
- Les modifications sont reflétées dans les listes et la fiche personnage.

### 2) Persistance
- En tant qu’utilisateur, je peux sauvegarder et recharger des personnages, scénarios et prompts.
- En tant qu’administrateur, je peux exporter/importer un jeu de données.

**Critères d’acceptation**
- Les données créées sont récupérables après redémarrage de l’application.
- L’export produit un fichier lisible et réimportable sans perte.
- L’import gère les collisions d’identifiants (fusion ou remplacement configurables).

### 3) Prompts
- En tant qu’utilisateur, je peux créer des templates de prompts avec variables.
- En tant qu’utilisateur, je peux versionner un prompt et revenir à une version antérieure.

**Critères d’acceptation**
- Les variables de prompts sont détectées et validées avant exécution.
- Chaque modification crée une nouvelle version horodatée.
- L’exécution d’un prompt journalise l’entrée et la sortie associées.

### 4) Scénarisation
- En tant qu’utilisateur, je peux créer un scénario composé d’actes, scènes et dialogues.
- En tant qu’utilisateur, je peux lier des personnages à des scènes.

**Critères d’acceptation**
- Un scénario contient au moins un acte et une scène.
- Chaque scène référence des personnages existants.
- Les modifications d’un personnage se reflètent dans les scènes liées.

## Formats d’entrée/sortie
### Entrées
- **Texte** : prompts, fiches personnage, scripts.
- **Images** : PNG, JPG (personnages, décors).
- **Vidéos** : MP4, WebM (références ou rendus).

### Sorties
- **Texte** : scripts, résumés, journaux d’exécution.
- **Images** : PNG, JPG (concepts, scènes).
- **Vidéos** : MP4, WebM (scènes scénarisées).

**Critères d’acceptation**
- L’application valide le type MIME et la taille maximale par média.
- Les sorties incluent les métadonnées minimales (date, source, version).

## Contraintes non fonctionnelles
### Stockage
- Stockage persistant local ou distant (configurable).
- Chiffrement au repos pour les données sensibles.

**Critères d’acceptation**
- Les données sont conservées selon une politique de rétention définie.
- Les sauvegardes peuvent être restaurées sur un nouvel environnement.

### Coûts
- Suivi des coûts par exécution (tokens, génération d’images/vidéos).
- Budget mensuel paramétrable avec alertes.

**Critères d’acceptation**
- Un tableau récapitulatif indique la consommation par projet.
- Un seuil configurable déclenche une alerte.

### Performances
- Temps de chargement acceptable des fiches et scénarios.
- Mise en cache des ressources fréquemment utilisées.

**Critères d’acceptation**
- 95 % des opérations de lecture sont servies en moins de 200 ms.
- Les opérations d’écriture critiques répondent en moins de 500 ms.

## Hypothèses et exclusions
- La génération finale (images/vidéos) dépend de services externes.
- La qualité créative est subjective et non garantie.

## Glossaire
- **Prompt** : instruction textuelle structurée pour guider une génération.
- **Scénarisation** : organisation narrative en actes, scènes et dialogues.
- **Persistance** : sauvegarde durable des données.
