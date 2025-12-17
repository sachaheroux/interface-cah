# Fonctionnement de la Base de Données - Interface CAH

## Introduction

Ce rapport explique comment fonctionne la base de données de l'application Interface CAH, notamment comment elle est persistée sur Render et comment on peut la télécharger pour l'analyser avec DB Browser.

## 1. Configuration et Persistance sur Render

### 1.1 Configuration de la Base de Données

Le fichier `database.py` configure la base de données SQLite. Voici les parties importantes :

```python
RENDER_DATABASE_URL = os.environ.get("DATABASE_URL")
```

**Explication détaillée** : `os.environ.get("DATABASE_URL")` lit une variable d'environnement. Sur Render, si on configure une base PostgreSQL, cette variable contient l'URL de connexion. Si elle n'existe pas (ou est vide), on utilise SQLite à la place.

```python
if RENDER_DATABASE_URL:
    # Sur Render avec PostgreSQL
    engine = create_engine(RENDER_DATABASE_URL, ...)
else:
    # Configuration SQLite locale ou sur Render avec disk persistant
    DATA_DIR = os.environ.get("DATA_DIR", "/opt/render/project/src/data")
    DATABASE_PATH = os.path.join(DATA_DIR, "cah_database.db")
    engine = create_engine(f"sqlite:///{DATABASE_PATH}", ...)
```

**Explication détaillée** : 
- Si `RENDER_DATABASE_URL` existe, on crée un moteur SQLAlchemy qui se connecte à PostgreSQL avec l'URL fournie.
- Sinon, on configure SQLite. Le chemin `/opt/render/project/src/data` est le répertoire du disque persistant sur Render. Ce disque persiste même si le serveur redémarre, contrairement au système de fichiers éphémère.
- `os.path.join()` combine le répertoire et le nom du fichier pour créer le chemin complet : `/opt/render/project/src/data/cah_database.db`
- `create_engine()` crée un objet SQLAlchemy qui gère les connexions à la base. Le préfixe `sqlite:///` indique qu'on utilise SQLite.

**Pourquoi utiliser un disque persistant ?** Sans disque persistant, le fichier SQLite serait dans `/tmp` ou un autre répertoire temporaire qui serait effacé à chaque redémarrage. Avec le disque persistant monté à `/opt/render/project/src/data`, le fichier `cah_database.db` reste intact entre les redémarrages.

### 1.2 Initialisation des Tables

Dans `main.py`, au démarrage de l'application :

```python
from database import init_database
init_database()
```

Cette fonction crée toutes les tables si elles n'existent pas :

```python
def init_database():
    from models_francais import Base
    Base.metadata.create_all(bind=engine)
```

