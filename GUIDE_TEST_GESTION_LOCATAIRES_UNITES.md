# Guide - Système de Gestion Centralisée des Locataires et Unités

## 🎯 **Nouveau Système Implémenté**

### ✅ **Gestion Centralisée des Locataires**
- **Base de données centralisée** : Tous les locataires sont gérés dans un système unique
- **Sélection par dropdown** : Plus de saisie manuelle, sélection depuis la liste existante
- **Création rapide** : Possibilité de créer un nouveau locataire directement depuis le formulaire d'unité
- **Synchronisation automatique** : Les informations sont synchronisées entre les modules

## 🔄 **Fonctionnement du Système**

### **1. Architecture des Données**
```
Locataires (Source de vérité)
├── ID unique
├── Informations personnelles
├── Contact d'urgence
├── Statut (Actif, En attente, etc.)
└── Métadonnées

Unités
├── tenantId (Référence vers Locataires)
├── tenant (Copie pour affichage)
├── Dates spécifiques (emménagement/déménagement)
└── Informations locatives
```

### **2. Flux de Travail**

#### **Scénario A : Assigner un Locataire Existant**
1. **Ouvrir** le formulaire d'unité (Modifier)
2. **Sélectionner** un locataire dans le dropdown
3. **Ajouter** les dates d'emménagement/déménagement
4. **Sauvegarder** → L'unité est liée au locataire

#### **Scénario B : Créer un Nouveau Locataire**
1. **Cliquer** "Nouveau" dans le sélecteur de locataire
2. **Remplir** nom, email, téléphone (nom obligatoire)
3. **Créer** → Le locataire est ajouté à la base centrale
4. **Sélection automatique** du nouveau locataire
5. **Continuer** avec les dates d'emménagement

#### **Scénario C : Libérer une Unité**
1. **Sélectionner** "Aucun locataire (unité libre)"
2. **Changer** le statut à "Libre"
3. **Sauvegarder** → L'unité devient disponible

## 🧪 **Tests à Effectuer**

### **Test 1 : Sélection de Locataire Existant**
```
1. Aller dans "Toutes les unités"
2. Modifier une unité libre
3. Sélectionner un locataire dans la liste
4. Vérifier que les infos se remplissent automatiquement
5. Ajouter une date d'emménagement
6. Changer le statut à "Occupée"
7. Sauvegarder et vérifier l'affichage
```

### **Test 2 : Création de Nouveau Locataire**
```
1. Modifier une unité
2. Cliquer "Nouveau" dans le sélecteur
3. Remplir : "Marie Dubois", "marie@email.com", "(514) 555-0123"
4. Cliquer "Créer le locataire"
5. Vérifier qu'il apparaît dans la liste
6. Vérifier qu'il est automatiquement sélectionné
7. Compléter et sauvegarder
```

### **Test 3 : Gestion des États**
```
1. Assigner un locataire → Statut "Occupée"
2. Retirer le locataire → Statut "Libre"
3. Vérifier les statistiques du tableau de bord
4. Tester les filtres par statut
```

### **Test 4 : Synchronisation avec Module Locataires**
```
1. Créer un locataire depuis les unités
2. Aller dans "Locataires" (menu principal)
3. Vérifier qu'il apparaît dans la liste
4. Modifier ses infos dans le module Locataires
5. Retourner aux unités et vérifier la synchronisation
```

## 🎨 **Interface Utilisateur**

### **Sélecteur de Locataire**
- **Dropdown** avec tous les locataires disponibles
- **Format** : "Nom - Email ou Téléphone"
- **Option** "Aucun locataire (unité libre)" en premier
- **Bouton "Nouveau"** pour création rapide

### **Formulaire de Création Rapide**
- **Champs** : Nom (obligatoire), Email, Téléphone
- **Interface** : Encadré gris avec boutons Créer/Annuler
- **Validation** : Nom requis, formats email/téléphone
- **Feedback** : Sélection automatique après création

