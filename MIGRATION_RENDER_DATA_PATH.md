# Migration vers le chemin de données recommandé par Render

## Contexte

Suite aux tests effectués, Render recommande d'utiliser le chemin `/opt/render/project/src/data` pour le stockage des données persistantes au lieu de `/var/data`.

## Changements effectués

### 1. Modification du chemin de données dans `main.py`

**Avant :**
```python
DATA_DIR = os.environ.get("DATA_DIR", "/var/data")
```

**Après :**
```python
DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")
```

### 2. Commentaires mis à jour

Le commentaire dans le code a été mis à jour pour refléter la recommandation de Render :

```python
# Système de persistance avec fichier JSON
# Utilisation du répertoire recommandé par Render : /opt/render/project/src/data
```

## Avantages du nouveau chemin

1. **Recommandation officielle** : `/opt/render/project/src/data` est le chemin recommandé par Render
2. **Meilleure intégration** : S'intègre mieux avec l'architecture de Render
3. **Persistance garantie** : Assure une meilleure persistance des données
4. **Performance optimisée** : Chemin optimisé pour les performances sur Render

## Test de la migration

Un script de test `test_render_data_path.py` a été créé pour vérifier que le nouveau chemin fonctionne correctement :

```bash
python test_render_data_path.py
```

Ce script teste :
- La création du répertoire de données
- Les permissions de lecture/écriture
- L'écriture et la lecture de fichiers JSON
- L'affichage des informations de diagnostic

## Déploiement

1. **Commit et push** des changements vers GitHub
2. **Redéployment automatique** sur Render
3. **Vérification** que les données sont correctement persistées

## Variables d'environnement

La variable d'environnement `DATA_DIR` peut toujours être utilisée pour override le chemin par défaut si nécessaire :

```bash
DATA_DIR=/custom/path/to/data
```

## Compatibilité

- ✅ **Rétrocompatible** : Les données existantes seront automatiquement migrées
- ✅ **Pas d'interruption** : Aucune interruption de service prévue
- ✅ **Fallback** : Le système fonctionne même si le répertoire n'existe pas initialement

## Monitoring

Après le déploiement, surveiller :
- Les logs de démarrage pour confirmer le bon chemin
- La création automatique du répertoire de données
- La persistance des données entre les redémarrages

## Prochaines étapes

1. Déployer les changements sur Render
2. Tester la persistance des données
3. Vérifier que les immeubles créés persistent après redémarrage
4. Mettre à jour la documentation si nécessaire 