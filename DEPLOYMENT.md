# Guide de Déploiement - Interface CAH

Ce guide vous explique comment déployer votre application Interface CAH sur GitHub, Render (backend) et Vercel (frontend).

## 📋 Prérequis

- Compte GitHub
- Compte Render (gratuit)
- Compte Vercel (gratuit)
- Git installé sur votre machine

## 🚀 Étape 1: Publier sur GitHub

### 1.1 Initialiser le repository Git

```bash
# Dans le dossier racine de votre projet
git init
git add .
git commit -m "Initial commit - Interface CAH"
```

### 1.2 Créer un repository sur GitHub

1. Allez sur [GitHub.com](https://github.com)
2. Cliquez sur "New repository"
3. Nommez votre repository: `interface-cah`
4. Laissez-le public ou privé selon votre préférence
5. Ne cochez AUCUNE option (README, .gitignore, license) car nous avons déjà ces fichiers
6. Cliquez "Create repository"

### 1.3 Connecter votre projet local à GitHub

```bash
# Remplacez YOUR_USERNAME par votre nom d'utilisateur GitHub
git remote add origin https://github.com/YOUR_USERNAME/interface-cah.git
git branch -M main
git push -u origin main
```

## 🔧 Étape 2: Déployer le Backend sur Render

### 2.1 Créer un service sur Render

1. Allez sur [Render.com](https://render.com)
2. Connectez-vous avec votre compte GitHub
3. Cliquez "New +" → "Web Service"
4. Connectez votre repository `interface-cah`
5. Configurez le service:
   - **Name**: `interface-cah-backend`
   - **Root Directory**: `backend`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

### 2.2 Variables d'environnement (optionnel)

Dans l'onglet "Environment", vous pouvez ajouter:
- `PYTHON_VERSION`: `3.11.0`

### 2.3 Déploiement

1. Cliquez "Create Web Service"
2. Render va automatiquement déployer votre backend
3. Notez l'URL de votre backend (ex: `https://interface-cah-backend.onrender.com`)

## 🌐 Étape 3: Déployer le Frontend sur Vercel

### 3.1 Créer un projet sur Vercel

1. Allez sur [Vercel.com](https://vercel.com)
2. Connectez-vous avec votre compte GitHub
3. Cliquez "New Project"
4. Importez votre repository `interface-cah`
5. Configurez le projet:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`

### 3.2 Variables d'environnement

Dans l'onglet "Environment Variables", ajoutez:
- **Name**: `VITE_API_URL`
- **Value**: URL de votre backend Render (ex: `https://interface-cah-backend.onrender.com`)

### 3.3 Déploiement

1. Cliquez "Deploy"
2. Vercel va automatiquement déployer votre frontend
3. Vous obtiendrez une URL (ex: `https://interface-cah.vercel.app`)

## 🔄 Étape 4: Workflow de Développement

### 4.1 Faire des modifications

```bash
# Modifier vos fichiers
# Puis commiter et pousser
git add .
git commit -m "Description de vos modifications"
git push
```

### 4.2 Déploiement automatique

- **Render**: Se redéploie automatiquement à chaque push sur la branche `main`
- **Vercel**: Se redéploie automatiquement à chaque push sur la branche `main`

## 🛠️ Étape 5: Tester la Communication

### 5.1 Vérifier le backend

Visitez: `https://votre-backend.onrender.com/health`
Vous devriez voir: `{"status": "healthy", "message": "API fonctionnelle"}`

### 5.2 Vérifier le frontend

Visitez votre URL Vercel et naviguez dans l'interface. Les données du tableau de bord devraient se charger depuis votre backend.

## 🔧 Configuration CORS

Le backend est déjà configuré pour accepter les requêtes de Vercel grâce à:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 📝 Domaines Personnalisés (Optionnel)

### Pour Vercel:
1. Dans votre projet Vercel → Settings → Domains
2. Ajoutez votre domaine personnalisé

### Pour Render:
1. Dans votre service Render → Settings → Custom Domains
2. Ajoutez votre domaine personnalisé

## 🚨 Dépannage

### Backend ne démarre pas sur Render:
- Vérifiez les logs dans Render Dashboard
- Assurez-vous que `requirements.txt` est correct
- Vérifiez que le port est bien configuré avec `$PORT`

### Frontend ne peut pas contacter le backend:
- Vérifiez que `VITE_API_URL` est correctement configuré
- Vérifiez les CORS dans le backend
- Ouvrez les outils de développement du navigateur pour voir les erreurs

### Erreurs de build:
- Vérifiez que toutes les dépendances sont listées
- Assurez-vous que les chemins de fichiers sont corrects

## 🎉 Félicitations!

Votre Interface CAH est maintenant déployée et accessible en ligne! 

- **Frontend**: https://votre-app.vercel.app
- **Backend**: https://votre-backend.onrender.com
- **Code source**: https://github.com/votre-username/interface-cah 