### **Informations Spécifiques à l'Unité**
- **Dates** d'emménagement/déménagement uniquement
- **Masquage** automatique si aucun locataire sélectionné
- **Persistance** des dates lors du changement de locataire

## 📊 **Avantages du Nouveau Système**

### **1. Cohérence des Données**
- ✅ **Source unique** de vérité pour les locataires
- ✅ **Pas de doublons** ou d'incohérences
- ✅ **Mise à jour centralisée** des informations

### **2. Efficacité Opérationnelle**
- ✅ **Sélection rapide** au lieu de ressaisie
- ✅ **Création rapide** si nécessaire
- ✅ **Historique complet** des locataires

### **3. Gestion Avancée**
- ✅ **Suivi des locataires** entre différentes unités
- ✅ **Historique des locations** par locataire
- ✅ **Rapports consolidés** possible

## 🔧 **Fonctionnalités Techniques**

### **API et Services**
```javascript
// Chargement des locataires
tenantsService.getTenants()

// Création d'un nouveau locataire
tenantsService.createTenant(data)

// Liaison unité-locataire
unit.tenantId = selectedTenant.id
unit.tenant = { ...selectedTenant, moveInDate, moveOutDate }
```

### **États de l'Interface**
- **Loading** : Chargement des locataires
- **Selection** : Dropdown avec options
- **Creation** : Formulaire de nouveau locataire
- **Assignment** : Informations spécifiques à l'unité

## 🚀 **Scénarios d'Usage Réels**

### **Gestionnaire Immobilier**
1. **Nouveau locataire** : Créer depuis le formulaire d'unité
2. **Mutation interne** : Déplacer un locataire existant vers une autre unité
3. **Départ** : Libérer l'unité en retirant le locataire
4. **Retour** : Réassigner un ancien locataire

### **Données de Test Suggérées**

#### **Locataires Existants** (dans le système)
```
1. Jean Dupont - jean.dupont@email.com - (514) 555-0001
2. Marie Martin - marie.martin@email.com - (514) 555-0002  
3. Pierre Durand - pierre.durand@email.com - (514) 555-0003
```

#### **Nouveaux Locataires à Créer**
```
1. Sophie Tremblay - sophie.t@email.com - (438) 555-0004
2. Michel Leblanc - michel.leblanc@email.com - (450) 555-0005
3. Julie Gagnon - julie.g@email.com - (514) 555-0006
```

## ✅ **Critères de Validation**

### **Fonctionnalité**
- [ ] **Sélection** d'un locataire existant fonctionne
- [ ] **Création** d'un nouveau locataire fonctionne
- [ ] **Synchronisation** automatique des informations
- [ ] **Persistance** des données après sauvegarde

### **Interface**
- [ ] **Dropdown** bien formaté et lisible
- [ ] **Formulaire** de création intuitive
- [ ] **États** visuels clairs (libre/occupé)
- [ ] **Responsive** sur tous les appareils

### **Intégration**
- [ ] **Statistiques** mises à jour automatiquement
- [ ] **Filtres** fonctionnent avec les nouvelles données
- [ ] **Navigation** fluide entre les modules
- [ ] **Performance** acceptable avec de nombreux locataires

## 🔮 **Évolutions Futures**

### **Court Terme**
1. **Historique des locations** par locataire
2. **Recherche** dans le sélecteur de locataires
3. **Validation** des formats email/téléphone

### **Moyen Terme**
1. **Gestion des contrats** de location
2. **Notifications** de fin de bail
3. **Rapports** de revenus par locataire

### **Long Terme**
1. **Module complet** de gestion des locataires
2. **Intégration** avec systèmes de paiement
3. **Portail locataire** en ligne

## 📝 **Notes Importantes**

- **Migration** : Les unités existantes conservent leurs données locataires actuelles
- **Compatibilité** : Le système fonctionne avec et sans locataire assigné
- **Performance** : Chargement optimisé des locataires à l'ouverture du formulaire
- **Sécurité** : Validation côté client et serveur pour les nouveaux locataires 