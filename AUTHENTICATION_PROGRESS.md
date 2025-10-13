# 🔐 Système d'Authentification Multi-Tenant - État des Lieux

**Date :** $(date)
**Progression globale :** ~40% complété

---

## ✅ CE QUI A ÉTÉ FAIT (Backend - 40%)

### 1. **Modèles de données** (`backend/models_auth.py`)
✅ Créé et fonctionnel

**Tables créées :**
- `Compagnie` : Gestion des compagnies (multi-tenant)
  - Nom, email, téléphone, adresse, logo, site web, numéro d'entreprise
  - `schema_name` : Nom du schéma PostgreSQL pour isolation des données
  - Relations vers utilisateurs et demandes d'accès

- `Utilisateur` : Gestion des utilisateurs (employés et admins)
  - Informations personnelles complètes (nom, prénom, date naissance, âge, sexe, téléphone, poste)
  - Authentification (email, mot_de_passe_hash)
  - Rôles (admin/employe) et statut (en_attente/actif/inactif/refuse)
  - Validation email (code_verification_email, expiration)
  - Récupération mot de passe (code_reset_mdp, expiration)
  - `est_admin_principal` : Booléen pour les admins principaux

- `DemandeAcces` : Gestion des demandes d'accès
  - Statut (en_attente/approuve/refuse)
  - Admin qui a traité la demande
  - Commentaire de refus optionnel

### 2. **Service d'authentification** (`backend/auth_service.py`)
✅ Créé et fonctionnel

**Fonctionnalités :**
- ✅ Hashage bcrypt des mots de passe
- ✅ Vérification des mots de passe
- ✅ Création et décodage de tokens JWT (30 jours de validité)
- ✅ Génération de codes de vérification (6 caractères alphanumériques)
- ✅ Génération de codes de reset (8 caractères)
- ✅ Validation de la force des mots de passe
- ✅ Validation des emails
- ✅ Calcul automatique de l'âge
- ✅ Génération de noms de schémas PostgreSQL valides

**Configuration JWT :**
- Clé secrète : `a8f5e7c9d2b4f6a1e3c8d5b7f9a2c4e6d8b1f3a5c7e9b2d4f6a8c1e3d5b7f9a2`
- Algorithme : HS256
- Durée de validité : 30 jours (session persistante)

### 3. **Service d'emails** (`backend/email_service.py`)
✅ Créé et fonctionnel

**Templates HTML professionnels :**
- ✅ Email de vérification (avec code)
- ✅ Notification de demande d'accès (pour admins)
- ✅ Approbation de demande
- ✅ Refus de demande (avec raison optionnelle)
- ✅ Réinitialisation de mot de passe (avec code)
- ✅ Email de bienvenue (création de compagnie)

