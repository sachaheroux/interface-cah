# Améliorations de la gestion des données - Interface CAH

## Phase 1 : Améliorations immédiates (Recommandé)

### 1. Système de sauvegarde automatique
```python
def create_backup():
    """Créer une sauvegarde des données"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = os.path.join(DATA_DIR, "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    for data_file in [BUILDINGS_DATA_FILE, TENANTS_DATA_FILE, ...]:
        if os.path.exists(data_file):
            backup_file = os.path.join(backup_dir, f"{os.path.basename(data_file)}_{timestamp}")
            shutil.copy2(data_file, backup_file)
```

### 2. Validation de cohérence des données
```python
def validate_data_consistency():
    """Valider la cohérence entre les différentes données"""
    buildings = load_buildings_data()
    tenants = load_tenants_data()
    assignments = load_assignments_data()
    
    # Vérifier que tous les buildingId dans assignments existent
    building_ids = {b['id'] for b in buildings['buildings']}
    for assignment in assignments['assignments']:
        if assignment['buildingId'] not in building_ids:
            print(f"⚠️ Assignation orpheline: buildingId {assignment['buildingId']} n'existe pas")
    
    # Vérifier que tous les tenantId dans assignments existent
    tenant_ids = {t['id'] for t in tenants['tenants']}
    for assignment in assignments['assignments']:
        if assignment['tenantId'] not in tenant_ids:
            print(f"⚠️ Assignation orpheline: tenantId {assignment['tenantId']} n'existe pas")
```

### 3. Transactions atomiques
```python
def atomic_save(data, filename):
    """Sauvegarde atomique - écrit d'abord dans un fichier temporaire"""
    temp_file = filename + ".tmp"
    try:
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        # Renommer seulement si l'écriture a réussi
        os.rename(temp_file, filename)
        return True
    except Exception as e:
        # Nettoyer le fichier temporaire en cas d'erreur
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return False
```

## Phase 2 : Migration vers une base de données (Moyen terme)

### Option A : SQLite (Recommandé pour commencer)
- **Avantages** : Pas de serveur, ACID, SQL standard
- **Inconvénients** : Limité en concurrence

### Option B : PostgreSQL (Recommandé pour production)
- **Avantages** : Robuste, scalable, JSON natif
- **Inconvénients** : Plus complexe à déployer

### Option C : MongoDB (Si vous préférez NoSQL)
- **Avantages** : Flexible, JSON natif
- **Inconvénients** : Moins de garanties ACID

## Phase 3 : Optimisations avancées (Long terme)

### 1. Système de cache intelligent
- Cache Redis pour les données fréquemment accédées
- Invalidation automatique du cache

### 2. Indexation et recherche
- Index sur les champs fréquemment recherchés
- Recherche full-text pour les noms, descriptions

### 3. API de migration
- Scripts de migration pour évoluer le schéma
- Versioning des données

## Structure de données recommandée

### Tables principales
```sql
-- Immeubles
CREATE TABLE buildings (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    address TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Locataires
CREATE TABLE tenants (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Unités (générées dynamiquement)
CREATE TABLE units (
    id VARCHAR(50) PRIMARY KEY,
    building_id INTEGER REFERENCES buildings(id),
    unit_number VARCHAR(50),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Assignations
CREATE TABLE assignments (
    id SERIAL PRIMARY KEY,
    tenant_id INTEGER REFERENCES tenants(id),
    unit_id VARCHAR(50) REFERENCES units(id),
    assigned_at TIMESTAMP DEFAULT NOW()
);

-- Factures
CREATE TABLE invoices (
    id SERIAL PRIMARY KEY,
    invoice_number VARCHAR(100) UNIQUE NOT NULL,
    category VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    building_id INTEGER REFERENCES buildings(id),
    unit_id VARCHAR(50) REFERENCES units(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

## Migration depuis JSON

### Script de migration
```python
def migrate_json_to_sqlite():
    """Migrer les données JSON vers SQLite"""
    # Charger toutes les données JSON
    buildings_data = load_buildings_data()
    tenants_data = load_tenants_data()
    # ... etc
    
    # Créer la base de données
    conn = sqlite3.connect('cah_data.db')
    
    # Insérer les données
    for building in buildings_data['buildings']:
        conn.execute("INSERT INTO buildings (id, name, address) VALUES (?, ?, ?)",
                    (building['id'], building['name'], building['address']))
    
    conn.commit()
    conn.close()
```
