# 🏢 Système de Persistance Backend - Interface CAH

## 📋 Vue d'ensemble

Le backend FastAPI utilise maintenant un système de persistance basé sur un fichier JSON pour sauvegarder les immeubles créés par les utilisateurs.

## 🗂️ Structure des Données

### Fichier de stockage
- **Fichier** : `buildings_data.json`
- **Format** : JSON avec structure :
  ```json
  {
    "buildings": [...],
    "next_id": 4
  }
  ```

### Types d'immeubles
1. **Immeubles par défaut** (ID 1-3) : Données de démonstration, non modifiables
2. **Immeubles utilisateur** (ID ≥ 4) : Créés via l'interface, modifiables et supprimables

## 🔧 Routes API

### GET /api/buildings
- **Description** : Récupère tous les immeubles (défaut + sauvegardés)
- **Réponse** : Liste combinée des immeubles

### GET /api/buildings/{id}
- **Description** : Récupère un immeuble spécifique
- **Paramètre** : `id` (entier)
- **Réponse** : Données de l'immeuble ou erreur 404

### POST /api/buildings
- **Description** : Crée un nouvel immeuble
- **Body** : Données de l'immeuble (format BuildingCreate)
- **Réponse** : Immeuble créé avec ID assigné

### PUT /api/buildings/{id}
- **Description** : Met à jour un immeuble existant
- **Paramètre** : `id` (entier)
- **Body** : Données partielles à mettre à jour
- **Restrictions** : Immeubles par défaut (ID 1-3) non modifiables
- **Réponse** : Immeuble mis à jour ou erreur 403

### DELETE /api/buildings/{id}
- **Description** : Supprime un immeuble
- **Paramètre** : `id` (entier)
- **Restrictions** : Immeubles par défaut (ID 1-3) non supprimables
- **Réponse** : Message de confirmation ou erreur 403

## 🛡️ Validation des Données

### Modèles Pydantic
- **Building** : Modèle complet avec tous les champs
- **BuildingCreate** : Modèle pour la création (sans ID)
- **BuildingUpdate** : Modèle pour la mise à jour (champs optionnels)

### Sous-modèles
- **Address** : Adresse complète (rue, ville, province, code postal, pays)
- **Characteristics** : Caractéristiques physiques (parking, ascenseur, etc.)
- **Financials** : Informations financières (prix, mise de fond, taux, valeur)
- **Contacts** : Contacts (propriétaire, banque, entrepreneur)

## 🔄 Fonctionnement

### Chargement des données
1. Lecture du fichier `buildings_data.json`
2. Si le fichier n'existe pas → structure vide avec `next_id: 4`
3. Combinaison avec les 3 immeubles par défaut

### Sauvegarde des données
1. Modification des données en mémoire
2. Écriture complète du fichier JSON
3. Gestion d'erreurs avec rollback

### Gestion des IDs
- **IDs 1-3** : Réservés aux immeubles par défaut
- **ID ≥ 4** : Assignés automatiquement aux nouveaux immeubles
- **next_id** : Compteur auto-incrémenté

## 🧪 Tests

### Script de test
```bash
cd backend
python test_api.py
```

### Tests manuels
```bash
# Démarrer le serveur
uvicorn main:app --reload

# Tester les routes
curl http://localhost:8000/api/buildings
curl -X POST http://localhost:8000/api/buildings -H "Content-Type: application/json" -d '{...}'
```

## 📁 Structure des fichiers

```
backend/
├── main.py              # Application FastAPI principale
├── buildings_data.json  # Données persistées (généré automatiquement)
├── test_api.py          # Script de test des routes
├── .gitignore           # Exclut buildings_data.json du versioning
└── README_PERSISTENCE.md
```

## 🚀 Déploiement

### Local
```bash
cd backend
pip install fastapi uvicorn
uvicorn main:app --reload
```

### Production
- Le fichier `buildings_data.json` sera créé automatiquement
- Permissions d'écriture requises dans le répertoire
- Sauvegarde régulière du fichier recommandée

## 🔐 Sécurité

### Protections implémentées
- Validation stricte avec Pydantic
- Protection des immeubles par défaut
- Gestion d'erreurs robuste
- Encodage UTF-8 pour les caractères spéciaux

### Limitations actuelles
- Pas d'authentification utilisateur
- Pas de concurrence (accès simultané)
- Stockage en fichier unique (pas de base de données)

## 🔄 Migration future

Ce système JSON peut facilement être migré vers une vraie base de données :
- PostgreSQL avec SQLAlchemy
- MongoDB pour NoSQL
- SQLite pour simplicité

Les modèles Pydantic restent compatibles avec tous ces systèmes. 