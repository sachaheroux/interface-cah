# 🗺️ Guide de Test - Vue Carte des Immeubles

## 📋 Fonctionnalités Implémentées

### ✅ **Vue Carte Interactive**
- **Carte OpenStreetMap** avec zoom et navigation
- **Marqueurs personnalisés** pour chaque immeuble
- **Popups informatifs** avec détails de l'immeuble
- **Géocodage automatique** des adresses
- **Ajustement automatique** de la vue pour voir tous les immeubles

### ✅ **Fonctionnalités de Navigation**
- **Zoom** avec la molette de la souris
- **Pan** en glissant la carte
- **Contrôles de zoom** (+/-) 
- **Vue adaptative** selon le nombre d'immeubles

### ✅ **Marqueurs Intelligents**
- **Icônes personnalisées** en forme de bâtiment
- **Animation hover** (agrandissement au survol)
- **Popups riches** avec toutes les informations
- **Actions directes** (Voir détails, Modifier)

## 🧪 Comment Tester

### **1. Test de Base**
1. Ouvrez l'application : `http://localhost:5173`
2. Allez sur la page **Immeubles**
3. Cliquez sur **"Vue Carte"** dans les actions rapides
4. Vérifiez que la carte s'ouvre en modal

### **2. Test avec Immeubles Existants**
Si vous avez des immeubles :
- ✅ Les marqueurs apparaissent aux bons emplacements
- ✅ Cliquez sur un marqueur → popup avec infos
- ✅ Testez "Détails" et "Modifier" dans le popup
- ✅ La carte s'ajuste pour voir tous les immeubles

### **3. Test de Géocodage**
1. Créez un nouvel immeuble avec une adresse réelle :
   - **Exemple** : "1000 Rue Sainte-Catherine, Montréal, QC"
   - **Exemple** : "400 Boulevard Jean-Lesage, Québec, QC"
2. Ouvrez la vue carte
3. Vérifiez que l'immeuble apparaît au bon endroit

### **4. Test des Contrôles**
- **Zoom** : Molette de souris ou boutons +/-
- **Navigation** : Glissez pour déplacer la carte
- **Fermeture** : Bouton X ou clic en dehors

## 🎯 **Résultats Attendus**

### ✅ **Affichage Correct**
- Carte OpenStreetMap claire et responsive
- Marqueurs bleus avec icône de bâtiment
- Popups bien formatés avec toutes les infos
- Footer avec statistiques

### ✅ **Géolocalisation**
- Adresses réelles → emplacements précis
- Adresses approximatives → coordonnées par ville
- Fallback vers Montréal si géocodage échoue

### ✅ **Performance**
- Chargement rapide de la carte
- Géocodage en arrière-plan
- Animations fluides

## 🔧 **Dépannage**

### **Si la carte ne s'affiche pas :**
1. Vérifiez la console du navigateur (F12)
2. Assurez-vous que Leaflet est installé : `npm list leaflet`
3. Vérifiez que les styles CSS sont chargés

### **Si les marqueurs n'apparaissent pas :**
1. Vérifiez que les immeubles ont des adresses
2. Regardez les logs de géocodage dans la console
3. Le géocodage peut prendre quelques secondes

### **Si le géocodage échoue :**
- Les immeubles apparaîtront quand même avec des coordonnées approximatives
- Vérifiez votre connexion internet
- L'API Nominatim peut avoir des limites de taux

## 📱 **Test sur Différents Écrans**

### **Desktop**
- Modal plein écran avec header/footer
- Contrôles de zoom visibles
- Popups bien positionnés

### **Mobile/Tablet**
- Modal responsive
- Contrôles tactiles fonctionnels
- Texte lisible dans les popups

## 🚀 **Fonctionnalités Avancées**

### **Géocodage Intelligent**
- **Cache** pour éviter les requêtes répétées
- **Fallback** vers coordonnées approximatives
- **Support** adresses string et objets

### **Marqueurs Personnalisés**
- **Design** cohérent avec l'interface
- **Animations** smooth au hover
- **Couleurs** selon le thème de l'app

### **Popups Riches**
- **Informations complètes** : nom, type, adresse, unités, valeur
- **Actions directes** : voir détails, modifier
- **Design responsive** et moderne

## 📊 **Données de Test Recommandées**

Créez des immeubles avec ces adresses pour tester :

```
1. Immeuble Montréal Centre
   Adresse: 1000 Rue Sainte-Catherine, Montréal, QC

2. Immeuble Québec Vieux-Port  
   Adresse: 400 Boulevard Jean-Lesage, Québec, QC

3. Immeuble Laval
   Adresse: 1555 Boulevard Chomedey, Laval, QC

4. Immeuble Longueuil
   Adresse: 825 Rue Saint-Laurent, Longueuil, QC
```

## 🎉 **Validation Finale**

La fonctionnalité carte est réussie si :
- ✅ Modal s'ouvre/ferme correctement
- ✅ Marqueurs apparaissent aux bons endroits
- ✅ Zoom et navigation fonctionnent
- ✅ Popups affichent les bonnes informations
- ✅ Actions "Détails" et "Modifier" fonctionnent
- ✅ Performance fluide même avec plusieurs immeubles

---

**🗺️ Profitez de votre nouvelle vue carte interactive !** 