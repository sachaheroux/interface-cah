// Types et modèles pour les immeubles

export const defaultBuilding = {
  id: null,
  nom_immeuble: '',
  adresse: '',
  ville: '',
  province: '',
  code_postal: '',
  pays: 'Canada',
  nbr_unite: 1,
  annee_construction: new Date().getFullYear(),
  prix_achete: 0,
  mise_de_fond: 0,
  taux_interet: 0,
  valeur_actuel: 0,
  proprietaire: '',
  banque: '',
  contracteur: '',
  notes: '',
  date_creation: null,
  date_modification: null
} 