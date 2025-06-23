# Guide de Test - Fonctionnalité des Unités

## Vue d'ensemble

La nouvelle fonctionnalité "Toutes les unités" génère automatiquement des fiches d'unités basées sur les immeubles existants en analysant les formats d'adresse.

## Formats d'adresse supportés

### Format 1: Adresses séparées par tirets
**Exemple :** `4932-4934-4936 Route Des Vétérans`

**Résultat :**
- Unité #1 : `4932 Route Des Vétérans`
- Unité #2 : `4934 Route Des Vétérans`  
- Unité #3 : `4936 Route Des Vétérans`

### Format 2: Numéro de base avec unités numérotées
**Exemple :** `4490, 1-2-3-4-5-6, Rue Denault`

**Résultat :**
- Unité #1 : `4490 #1 Rue Denault`
- Unité #2 : `4490 #2 Rue Denault`
- Unité #3 : `4490 #3 Rue Denault`
- Unité #4 : `4490 #4 Rue Denault`
- Unité #5 : `4490 #5 Rue Denault`
- Unité #6 : `4490 #6 Rue Denault`

### Format 3: Adresse standard
**Exemple :** `123 Rue Principale` avec 4 unités dans l'immeuble

**Résultat :**
- Unité #1 : `123 Rue Principale #1`
- Unité #2 : `123 Rue Principale #2`
- Unité #3 : `123 Rue Principale #3`
- Unité #4 : `123 Rue Principale #4`

## Gestion des caractères spéciaux

### Adresses avec lettres
**Exemple :** `97A-97B-97C St-Alphonse`

**Résultat :**
- Unité #1 : `97A St-Alphonse`
- Unité #2 : `97B St-Alphonse`
- Unité #3 : `97C St-Alphonse`

## Tests à effectuer

### 1. Test de génération automatique
1. Aller dans **Immeubles** → **Tous les immeubles**
2. Créer un nouvel immeuble avec l'adresse : `4932-4934-4936 Route Des Vétérans`
3. Définir **3 unités** dans le formulaire
4. Sauvegarder l'immeuble
5. Aller dans **Toutes les unités**
6. Vérifier que 3 unités sont générées avec les bonnes adresses

### 2. Test du format avec virgules
1. Créer un immeuble avec l'adresse : `4490, 1-2-3-4, Rue Denault`
2. Définir **4 unités**
3. Vérifier dans **Toutes les unités** que les adresses sont : 
   - `4490 #1 Rue Denault`
   - `4490 #2 Rue Denault`
   - `4490 #3 Rue Denault`
   - `4490 #4 Rue Denault`

### 3. Test du format standard
1. Créer un immeuble avec l'adresse : `123 Rue Principale`
2. Définir **2 unités**
3. Vérifier que les unités générées sont :
   - `123 Rue Principale #1`
   - `123 Rue Principale #2`

## Fonctionnalités de la vue Unités

### Statistiques affichées
- **Total Unités** : Nombre total d'unités générées
- **Occupées** : Unités avec statut "Occupée" 
- **Libres** : Unités avec statut "Libre"
- **Revenus Totaux** : Somme de tous les loyers mensuels
- **Taux Occupation** : Pourcentage d'unités occupées

### Filtres et recherche
- **Recherche** : Par adresse, nom d'immeuble, nom de locataire, numéro d'unité
- **Statut** : Occupée, Libre, Maintenance, Réservée
- **Immeuble** : Filtrer par immeuble spécifique
- **Effacer filtres** : Bouton pour réinitialiser tous les filtres

### Informations par unité
- **En-tête** : Numéro d'unité, nom de l'immeuble, statut
- **Adresse** : Adresse complète de l'unité
- **Type** : Studio, 1 chambre, 2 chambres, etc.
- **Superficie** : En pieds carrés (si renseignée)
- **Loyer** : Montant mensuel (si renseigné)
- **Locataire** : Nom, email, téléphone (si renseigné)
- **Services inclus** : Badges visuels pour chaque service

### Services inclus supportés
- 🌡️ **Chauffage** : Chauffage inclus dans le loyer
- ⚡ **Électricité** : Électricité incluse
- 📶 **WiFi** : Internet inclus
- 🛋️ **Meublé** : Unité meublée
- 🚗 **Stationnement** : Place de parking incluse
- 💧 **Buanderie** : Accès buanderie
- 🌪️ **Climatisation** : Climatisation installée
- 🏠 **Balcon** : Présence d'un balcon
- 📦 **Rangement** : Espace de rangement supplémentaire
- 🍽️ **Lave-vaisselle** : Lave-vaisselle installé
- 👕 **Laveuse-sécheuse** : Laveuse-sécheuse dans l'unité

## Synchronisation avec les immeubles

### Génération automatique
- Les unités sont **générées automatiquement** à partir des immeubles existants
- Chaque modification d'immeuble **met à jour** les unités correspondantes
- Le **nombre d'unités** dans l'immeuble détermine le nombre d'unités générées

### Communication bidirectionnelle
- **Immeubles → Unités** : Création/modification d'immeuble génère les unités
- **Unités → Immeubles** : Les statistiques d'unités remontent au niveau immeuble

## Cas d'erreur à tester

### Adresses malformées
- Tester avec des adresses qui ne correspondent à aucun format
- Vérifier que le système utilise le format standard par défaut

### Nombre d'unités incohérent
- Créer un immeuble avec 5 unités mais une adresse qui indique 3 adresses
- Vérifier le comportement du système

### Caractères spéciaux
- Tester avec des accents, apostrophes, traits d'union
- Exemple : `123 Rue de l'Église`

## Prochaines améliorations possibles

1. **Édition des unités** : Permettre la modification des informations d'unité
2. **Gestion des locataires** : Interface complète de gestion des locataires
3. **Historique des loyers** : Suivi des paiements et historique
4. **Contrats de location** : Gestion des baux et documents
5. **Maintenance par unité** : Suivi des réparations par unité
6. **Photos des unités** : Galerie de photos pour chaque unité 