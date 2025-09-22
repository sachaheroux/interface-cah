# Guide de Migration vers Backblaze B2

## 🎯 Objectif
Migrer le stockage des PDFs de Render vers Backblaze B2 pour réduire les coûts de 98%.

## 📋 Prérequis

### 1. Compte Backblaze B2
1. Aller sur [backblaze.com](https://www.backblaze.com/b2/cloud-storage.html)
2. Créer un compte gratuit
3. Créer un bucket nommé `interface-cah-pdfs`

### 2. Clés d'API
1. Aller dans "App Keys" dans votre compte Backblaze
2. Créer une nouvelle clé d'application
3. Noter :
   - `Application Key ID`
   - `Application Key`

## 🔧 Configuration

### 1. Variables d'environnement
Créer un fichier `.env` dans le dossier `backend/` :

```bash
# Backblaze B2 Configuration
B2_APPLICATION_KEY_ID=votre_application_key_id
B2_APPLICATION_KEY=votre_application_key
B2_BUCKET_NAME=interface-cah-pdfs
```

### 2. Installation des dépendances
```bash
cd backend
pip install boto3
```

### 3. Test de configuration
```bash
python setup_backblaze_b2.py
```

## 🚀 Migration

### 1. Sauvegarde complète
```bash
# Le script crée automatiquement une sauvegarde
python migrate_pdfs_to_backblaze.py
```

### 2. Vérification
- Vérifier que les PDFs sont dans Backblaze B2
- Tester l'affichage des PDFs dans l'interface
- Vérifier que la base de données a été mise à jour

## 🔄 Mise à jour du code

### 1. Modifier les endpoints d'upload
Les endpoints `/api/documents/upload` doivent utiliser Backblaze B2 au lieu du stockage local.

### 2. Modifier les endpoints de téléchargement
Les endpoints `/api/documents/{filename}` doivent servir depuis Backblaze B2.

## 💰 Économies

| Taille | Render | Backblaze B2 | Économie |
|--------|--------|--------------|----------|
| 10 GB  | $2.50  | $0.00        | 100%     |
| 50 GB  | $12.50 | $0.20        | 98%      |
| 100 GB | $25.00 | $0.45        | 98%      |

## 🛡️ Sécurité

- ✅ Sauvegarde complète avant migration
- ✅ Migration réversible
- ✅ Test complet avant activation
- ✅ Rollback possible

## 📞 Support

En cas de problème :
1. Vérifier les logs de migration
2. Restaurer depuis la sauvegarde
3. Contacter le support technique
