# 🚀 Guide de Migration : JSON → SQLite

## 📋 Vue d'ensemble

Ce guide vous accompagne dans la migration de vos données JSON vers une base de données SQLite robuste et sécurisée.

## 🎯 Avantages de la migration

- ✅ **Sécurité** : Plus de corruption de données
- ✅ **Performance** : Requêtes rapides et indexées
- ✅ **Intégrité** : Contraintes et relations garanties
- ✅ **Sauvegarde** : Système automatique de sauvegarde
- ✅ **Évolutivité** : Facile à migrer vers PostgreSQL plus tard

## 📦 Prérequis

### 1. Installer les dépendances
```bash
cd backend
python install_sqlite_deps.py
```

### 2. Vérifier l'installation
```bash
python -c "import sqlite3, sqlalchemy; print('✅ Dépendances installées')"
```

## 🔄 Processus de migration

### Étape 1 : Sauvegarde de sécurité
```bash
# Créer une sauvegarde de vos données JSON
cp -r data data_backup_$(date +%Y%m%d_%H%M%S)
```

### Étape 2 : Test de la migration
```bash
# Tester la migration (recommandé)
python test_migration.py
```

### Étape 3 : Migration des données
```bash
# Exécuter la migration
python migrate_to_sqlite.py
```

### Étape 4 : Vérification
```bash
# Vérifier que tout fonctionne
python test_migration.py
```

## 📊 Structure de la base de données

### Tables créées :
- **buildings** : Immeubles
- **tenants** : Locataires  
- **assignments** : Assignations locataire-unité
- **building_reports** : Rapports d'immeubles
- **unit_reports** : Rapports d'unités
- **invoices** : Factures

### Contraintes appliquées :
- Clés primaires sur tous les ID
- Clés étrangères pour les relations
- Contraintes UNIQUE sur les champs critiques
- Index pour optimiser les performances

## 🔧 Configuration

### Variables d'environnement
```bash
# En local (développement)
export DATA_DIR="./data"

# Sur Render (production)
export DATA_DIR="/opt/render/project/src/data"
```

### Fichiers créés
```
data/
├── cah_database.db          # Base de données SQLite
├── backups/                 # Sauvegardes automatiques
│   └── cah_backup_*.db
└── [vos fichiers JSON existants]  # Conservés pour référence
```

## 🛡️ Sécurité et sauvegarde

### Sauvegarde automatique
- Créée avant chaque migration
- Stockée dans `data/backups/`
- Nommé avec timestamp : `cah_backup_YYYYMMDD_HHMMSS.db`

### Restauration
```bash
# En cas de problème, restaurer depuis la sauvegarde
cp data/backups/cah_backup_YYYYMMDD_HHMMSS.db data/cah_database.db
```

## 🚨 En cas de problème

### Problème : Migration échouée
1. Vérifiez les logs d'erreur
2. Restaurez depuis la sauvegarde
3. Vérifiez l'intégrité des données JSON
4. Relancez la migration

### Problème : Données corrompues
1. Arrêtez l'application
2. Restaurez depuis la dernière sauvegarde
3. Vérifiez l'intégrité avec `test_migration.py`

### Problème : Performance lente
1. Vérifiez les index : `python -c "from database import db_manager; db_manager.connect(); print('Index OK')"`
2. Optimisez les requêtes
3. Considérez la migration vers PostgreSQL

## 📈 Monitoring

### Vérification de santé
```bash
# Vérifier l'état de la base de données
python -c "
from database import db_manager
db_manager.connect()
cursor = db_manager.connection.cursor()
cursor.execute('SELECT COUNT(*) FROM buildings')
print(f'Immeubles: {cursor.fetchone()[0]}')
db_manager.disconnect()
"
```

### Logs à surveiller
- Erreurs de connexion
- Violations de contraintes
- Performances des requêtes

## 🔄 Migration future vers PostgreSQL

Quand vous serez prêt pour PostgreSQL :

1. **Exporter les données SQLite**
```bash
sqlite3 cah_database.db .dump > data_export.sql
```

2. **Créer la base PostgreSQL**
```sql
CREATE DATABASE cah_production;
```

3. **Importer les données**
```bash
psql cah_production < data_export.sql
```

## ✅ Checklist de migration

- [ ] Dépendances installées
- [ ] Sauvegarde JSON créée
- [ ] Test de migration réussi
- [ ] Migration exécutée
- [ ] Vérification post-migration
- [ ] Application testée
- [ ] Sauvegarde automatique configurée

## 🆘 Support

En cas de problème :
1. Consultez les logs d'erreur
2. Vérifiez l'intégrité des données
3. Restaurez depuis la sauvegarde
4. Contactez le support technique

---

**🎉 Félicitations !** Votre base de données est maintenant robuste et protégée contre la corruption.