**Configuration SMTP (Gmail) :**
- Serveur : smtp.gmail.com:587
- Username : sacha.heroux87@gmail.com
- Password : dtxkfwhqmdvuthli (mot de passe d'application)
- Mode développement : Affiche les emails dans la console si SMTP non configuré

### 4. **Endpoints API d'authentification** (`backend/auth_routes.py` + `auth_routes_part2.py`)
✅ Créé (pas encore intégré dans main.py)

**Endpoints d'inscription :**
- `POST /api/auth/register` : Créer un compte utilisateur
- `POST /api/auth/verify-email` : Vérifier l'email avec le code
- `POST /api/auth/resend-verification` : Renvoyer le code de vérification

**Endpoints de connexion :**
- `POST /api/auth/login` : Se connecter (retourne token JWT)
- `GET /api/auth/me` : Obtenir les infos de l'utilisateur connecté
- `POST /api/auth/logout` : Se déconnecter

**Endpoints setup compagnie :**
- `POST /api/auth/setup-company` : Créer ou rejoindre une compagnie
- `GET /api/auth/companies` : Lister toutes les compagnies disponibles

**Endpoints récupération mot de passe :**
- `POST /api/auth/forgot-password` : Demander un code de reset
- `POST /api/auth/reset-password` : Réinitialiser avec le code

**Endpoints gestion des demandes (admins) :**
- `GET /api/auth/pending-requests` : Voir les demandes en attente
- `POST /api/auth/approve-request` : Approuver ou refuser une demande

**Middleware de sécurité :**
- `get_current_user` : Valide le token JWT et retourne l'utilisateur
- `require_admin` : Vérifie que l'utilisateur est admin

### 5. **Configuration** (`.env`)
✅ À créer manuellement

**Variables nécessaires :**
```env
# JWT
JWT_SECRET_KEY=a8f5e7c9d2b4f6a1e3c8d5b7f9a2c4e6d8b1f3a5c7e9b2d4f6a8c1e3d5b7f9a2

# SMTP Gmail
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=sacha.heroux87@gmail.com
SMTP_PASSWORD=dtxkfwhqmdvuthli
FROM_EMAIL=sacha.heroux87@gmail.com
FROM_NAME=Interface CAH

# URLs
FRONTEND_URL=http://localhost:5173
DATABASE_URL=postgresql://...

# Backblaze B2 (déjà existant)
B2_KEY_ID=...
B2_APPLICATION_KEY=...
B2_BUCKET_NAME=cah-documents
B2_BUCKET_ID=...
```

---

## 🚧 CE QUI RESTE À FAIRE (60%)

### **Backend Critique (20%)**

#### 1. Service Multi-Tenant (À créer)
**Fichier :** `backend/multitenant_service.py`

**Fonctionnalités nécessaires :**
- Créer un schéma PostgreSQL par compagnie
- Créer toutes les tables dans chaque schéma (immeubles, unites, locataires, baux, transactions, paiements_loyers)
- Fonction pour se connecter au bon schéma selon l'utilisateur
- Middleware pour injecter automatiquement le schéma dans les requêtes

#### 2. Script de migration des données actuelles
**Fichier :** `backend/migrate_to_multitenant.py`

**Actions :**
1. Créer les tables d'authentification dans le schéma `public`
2. Créer la compagnie de Sacha
3. Créer l'utilisateur Sacha (sacha.heroux87@gmail.com / Champion2024!)
4. Créer le schéma pour la compagnie de Sacha
5. Migrer toutes les données actuelles vers ce schéma
6. Tester que tout fonctionne

#### 3. Intégration dans main.py
**Modifications nécessaires :**
- Importer et inclure les routes d'authentification
- Ajouter le middleware multi-tenant
- Protéger les endpoints existants avec authentification
- Filtrer les données par compagnie automatiquement

#### 4. Script de création des tables
**Fichier :** `backend/create_auth_tables.py`

**Actions :**
- Créer les tables compagnies, utilisateurs, demandes_acces sur Render
- Insérer la compagnie et l'utilisateur de Sacha

---

### **Frontend (40%)**

#### 1. Pages à créer (6-8 pages)

**Page de connexion** (`frontend/src/pages/Login.jsx`)
- Design professionnel et moderne
- Formulaire email + mot de passe
- Lien "Mot de passe oublié ?"
- Lien "Créer un compte"
- Validation et gestion d'erreurs

**Page d'inscription** (`frontend/src/pages/Register.jsx`)
- Formulaire multi-étapes :
  1. Informations de base (email, mot de passe, nom, prénom)
  2. Informations personnelles (date naissance, sexe, téléphone, poste)
- Indicateur de force du mot de passe
- Validation en temps réel

**Page vérification email** (`frontend/src/pages/VerifyEmail.jsx`)
- Input pour le code de vérification
- Bouton "Renvoyer le code"
- Timer de 15 minutes

**Page setup compagnie** (`frontend/src/pages/CompanySetup.jsx`)
- Choix : Créer ou Rejoindre
- Si créer : Formulaire complet de compagnie
- Si rejoindre : Liste des compagnies + choix du rôle
- Interface moderne avec icônes

**Page en attente d'approbation** (`frontend/src/pages/PendingApproval.jsx`)
- Message d'attente
- Informations sur la compagnie rejointe
- Bouton pour se déconnecter

**Page récupération mot de passe** (`frontend/src/pages/ForgotPassword.jsx`)
- Étape 1 : Entrer email
- Étape 2 : Entrer code + nouveau mot de passe
- Validation

**Page gestion des demandes (Admin)** (`frontend/src/pages/AdminApprovals.jsx`)
- Liste des demandes en attente
- Cartes avec infos de chaque utilisateur
- Boutons Approuver / Refuser
- Modal de confirmation pour refus (avec raison)

#### 2. Composants à créer/modifier

**AuthContext** (`frontend/src/contexts/AuthContext.jsx`)
- State global pour l'utilisateur connecté
- Fonctions login, logout, register
- Vérification du token au chargement
- Stockage du token dans localStorage

**ProtectedRoute** (`frontend/src/components/ProtectedRoute.jsx`)
- Composant wrapper pour les routes protégées
- Redirige vers /login si pas connecté
- Vérifie le rôle (admin/employe)

**Menu utilisateur** (Modifier `frontend/src/components/TopNavigation.jsx`)
- Afficher l'email à côté de l'icône utilisateur
- Menu déroulant au clic :
  - Mon compte
  - Changer mot de passe
  - Déconnexion

#### 3. Service API frontend
**Fichier :** `frontend/src/services/authApi.js`

**Fonctions :**
- register(), verifyEmail(), resendVerification()
- login(), logout(), getCurrentUser()
- setupCompany(), getCompanies()
- forgotPassword(), resetPassword()
- getPendingRequests(), approveRequest()

#### 4. Routes et navigation
**Fichier :** `frontend/src/App.jsx`

**Routes à ajouter :**
```jsx
<Route path="/login" element={<Login />} />
<Route path="/register" element={<Register />} />
<Route path="/verify-email" element={<VerifyEmail />} />
<Route path="/company-setup" element={<CompanySetup />} />
<Route path="/pending-approval" element={<PendingApproval />} />
<Route path="/forgot-password" element={<ForgotPassword />} />
<Route path="/admin/approvals" element={<ProtectedRoute admin><AdminApprovals /></ProtectedRoute>} />

// Routes existantes à protéger
<Route path="/*" element={<ProtectedRoute><...existing routes...</ProtectedRoute>} />
```

#### 5. Filtrage par rôle
**Modifications :**
- Employés : Voir uniquement l'onglet "Employés"
- Admins : Voir tous les onglets
- Cacher/afficher les onglets dans TopNavigation selon le rôle

---

## 📋 PLAN D'ACTION POUR LA SUITE

### **Session 1 : Backend Multi-Tenant (2-3h)**
1. Créer `multitenant_service.py`
2. Créer `create_auth_tables.py` et l'exécuter sur Render
3. Créer `migrate_to_multitenant.py`
4. Intégrer les routes dans `main.py`
5. Tester tous les endpoints avec Postman/Thunder Client

### **Session 2 : Frontend Auth Flow (3-4h)**
1. Créer AuthContext
2. Créer les pages Login, Register, VerifyEmail
3. Créer CompanySetup
4. Créer authApi.js
5. Tester le flux complet : inscription → vérification → setup compagnie

### **Session 3 : Frontend Avancé (2-3h)**
1. Créer PendingApproval, ForgotPassword
2. Créer AdminApprovals
3. Modifier TopNavigation (menu utilisateur)
4. Créer ProtectedRoute
5. Filtrer les onglets par rôle

### **Session 4 : Tests et Déploiement (2-3h)**
1. Tester tous les flux
2. Corriger les bugs
3. Migrer les données de Sacha
4. Configurer les variables d'environnement sur Render
5. Déployer et tester en production

**TOTAL ESTIMÉ : 10-15 heures supplémentaires**

---

## 🎯 PROCHAINES ÉTAPES IMMÉDIATES

Quand tu seras prêt à continuer :

1. **Créer le fichier `.env`** manuellement avec le contenu fourni ci-dessus
2. **Fusionner `auth_routes.py` et `auth_routes_part2.py`** en un seul fichier
3. **Commencer par le service multi-tenant** (le plus critique)

---

## 📞 NOTES IMPORTANTES

- ⚠️ **Ne pas commiter le fichier `.env` dans Git !**
- 📧 Le mot de passe d'application Gmail est à usage unique
- 🔐 La clé JWT doit rester secrète
- 🗄️ L'isolation par schémas PostgreSQL est cruciale pour la sécurité
- 📱 Les emails sont en mode développement tant que SMTP n'est pas configuré en production

---

## 📁 FICHIERS CRÉÉS CETTE SESSION

1. `backend/models_auth.py` - Modèles Compagnie, Utilisateur, DemandeAcces
2. `backend/auth_service.py` - Service JWT, bcrypt, validation
3. `backend/email_service.py` - Service emails avec templates HTML
4. `backend/auth_routes.py` - Endpoints d'authentification (partie 1)
5. `backend/auth_routes_part2.py` - Endpoints d'authentification (partie 2)
6. `backend/.env` - Configuration (À CRÉER MANUELLEMENT)

---

## 🎨 DESIGN ET UX

**Couleurs principales (à utiliser dans les pages d'auth) :**
- Primaire : #667eea (bleu-violet)
- Secondaire : #764ba2 (violet)
- Accent : Gradient (135deg, #667eea 0%, #764ba2 100%)
- Succès : #10b981 (vert)
- Erreur : #ef4444 (rouge)
- Warning : #f59e0b (orange)

**Style :**
- Design moderne et professionnel
- Espace blanc généreux
- Icônes Lucide React
- Animations subtiles
- Feedback visuel immédiat
- Messages d'erreur clairs et en français

---

**Bon courage pour la suite ! 🚀**