**Explication détaillée** : 
- `Base` est une classe déclarative de SQLAlchemy. Tous les modèles (comme `Locataire`, `Unite`, `Immeuble`, etc.) héritent de cette classe.
- `Base.metadata` contient toutes les informations sur les tables définies dans les modèles (colonnes, types, clés étrangères, etc.).
- `create_all(bind=engine)` lit ces métadonnées et génère les commandes SQL `CREATE TABLE` nécessaires, puis les exécute via le moteur `engine`.
- Si une table existe déjà, SQLAlchemy ne fait rien (pas d'erreur). C'est pour ça qu'on peut appeler `init_database()` plusieurs fois sans problème.
- Les tables sont créées dans le fichier SQLite sur le disque persistant Render.

**Exemple concret** : Si le modèle `Locataire` définit des colonnes `id_locataire`, `nom`, `prenom`, etc., `create_all()` va créer une table `locataires` avec ces colonnes dans le fichier `cah_database.db`.

### 1.3 Module de Construction

Le fichier `database_construction.py` utilise **exactement le même fichier SQLite** :

```python
from database import db_manager, engine
construction_engine = engine  # Même moteur
CONSTRUCTION_DATABASE_PATH = db_manager.db_path  # Même fichier
```

**Explication détaillée** : 
- Au lieu de créer une base séparée, le module construction partage le même fichier `cah_database.db`.
- `construction_engine = engine` signifie qu'on utilise le même objet moteur SQLAlchemy, donc la même connexion au même fichier.
- `db_manager.db_path` contient le chemin vers `cah_database.db` (ex: `/opt/render/project/src/data/cah_database.db`).
- Les tables de construction (projets, commandes, factures_st, etc.) sont ajoutées dans le même fichier que les tables locatives (immeubles, unités, locataires, etc.).

**Avantage** : Toutes les données sont dans un seul fichier, ce qui simplifie les sauvegardes et permet de faire des requêtes qui joignent des tables de différents modules (ex: lier un projet à un immeuble).

## 2. Modification des Données

### 2.1 Via l'API

Quand l'utilisateur crée ou modifie des données via l'interface web, le frontend envoie des requêtes HTTP au backend. Par exemple, pour créer un locataire :

```python
@app.post("/api/tenants")
async def create_tenant(tenant_data: TenantCreateFrancais):
    tenant_dict = tenant_data.dict()
    created_tenant = db_service_francais.create_tenant(tenant_dict)
    return {"data": created_tenant}
```

**Explication détaillée** : 
- `@app.post("/api/tenants")` est un décorateur FastAPI qui crée un endpoint HTTP POST accessible à l'URL `/api/tenants`.
- Quand le frontend envoie une requête POST avec des données JSON (ex: `{"nom": "Dupont", "prenom": "Jean", ...}`), FastAPI les valide automatiquement avec le modèle Pydantic `TenantCreateFrancais`.
- `tenant_data.dict()` convertit l'objet Pydantic en dictionnaire Python standard (ex: `{"nom": "Dupont", "prenom": "Jean", ...}`).
- `db_service_francais.create_tenant(tenant_dict)` appelle la fonction qui insère réellement dans SQLite (voir section 2.2).
- Le résultat est retourné en JSON au frontend avec `{"data": created_tenant}`.

**Flux complet** : Frontend → HTTP POST → FastAPI endpoint → Validation Pydantic → Service DB → SQLite → Disque Render

### 2.2 Service de Base de Données

Le service `database_service_francais.py` gère les opérations CRUD :

```python
def create_tenant(self, tenant_data: Dict[str, Any]) -> Dict[str, Any]:
    with self.get_session() as session:
        tenant = Locataire(
            nom=tenant_data.get('nom'),
            prenom=tenant_data.get('prenom'),
            id_unite=tenant_data.get('id_unite'),
            ...
        )
        session.add(tenant)
        session.commit()
        return tenant.to_dict()
```

**Explication détaillée** : 
- `self.get_session()` est un context manager qui ouvre une session SQLAlchemy. Une session est comme une transaction : elle regroupe plusieurs opérations.
- `with ... as session:` garantit que la session sera fermée automatiquement à la fin, même en cas d'erreur.
- `Locataire(...)` crée une instance du modèle SQLAlchemy. Les données du dictionnaire sont passées au constructeur. Par exemple, `nom=tenant_data.get('nom')` récupère la valeur de la clé 'nom' ou `None` si elle n'existe pas.
- `session.add(tenant)` ajoute l'objet à la session. À ce stade, rien n'est encore écrit dans le fichier SQLite, c'est juste en mémoire.
- `session.commit()` exécute réellement l'insertion SQL (`INSERT INTO locataires ...`) et écrit dans le fichier `cah_database.db` sur le disque Render. C'est à ce moment que les données sont persistées.
- `tenant.to_dict()` convertit l'objet SQLAlchemy en dictionnaire Python (ex: `{"id_locataire": 1, "nom": "Dupont", ...}`) pour le retourner en JSON au frontend.

**Important** : Si une erreur survient avant `commit()`, la transaction est annulée (rollback) et rien n'est écrit. C'est la garantie de cohérence des données.

### 2.3 Mise à Jour Dynamique des Colonnes

Quand on ajoute de nouvelles colonnes aux modèles, `database_construction.py` les ajoute automatiquement :

```python
result = db.execute(text("PRAGMA table_info(projets)"))
existing_columns = [col[1] for col in result.fetchall()]

if "adresse" not in existing_columns:
    db.execute(text("ALTER TABLE projets ADD COLUMN adresse VARCHAR(255)"))
    db.commit()
```

**Explication détaillée** : 
- `PRAGMA table_info(projets)` est une commande SQLite spéciale qui retourne des informations sur les colonnes de la table `projets`. Chaque ligne contient : `(cid, name, type, notnull, default_value, pk)`.
- `result.fetchall()` récupère toutes les lignes du résultat.
- `[col[1] for col in result.fetchall()]` est une liste en compréhension qui extrait seulement le nom de chaque colonne (index 1). Par exemple, si la table a les colonnes `id_projet`, `nom`, `date_debut`, on obtient `["id_projet", "nom", "date_debut"]`.
- `if "adresse" not in existing_columns:` vérifie si la colonne `adresse` n'existe pas déjà.
- `ALTER TABLE projets ADD COLUMN adresse VARCHAR(255)` ajoute la nouvelle colonne à la table existante. `VARCHAR(255)` signifie une chaîne de caractères de maximum 255 caractères.
- `db.commit()` applique la modification au fichier SQLite.

**Pourquoi c'est important** : Si on modifie le modèle Python pour ajouter un champ (ex: `adresse`), mais que la table SQLite existe déjà sans ce champ, on aurait une erreur. Cette vérification permet d'ajouter automatiquement les colonnes manquantes sans perdre les données existantes.

## 3. Téléchargement des Données pour DB Browser

### 3.1 Script de Téléchargement

Le script `download_construction_db.py` récupère toutes les données depuis l'API Render et les sauvegarde dans un fichier SQLite local. Ce fichier peut ensuite être ouvert avec DB Browser pour analyser les données.

### 3.2 Récupération via l'API

```python
def fetch_data_from_api(endpoint: str) -> List[Dict[str, Any]]:
    response = requests.get(f"{RENDER_URL}{endpoint}", timeout=30)
    if response.status_code == 200:
        data = response.json()
        items = data.get('data', [])
        return items
```

**Explication détaillée** : 
- `RENDER_URL` est l'URL de l'API sur Render (ex: `https://interface-cah-backend.onrender.com`).
- `requests.get()` fait une requête HTTP GET vers l'endpoint (ex: `/api/construction/projets`). `timeout=30` signifie qu'on attend maximum 30 secondes pour la réponse.
- `response.status_code == 200` vérifie que la requête a réussi (200 = OK). Si c'est 404, 500, etc., c'est une erreur.
- `response.json()` parse le contenu JSON de la réponse. L'API retourne généralement `{"success": true, "data": [...]}`.
- `data.get('data', [])` extrait la liste des éléments. Si la clé 'data' n'existe pas, on retourne une liste vide `[]` par défaut.
- La fonction retourne une liste de dictionnaires Python, chaque dictionnaire représentant un élément (ex: un projet, une commande, etc.).

**Flux** : Le script appelle l'API → L'API lit depuis SQLite sur Render → L'API retourne JSON → Le script reçoit les données.

### 3.3 Création de la Base Locale

```python
def create_local_database():
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS projets (
            id_projet INTEGER PRIMARY KEY,
            nom TEXT NOT NULL,
            date_debut TEXT,
            ...
        )
    ''')
    conn.commit()
```

**Explication détaillée** : 
- `sqlite3.connect(LOCAL_DB_PATH)` ouvre (ou crée si elle n'existe pas) une connexion à un fichier SQLite local. `LOCAL_DB_PATH` est typiquement `"data/construction_projects_local.db"`.
- `conn.cursor()` crée un curseur, qui est l'objet utilisé pour exécuter des commandes SQL.
- `CREATE TABLE IF NOT EXISTS projets (...)` crée la table `projets` seulement si elle n'existe pas déjà. Sans `IF NOT EXISTS`, on aurait une erreur si la table existe déjà.
- Les colonnes sont définies : `id_projet INTEGER PRIMARY KEY` (clé primaire auto-incrémentée), `nom TEXT NOT NULL` (texte obligatoire), `date_debut TEXT` (texte optionnel), etc.
- `conn.commit()` applique les changements au fichier SQLite local.

**Pourquoi créer la structure localement ?** On doit avoir les mêmes tables que sur Render pour pouvoir insérer les données. Le script définit la structure pour chaque table (projets, commandes, factures_st, etc.).

### 3.4 Insertion des Données

```python
def insert_data_to_local_db(table_name: str, data: List[Dict[str, Any]]):
    conn = sqlite3.connect(LOCAL_DB_PATH)
    cursor = conn.cursor()
    
    # Obtenir les colonnes de la table
    cursor.execute(f"PRAGMA table_info({table_name})")
    table_columns = [col[1] for col in cursor.fetchall()]
    
    # Filtrer les colonnes valides (exclure les relations imbriquées)
    columns = [col for col in table_columns if col in data[0].keys()]
    
    # Vider la table
    cursor.execute(f"DELETE FROM {table_name}")
    
    # Insérer chaque élément
    placeholders = ', '.join(['?' for _ in columns])
    for item in data:
        values = [item.get(col) for col in columns]
        cursor.execute(f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})", values)
    
    conn.commit()
```

**Explication détaillée** : 
- `PRAGMA table_info(table_name)` récupère la liste des colonnes de la table locale.
- `columns = [col for col in table_columns if col in data[0].keys()]` filtre pour garder seulement les colonnes qui existent à la fois dans la table ET dans les données JSON. Par exemple, si la table a `id_projet`, `nom`, `adresse` mais que les données JSON ont aussi `projet` (une relation imbriquée), on exclut `projet`.
- `DELETE FROM {table_name}` vide complètement la table avant d'insérer. Ça évite les doublons si on relance le script plusieurs fois.
- `placeholders = ', '.join(['?' for _ in columns])` crée une chaîne comme `"?, ?, ?"` pour chaque colonne. Les `?` sont des placeholders pour éviter les injections SQL.
- `for item in data:` itère sur chaque élément de la liste (ex: chaque projet).
- `values = [item.get(col) for col in columns]` extrait les valeurs dans le même ordre que les colonnes. Par exemple, si `columns = ["id_projet", "nom"]` et `item = {"id_projet": 1, "nom": "Maison"}`, on obtient `[1, "Maison"]`.
- `cursor.execute(f"INSERT INTO ... VALUES ({placeholders})", values)` insère une ligne. Les `?` sont remplacés par les valeurs de `values` de manière sécurisée.
- `conn.commit()` écrit toutes les insertions dans le fichier SQLite local.

**Résultat** : Après cette étape, le fichier `construction_projects_local.db` contient toutes les données de Render, prêtes à être ouvertes avec DB Browser.

### 3.5 Fonction Principale

```python
def download_all_construction_data():
    create_local_database()
    
    # Télécharger chaque type de données
    projets = fetch_data_from_api("/api/construction/projets")
    insert_data_to_local_db("projets", projets)
    
    commandes = fetch_data_from_api("/api/construction/commandes")
    insert_data_to_local_db("commandes", commandes)
    
    factures_st = fetch_data_from_api("/api/construction/factures-st")
    insert_data_to_local_db("factures_st", factures_st)
    
    # ... etc pour toutes les tables (employes, punchs_employes, fournisseurs, etc.)
```

**Explication détaillée** : 
- `create_local_database()` crée d'abord toutes les tables vides avec la bonne structure.
- Pour chaque type de données (projets, commandes, factures, etc.), le script :
  1. Appelle `fetch_data_from_api()` avec l'endpoint correspondant (ex: `/api/construction/projets`)
  2. Reçoit une liste de dictionnaires JSON
  3. Appelle `insert_data_to_local_db()` pour insérer ces données dans la table locale correspondante
- À la fin, le fichier `construction_projects_local.db` contient toutes les données de Render, organisées dans les mêmes tables.

**Utilisation avec DB Browser** : 
1. Exécuter le script : `python download_construction_db.py`
2. Ouvrir DB Browser SQLite
3. Ouvrir le fichier `data/construction_projects_local.db`
4. Naviguer dans les tables pour voir toutes les données, faire des requêtes SQL, exporter en CSV, etc.

## Conclusion

La base de données SQLite est stockée sur le disque persistant Render (`/opt/render/project/src/data/cah_database.db`). Ce disque persiste entre les redémarrages, contrairement au système de fichiers éphémère. 

Les modifications via l'API (création, mise à jour, suppression) écrivent directement dans ce fichier via SQLAlchemy et `session.commit()`. 

Le script de téléchargement `download_construction_db.py` récupère toutes les données via l'API (qui lit depuis le fichier SQLite sur Render) et les copie dans un fichier SQLite local (`construction_projects_local.db`). Ce fichier local peut ensuite être ouvert avec DB Browser pour analyser les données, faire des requêtes SQL, ou exporter les données.

