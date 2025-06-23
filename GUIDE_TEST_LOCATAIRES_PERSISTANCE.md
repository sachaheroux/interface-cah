# Guide de Test - Persistance des Locataires

## 🎯 Objectif
Vérifier que les locataires sont bien sauvegardés et persistent après rechargement.

## ✅ Étapes de Test

### 1. Démarrer le Backend
```bash
cd backend
python main.py
```

Vous devriez voir :
```
🔧 DIAGNOSTIC DISQUE PERSISTANT
📂 DATA_DIR (utilisé): /opt/render/project/src/data
📁 Répertoire existe: True
INFO: Uvicorn running on http://0.0.0.0:8000
```

### 2. Démarrer le Frontend
Dans un autre terminal :
```bash
cd frontend
npm run dev
```

### 3. Test de Création d'un Locataire

1. **Aller sur la page Locataires**
2. **Cliquer sur "Nouveau Locataire"**
3. **Remplir le formulaire** avec au minimum :
   - Nom : "Test Persistance"
   - Email : "test@example.com"
   - Téléphone : "(514) 555-0000"
   - Statut : "Actif"

4. **Optionnel - Remplir d'autres sections** :
   - Adresse personnelle
   - Contact d'urgence
   - Informations financières
   - Notes

5. **Cliquer sur "Sauvegarder"**

### 4. Vérification de la Persistance

#### Test 1 : Rechargement de page
1. **Recharger la page** (F5 ou Ctrl+R)
2. **Vérifier** que le locataire créé est toujours là ✅

#### Test 2 : Redémarrage du backend
1. **Arrêter le backend** (Ctrl+C dans le terminal)
2. **Redémarrer le backend** (`python main.py`)
3. **Recharger la page frontend**
4. **Vérifier** que le locataire est toujours là ✅

#### Test 3 : Modification
1. **Cliquer sur "Modifier"** sur le locataire créé
2. **Changer quelques informations** (ex: téléphone, notes)
3. **Sauvegarder**
4. **Recharger la page**
5. **Vérifier** que les modifications sont conservées ✅

## 🔍 Vérification Technique

### Fichier de Données
Le fichier de données devrait être créé dans :
- **Windows (local)** : `backend/opt/render/project/src/data/tenants_data.json`
- **Render (production)** : `/opt/render/project/src/data/tenants_data.json`

### Console du Navigateur
Ouvrez les outils de développement (F12) et regardez la console :
- Vous devriez voir des logs comme :
  ```
  Creating tenant with data: {...}
  API create tenant response: {...}
  ```

### Logs du Backend
Dans le terminal du backend, vous devriez voir :
```
Données locataires chargées: X locataires
Données locataires sauvegardées: X locataires
```

## 🐛 Résolution de Problèmes

### Problème : Locataires vides après création
**Cause** : Problème de sérialisation des données
**Solution** : Vérifier les logs dans la console du navigateur

### Problème : Données perdues après rechargement
**Cause** : Fichier non créé ou non accessible
**Solution** : Vérifier les permissions du répertoire

### Problème : Erreur de connexion API
**Cause** : Backend non démarré ou port différent
**Solution** : 
1. Vérifier que le backend tourne sur `http://localhost:8000`
2. Vérifier la variable `VITE_API_URL` dans le frontend

## 📊 Données de Test Suggérées

### Locataire Complet
```json
{
  "name": "Jean Test",
  "email": "jean.test@example.com",
  "phone": "(514) 555-1234",
  "status": "active",
  "personalAddress": {
    "street": "123 Rue Test",
    "city": "Montréal",
    "province": "QC",
    "postalCode": "H1A 1A1"
  },
  "emergencyContact": {
    "name": "Marie Test",
    "phone": "(514) 555-5678",
    "relationship": "conjoint"
  },
  "financial": {
    "monthlyIncome": 5000,
    "creditScore": 750,
    "employer": "Entreprise Test"
  },
  "notes": "Test de persistance des données"
}
```

### Locataire Minimal
```json
{
  "name": "Test Minimal"
}
```

## ✅ Critères de Réussite

- ✅ Création de locataire fonctionne
- ✅ Données complètes sauvegardées (pas vides)
- ✅ Persistance après rechargement de page
- ✅ Persistance après redémarrage backend
- ✅ Modifications sauvegardées
- ✅ Suppression fonctionne
- ✅ Filtres et recherche fonctionnent

## 🚀 Prêt pour Production

Une fois tous les tests passés, le système est prêt pour le déploiement sur Render avec persistance garantie ! 