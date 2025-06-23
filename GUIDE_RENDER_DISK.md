# Guide de Configuration Render Disk

## Problème Résolu
Ce guide résout le problème de **perte de données à chaque déploiement** en configurant un disque persistant sur Render.

## Prérequis
- Un service Render **PAYANT** (minimum $7/mois)
- Accès au dashboard Render

## Étapes de Configuration

### 1. Upgrade vers un Plan Payant

1. Allez sur https://dashboard.render.com
2. Sélectionnez votre service backend
3. Cliquez sur "Settings"
4. Dans la section "Instance Type", cliquez "Change"
5. Sélectionnez **"Starter" ($7/mois)** ou plus
6. Confirmez le changement

### 2. Ajouter un Disque Persistant

1. Dans votre service backend, allez à l'onglet **"Disks"**
2. Cliquez sur **"Add Disk"**
3. Configurez le disque :
   - **Name** : `interface-cah-data`
   - **Mount Path** : `/var/data` (IMPORTANT : doit correspondre au code)
   - **Size** : `1 GB` (suffisant pour commencer)
4. Cliquez **"Add Disk"**

### 3. Configurer les Variables d'Environnement

1. Allez dans l'onglet **"Environment"** de votre service
2. Ajoutez cette variable :
   - **Key** : `DATA_DIR`
   - **Value** : `/var/data`
3. Cliquez **"Save Changes"**

### 4. Redéployer le Service

1. Allez dans l'onglet **"Manual Deploy"**
2. Cliquez **"Deploy Latest Commit"**
3. Attendez que le déploiement se termine (2-3 minutes)

## Vérification

### Test de Persistance

1. Créez un immeuble via votre interface
2. Vérifiez qu'il apparaît dans la liste
3. Redéployez manuellement le service
4. ✅ **L'immeuble doit toujours être présent !**

### Logs de Vérification

Dans les logs du service, vous devriez voir :
```
Données chargées: X immeubles
Données sauvegardées: X immeubles
```

## Développement Local

Pour tester localement avec la même structure :

1. Créez un dossier `data` dans le backend :
```bash
mkdir backend/data
```

2. Ajoutez cette variable d'environnement locale :
```bash
export DATA_DIR=./data
```

3. Lancez votre serveur :
```bash
cd backend
python -m uvicorn main:app --reload
```

## Avantages de cette Solution

✅ **Persistance garantie** : Les données survivent aux redéploiements
✅ **Sauvegardes automatiques** : Render fait des snapshots quotidiens
✅ **Performance** : SSD haute performance
✅ **Sécurité** : Données chiffrées au repos
✅ **Évolutif** : Peut augmenter la taille du disque plus tard

## Coûts

- **Service Starter** : $7/mois
- **Disque 1GB** : Inclus dans le plan
- **Total** : $7/mois pour une solution professionnelle

## Limitations

⚠️ **Downtime** : 2-3 secondes lors des déploiements (vs 0 seconde avant)
⚠️ **Scaling** : Un seul instance possible avec disque
⚠️ **Accès** : Disque accessible uniquement par ce service

## Troubleshooting

### Problème : "Permission denied" sur /var/data
**Solution** : Vérifiez que le Mount Path est exactement `/var/data`

### Problème : Données toujours perdues
**Solution** : 
1. Vérifiez la variable `DATA_DIR=/var/data`
2. Vérifiez les logs pour voir si le disque est monté
3. Redéployez après ajout du disque

### 🚨 **PROBLÈME COURANT : Chemin de montage incorrect**

**Symptôme** : Les données sont encore perdues après configuration du disque

**Cause** : Le chemin `/var/data` ne fonctionne pas toujours. Basé sur la communauté Render, le chemin correct est souvent différent.

**Solution** : Essayez ces chemins dans l'ordre :

1. **Chemin recommandé par la communauté** (cas de succès confirmé) :
   - **Mount Path** : `/opt/render/project/src/data`
   - **Variable** : `DATA_DIR=/opt/render/project/src/data`

2. **Chemin alternatif simple** :
   - **Mount Path** : `/data`
   - **Variable** : `DATA_DIR=/data`

3. **Chemin original** (si les autres ne marchent pas) :
   - **Mount Path** : `/var/data`
   - **Variable** : `DATA_DIR=/var/data`

### 🔧 **Script de Diagnostic**

Utilisez le script `backend/debug_disk.py` pour identifier le bon chemin :

1. Déployez le code avec le script
2. Allez dans Shell de votre service Render
3. Exécutez : `python debug_disk.py`
4. Utilisez le chemin recommandé dans les résultats

### Problème : "No space left on device"
**Solution** : Augmentez la taille du disque dans l'onglet "Disks"

### Problème : Variable d'environnement ignorée
**Solution** :
1. Vérifiez que `DATA_DIR` est bien définie dans l'onglet Environment
2. Redéployez après avoir ajouté la variable
3. Vérifiez les logs de démarrage pour voir la valeur utilisée

## Migration Future vers PostgreSQL

Cette solution peut facilement évoluer vers PostgreSQL plus tard :
1. Créer une base Render Postgres
2. Migrer les données JSON vers PostgreSQL
3. Supprimer le disque persistant

## Support

Si vous rencontrez des problèmes :
1. Vérifiez les logs du service
2. Contactez le support Render si nécessaire
3. Consultez la documentation : https://render.com/docs/disks 