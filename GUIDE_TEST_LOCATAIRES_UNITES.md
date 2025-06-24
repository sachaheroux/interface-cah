# Guide de Test - Gestion Locataires et Unités Améliorée

## Nouvelles Fonctionnalités Implémentées

### 1. Recherche d'Unités dans le Formulaire Locataire
- **Barre de recherche** remplace le menu déroulant
- **Recherche en temps réel** par adresse, immeuble, ou numéro d'unité
- **Affichage des locataires actuels** pour chaque unité
- **Support de plusieurs locataires par unité** (jusqu'à 4)

### 2. Affichage Direct des Locataires dans les Fiches d'Unités
- **Section "Locataires Assignés"** remplace la sélection manuelle
- **Informations complètes** de chaque locataire
- **Bouton de suppression** pour retirer un locataire de l'unité
- **Indicateur de capacité** (ex: 2/4 locataires)

## Tests à Effectuer

### A. Test de la Recherche d'Unités (Formulaire Locataire)

#### 1. Navigation vers les Locataires
```
1. Aller dans "Locataires" dans la navigation
2. Cliquer sur "Nouveau Locataire"
3. Remplir les informations de base du locataire
4. Arriver à la section "Unité de Résidence"
```

#### 2. Test de la Barre de Recherche
```
✓ Vérifier que la barre de recherche s'affiche avec le placeholder
✓ Taper "4932" → Doit filtrer les unités contenant cette adresse
✓ Taper "Route" → Doit filtrer par nom de rue
✓ Taper "Immeuble" → Doit filtrer par nom d'immeuble
✓ Taper "101" → Doit filtrer par numéro d'unité
✓ Effacer le texte → Doit afficher les 20 premières unités
```

#### 3. Test de Sélection d'Unité
```
✓ Cliquer sur une unité → Doit la sélectionner (bordure bleue)
✓ Vérifier l'aperçu détaillé en bas avec toutes les infos
✓ Voir les locataires actuels s'il y en a (badges verts)
✓ Cliquer sur "Désélectionner l'unité" → Doit retirer la sélection
```

#### 4. Test des Locataires Multiples
```
✓ Sélectionner une unité qui a déjà des locataires
✓ Vérifier que les locataires actuels sont affichés
✓ Assigner le nouveau locataire à cette unité
✓ Vérifier que l'unité peut avoir plusieurs locataires
```

### B. Test des Fiches d'Unités Améliorées

#### 1. Accès aux Fiches d'Unités
```
1. Aller dans "Immeubles" → "Toutes les unités"
2. Cliquer sur "Détails" d'une unité avec locataires
3. Vérifier la section "Locataires Assignés"
```

#### 2. Test de l'Affichage des Locataires
```
✓ Voir tous les locataires assignés à l'unité
✓ Vérifier les informations complètes (nom, email, téléphone)
✓ Voir la date d'emménagement si disponible
✓ Vérifier le compteur "X/4 locataires"
```

#### 3. Test de Suppression de Locataires
```
✓ Cliquer sur l'icône poubelle d'un locataire
✓ Confirmer la suppression dans la boîte de dialogue
✓ Vérifier que le locataire est retiré de l'unité
✓ Vérifier que le compteur se met à jour
```

### C. Test de Cohérence des Données

#### 1. Synchronisation Locataire ↔ Unité
```
✓ Assigner un locataire à une unité via le formulaire locataire
✓ Vérifier qu'il apparaît dans la fiche de l'unité
✓ Retirer le locataire de l'unité
✓ Vérifier qu'il n'apparaît plus dans la liste des unités du locataire
```

#### 2. Test des Limites
```
✓ Essayer d'assigner plus de 4 locataires à une unité
✓ Vérifier que l'unité reste disponible jusqu'à 4 locataires
✓ Vérifier qu'elle disparaît des unités "disponibles" après 4 locataires
```

### D. Test de Performance et UX

#### 1. Recherche en Temps Réel
```
✓ Taper rapidement dans la barre de recherche
✓ Vérifier que les résultats se mettent à jour fluidement
✓ Vérifier la limitation à 50 résultats maximum
```

#### 2. Interface Responsive
```
✓ Tester sur mobile/tablette
✓ Vérifier que la recherche fonctionne sur tous les écrans
✓ Vérifier l'affichage des cartes de locataires sur mobile
```

## Scénarios de Test Complets

### Scénario 1: Famille avec Enfants
```
1. Créer un locataire principal "Jean Dupont"
2. L'assigner à l'unité "4932 Route Des Vétérans - Unité 1"
3. Créer sa conjointe "Marie Dupont"
4. L'assigner à la même unité
5. Vérifier que l'unité affiche 2/4 locataires
6. Ouvrir la fiche de l'unité et voir les deux locataires
```

### Scénario 2: Colocation Étudiante
```
1. Créer 4 étudiants différents
2. Les assigner tous à la même unité
3. Vérifier que l'unité affiche 4/4 locataires
4. Vérifier qu'elle n'apparaît plus dans les unités disponibles
5. Retirer un étudiant
6. Vérifier qu'elle redevient disponible (3/4)
```

### Scénario 3: Recherche Efficace
```
1. Avoir au moins 20 unités dans le système
2. Chercher une adresse spécifique
3. Vérifier que les résultats sont pertinents
4. Sélectionner une unité avec des locataires existants
5. Assigner un nouveau locataire
6. Vérifier la mise à jour en temps réel
```

## Points d'Attention

### Erreurs Potentielles
- Vérifier que la recherche fonctionne avec les caractères spéciaux (é, à, ç)
- S'assurer que les unités sans adresse ne cassent pas la recherche
- Vérifier que la suppression de locataires met à jour les statistiques

### Performance
- La recherche doit être fluide même avec 100+ unités
- Le chargement des locataires assignés doit être rapide
- Les mises à jour doivent être instantanées

### Accessibilité
- Vérifier que la barre de recherche est accessible au clavier
- S'assurer que les boutons ont des tooltips explicites
- Vérifier le contraste des couleurs pour les badges de locataires

## Données de Test Recommandées

### Créer ces Unités pour Tester
```
1. 4932 Route Des Vétérans - Unité 1 (vide)
2. 4934 Route Des Vétérans - Unité 2 (1 locataire)
3. 4936 Route Des Vétérans - Unité 3 (2 locataires)
4. 4490 Rue Denault - Unité 1 (3 locataires)
5. 97A St-Alphonse - Unité A (4 locataires - pleine)
```

### Créer ces Locataires
```
1. Jean Dupont (jean@email.com, 514-555-0001)
2. Marie Dupont (marie@email.com, 514-555-0002)
3. Pierre Martin (pierre@email.com, 514-555-0003)
4. Sophie Tremblay (sophie@email.com, 514-555-0004)
5. Alex Johnson (alex@email.com, 514-555-0005)
```

## Résultats Attendus

Après tous ces tests, vous devriez avoir :
- ✅ Une recherche d'unités fluide et intuitive
- ✅ Un système de locataires multiples fonctionnel
- ✅ Une synchronisation parfaite entre locataires et unités
- ✅ Une interface moderne et responsive
- ✅ Des données cohérentes dans tout le système 