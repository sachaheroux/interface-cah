# Guide de Test : Intégration Locataires-Unités

## Vue d'ensemble
Ce guide teste la nouvelle fonctionnalité d'intégration entre les locataires et les unités, où les locataires sont assignés directement aux unités disponibles au lieu d'avoir une adresse personnelle séparée.

## Fonctionnalités à Tester

### 1. Création/Modification de Locataire avec Sélection d'Unité

**Étapes :**
1. Aller dans la section "Locataires"
2. Cliquer sur "Nouveau Locataire"
3. Vérifier que la section "Unité de Résidence" remplace l'ancienne section "Adresse personnelle"
4. Remplir les informations de base (nom, email, téléphone)
5. Dans la sélection d'unité :
   - Vérifier que les unités disponibles s'affichent
   - Format attendu : "Nom Immeuble - Unité X (Adresse complète)"
   - Sélectionner une unité
   - Vérifier que l'aperçu de l'unité s'affiche avec les détails

**Résultats attendus :**
- ✅ Dropdown avec toutes les unités disponibles (non occupées)
- ✅ Aperçu détaillé de l'unité sélectionnée
- ✅ Message informatif si aucune unité disponible
- ✅ Animation de chargement pendant la récupération des unités

### 2. Assignation Automatique Locataire-Unité

**Étapes :**
1. Créer un locataire avec une unité sélectionnée
2. Sauvegarder le locataire
3. Vérifier que l'assignation est créée dans localStorage
4. Aller dans la vue "Toutes les unités"
5. Vérifier que l'unité assignée montre maintenant le locataire

**Résultats attendus :**
- ✅ Assignation sauvegardée dans `unitTenantAssignments` localStorage
- ✅ Unité marquée comme occupée avec informations du locataire
- ✅ Synchronisation bidirectionnelle locataire ↔ unité

### 3. Affichage des Détails de Locataire avec Unité

**Étapes :**
1. Ouvrir les détails d'un locataire assigné à une unité
2. Vérifier la section "Unité de Résidence"
3. Vérifier les statistiques en haut (unité assignée)

**Résultats attendus :**
- ✅ Section "Unité de Résidence" avec informations complètes
- ✅ Adresse complète de l'unité
- ✅ Nom de l'immeuble et numéro d'unité
- ✅ Type d'unité, superficie, loyer mensuel
- ✅ Message informatif si aucune unité assignée

### 4. Modification d'Assignation d'Unité

**Étapes :**
1. Modifier un locataire existant
2. Changer l'unité assignée
3. Sauvegarder
4. Vérifier que l'ancienne assignation est supprimée
5. Vérifier que la nouvelle assignation est créée

**Résultats attendus :**
- ✅ Une seule assignation par locataire
- ✅ L'ancienne unité redevient disponible
- ✅ La nouvelle unité devient occupée

### 5. Gestion des Unités Disponibles

**Étapes :**
1. Créer plusieurs immeubles avec différents formats d'adresse
2. Vérifier que toutes les unités sont générées correctement
3. Assigner des locataires à quelques unités
4. Créer un nouveau locataire
5. Vérifier que seules les unités non assignées apparaissent

**Résultats attendus :**
- ✅ Génération correcte des unités depuis tous les immeubles
- ✅ Filtrage automatique des unités occupées
- ✅ Mise à jour en temps réel de la disponibilité

## Tests de Cas Limites

### Cas 1 : Aucune Unité Disponible
- Assigner tous les locataires aux unités
- Créer un nouveau locataire
- Vérifier le message "Aucune unité disponible"

### Cas 2 : Locataire Sans Unité
- Créer un locataire sans sélectionner d'unité
- Vérifier l'affichage dans les détails
- Message "Aucune unité assignée"

### Cas 3 : Modification d'Immeuble
- Modifier un immeuble (changer le nombre d'unités)
- Vérifier l'impact sur les assignations existantes
- Vérifier la génération des nouvelles unités

## Données de Test Recommandées

### Immeubles à Créer
1. **Immeuble Simple**
   - Nom : "Résidence Maple"
   - Adresse : "123 Rue Principale, Montréal, QC"
   - 4 unités

2. **Immeuble avec Adresses Multiples**
   - Nom : "Complexe des Vétérans"
   - Adresse : "4932-4934-4936 Route Des Vétérans"
   - 6 unités

3. **Immeuble avec Numéros**
   - Nom : "Tours Denault"
   - Adresse : "4490, 1-2-3-4-5-6, Rue Denault"
   - 8 unités

### Locataires à Créer
1. **Locataire Complet**
   - Nom : "Jean Dupont"
   - Email : "jean.dupont@email.com"
   - Téléphone : "(514) 555-0123"
   - Unité : Résidence Maple - Unité 1
   - Contact d'urgence complet
   - Informations financières

2. **Locataire Minimal**
   - Nom : "Marie Martin"
   - Unité : Complexe des Vétérans - Unité 4932

3. **Locataire Sans Unité**
   - Nom : "Pierre Durand"
   - Aucune unité sélectionnée

## Vérifications Techniques

### LocalStorage
Vérifier la structure des données dans `unitTenantAssignments` :
```json
[
  {
    "unitId": "1-1",
    "tenantId": 123,
    "tenantData": {
      "name": "Jean Dupont",
      "email": "jean.dupont@email.com",
      "phone": "(514) 555-0123",
      "moveInDate": "2024-01-15T10:00:00.000Z",
      "moveOutDate": null
    },
    "assignedAt": "2024-01-15T10:00:00.000Z"
  }
]
```

### Console Logs
Surveiller les logs pour :
- ✅ "Available units:" - Liste des unités disponibles
- ✅ "Assigning tenant to unit:" - Assignation en cours
- ✅ "Tenant assigned to unit successfully" - Assignation réussie
- ❌ Erreurs d'assignation ou de chargement

## Résultats Attendus Globaux

1. **Interface Utilisateur**
   - Formulaire de locataire moderne avec sélection d'unité
   - Détails de locataire avec informations d'unité complètes
   - Messages informatifs appropriés

2. **Fonctionnalité**
   - Assignation automatique locataire ↔ unité
   - Synchronisation bidirectionnelle
   - Gestion des unités disponibles

3. **Données**
   - Persistance des assignations
   - Cohérence entre locataires et unités
   - Pas de doublons d'assignation

4. **Performance**
   - Chargement rapide des unités
   - Interface réactive
   - Pas de blocages lors des assignations 