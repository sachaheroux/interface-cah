// Types et modèles pour les unités d'immeubles

export const defaultUnit = {
  id: null,
  id_immeuble: null,
  nom_immeuble: '',
  adresse_unite: '',
  type: '1 1/2',
  nbr_chambre: 1,
  nbr_salle_de_bain: 1,
  
  // Métadonnées
  date_creation: null,
  date_modification: null
}

// Fonction pour obtenir le label du type d'unité
export const getUnitTypeLabel = (type) => {
  return type || '1 1/2'
}
