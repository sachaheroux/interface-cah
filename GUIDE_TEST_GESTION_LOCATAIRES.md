# Guide de Test - Gestion des Locataires

## Vue d'ensemble
La page "Locataires" permet maintenant de gérer complètement les locataires avec des formulaires complets, des détails, et toutes les opérations CRUD.

## Fonctionnalités Implémentées

### 1. Interface Principale
- **Bouton "Nouveau Locataire"** : Maintenant fonctionnel, ouvre le formulaire de création
- **Filtres et Recherche** : Recherche par nom, email, téléphone, immeuble + filtre par statut
- **Liste des Locataires** : Cartes avec informations essentielles et actions
- **Compteur** : Affiche le nombre de locataires filtrés

### 2. Formulaire de Locataire (TenantForm)
#### Sections du formulaire :
1. **Informations personnelles**
   - Nom complet (requis)
   - Email
   - Téléphone
   - Statut (Actif, En attente, Inactif, Ancien locataire)

2. **Adresse personnelle**
   - Adresse complète
   - Ville
   - Province (dropdown avec toutes les provinces canadiennes)
   - Code postal (formatage automatique en majuscules)

3. **Contact d'urgence**
   - Nom, téléphone, email
   - Relation (Parent, Conjoint(e), Enfant, etc.)

4. **Informations financières**
   - Revenu mensuel (avec aperçu formaté en CAD)
   - Cote de crédit (300-900)
   - Compte bancaire
   - Employeur et téléphone employeur

5. **Notes et commentaires**
   - Zone de texte libre pour notes additionnelles

### 3. Détails du Locataire (TenantDetails)
- **Vue complète** de toutes les informations
- **Sections conditionnelles** (n'affiche que les sections avec données)
- **Formatage professionnel** des devises, dates, adresses
- **Actions** : Modifier, Supprimer

### 4. Opérations CRUD
- **Création** : Nouveau locataire avec formulaire complet
- **Lecture** : Affichage des détails en modal
- **Mise à jour** : Modification via le même formulaire
- **Suppression** : Avec confirmation

## Tests à Effectuer

### Test 1 : Création d'un Nouveau Locataire
1. Cliquer sur "Nouveau Locataire"
2. Remplir au minimum le nom (requis)
3. Tester la validation (essayer de sauvegarder sans nom)
4. Remplir plusieurs sections
5. Vérifier le formatage automatique :
   - Code postal en majuscules
   - Aperçu du revenu en CAD
6. Sauvegarder et vérifier l'ajout à la liste

### Test 2 : Recherche et Filtres
1. Créer plusieurs locataires avec différents statuts
2. Tester la recherche par :
   - Nom
   - Email
   - Téléphone
   - Immeuble (si applicable)
3. Tester le filtre par statut
4. Vérifier le compteur de résultats
5. Tester "Effacer filtres"

### Test 3 : Affichage des Détails
1. Cliquer sur "Détails" d'un locataire
2. Vérifier l'affichage de toutes les sections remplies
3. Vérifier que les sections vides ne s'affichent pas
4. Tester le formatage :
   - Devises en CAD
   - Dates en format français
   - Adresses complètes
5. Tester les boutons d'action

### Test 4 : Modification
1. Cliquer sur "Modifier" depuis la liste ou les détails
2. Vérifier que le formulaire se pré-remplit
3. Modifier plusieurs champs
4. Sauvegarder et vérifier les changements
5. Vérifier la mise à jour de la date de modification

### Test 5 : Suppression
1. Cliquer sur le bouton de suppression (icône poubelle)
2. Vérifier la confirmation
3. Confirmer la suppression
4. Vérifier la suppression de la liste
5. Tester l'annulation de la suppression

### Test 6 : Gestion des États
1. Tester avec aucun locataire (empty state)
2. Tester avec recherche sans résultats
3. Vérifier les états de chargement
4. Tester la fermeture des modales (X, Annuler, clic extérieur)

### Test 7 : Responsivité
1. Tester sur mobile (colonnes adaptatives)
2. Tester sur tablette
3. Vérifier le défilement des modales sur petits écrans
4. Tester les formulaires sur différentes tailles

## Données de Test Suggérées

### Locataire 1 - Complet
```
Nom: Jean Dupont
Email: jean.dupont@email.com
Téléphone: (514) 555-0123
Statut: Actif
Adresse: 123 Rue Sainte-Catherine, Montréal, QC, H1A 1A1
Contact d'urgence: Marie Dupont, (514) 555-0124, conjoint
Revenu: 4500
Cote de crédit: 750
Employeur: Entreprise ABC
```

### Locataire 2 - Minimal
```
Nom: Sophie Martin
Statut: En attente
```

### Locataire 3 - Ancien
```
Nom: Pierre Tremblay
Email: pierre@email.com
Statut: Ancien locataire
Notes: A quitté en décembre 2023, bon locataire
```

## Points d'Attention

### Validation
- Le nom est le seul champ obligatoire
- Les autres champs sont optionnels mais formatés
- Validation du format email automatique

### Formatage
- Code postal automatiquement en majuscules
- Revenu affiché en format CAD
- Cote de crédit limitée à 300-900

### UX/UI
- Modales avec défilement sur petits écrans
- Fermeture par X, bouton Annuler, ou clic extérieur
- États de chargement pendant les opérations
- Confirmations pour les suppressions

### Intégration
- Les locataires créés ici peuvent être sélectionnés dans les formulaires d'unités
- Synchronisation avec le système centralisé de gestion des locataires

## Évolutions Futures Possibles
1. **Import/Export** de locataires en CSV
2. **Photos** de profil des locataires
3. **Historique** des modifications
4. **Notifications** pour les échéances (baux, etc.)
5. **Intégration** avec les documents (contrats, etc.)
6. **Rapports** sur les locataires
7. **Communications** intégrées (email, SMS)

## Architecture Technique

### Composants
- `Tenants.jsx` : Page principale avec liste et filtres
- `TenantForm.jsx` : Formulaire de création/modification
- `TenantDetails.jsx` : Modal d'affichage des détails
- `tenant.js` : Types et utilitaires pour les locataires

### État Local
- Gestion locale avec fallback API
- Synchronisation avec le backend via `tenantsService`
- États de chargement et d'erreur gérés

### Responsive Design
- Grilles adaptatives (1-2-3 colonnes)
- Modales avec défilement vertical
- Formulaires optimisés mobile 