// Service de géocodage pour convertir les adresses en coordonnées
// Utilise l'API Nominatim d'OpenStreetMap (gratuite)

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org/search'

// Cache pour éviter les requêtes répétées
const geocodeCache = new Map()

/**
 * Convertit une adresse en coordonnées latitude/longitude
 * @param {Object} address - Objet adresse avec street, city, province, country
 * @returns {Promise<Object>} - Coordonnées {lat, lng} ou null si non trouvé
 */
export const geocodeAddress = async (address) => {
  try {
    // Construire l'adresse complète pour la recherche
    const addressParts = [];
    if (address.street) addressParts.push(address.street);
    if (address.city) addressParts.push(address.city);
    if (address.province) addressParts.push(address.province);
    if (address.country) addressParts.push(address.country);
    
    const fullAddress = addressParts.join(', ');
    
    console.log(`🔍 Géocodage de: "${fullAddress}"`);
    
    const params = new URLSearchParams({
      q: fullAddress,
      format: 'json',
      limit: '1',
      countrycodes: address.country === 'Canada' ? 'ca' : '',
      addressdetails: '1'
    });

    const response = await fetch(`${NOMINATIM_BASE_URL}?${params}`, {
      headers: {
        'User-Agent': 'Interface-CAH/1.0 (contact@interface-cah.com)'
      }
    });

    if (!response.ok) {
      throw new Error(`Erreur HTTP: ${response.status}`);
    }

    const data = await response.json();
    
    if (data && data.length > 0) {
      const result = data[0];
      const coordinates = {
        lat: parseFloat(result.lat),
        lng: parseFloat(result.lon)
      };
      
      console.log(`✅ Coordonnées trouvées: ${coordinates.lat}, ${coordinates.lng}`);
      return coordinates;
    } else {
      console.warn(`⚠️ Aucune coordonnée trouvée pour: ${fullAddress}`);
      return null;
    }
  } catch (error) {
    console.error('❌ Erreur de géocodage:', error);
    return null;
  }
};

/**
 * Géocode tous les immeubles et retourne ceux avec des coordonnées valides
 * @param {Array} buildings - Liste des immeubles
 * @returns {Promise<Array>} - Immeubles avec coordonnées
 */
export const geocodeBuildings = async (buildings) => {
  console.log(`🗺️ Géocodage de ${buildings.length} immeubles...`);
  
  const buildingsWithCoords = [];
  
  for (const building of buildings) {
    if (!building.address) {
      console.warn(`⚠️ Immeuble "${building.name}" sans adresse`);
      continue;
    }
    
    // Attendre un peu entre les requêtes pour respecter les limites de l'API
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    const coordinates = await geocodeAddress(building.address);
    
    if (coordinates) {
      buildingsWithCoords.push({
        ...building,
        coordinates
      });
    }
  }
  
  console.log(`✅ ${buildingsWithCoords.length}/${buildings.length} immeubles géocodés avec succès`);
  return buildingsWithCoords;
};

/**
 * Calcule les limites géographiques pour englober tous les immeubles
 * @param {Array} buildingsWithCoords - Immeubles avec coordonnées
 * @returns {Object} - Limites {north, south, east, west} ou null
 */
export const calculateBounds = (buildingsWithCoords) => {
  if (!buildingsWithCoords || buildingsWithCoords.length === 0) {
    return null;
  }
  
  const coords = buildingsWithCoords.map(b => b.coordinates);
  
  const bounds = {
    north: Math.max(...coords.map(c => c.lat)),
    south: Math.min(...coords.map(c => c.lat)),
    east: Math.max(...coords.map(c => c.lng)),
    west: Math.min(...coords.map(c => c.lng))
  };
  
  // Ajouter une marge de 10% pour éviter que les marqueurs soient collés aux bords
  const latMargin = (bounds.north - bounds.south) * 0.1;
  const lngMargin = (bounds.east - bounds.west) * 0.1;
  
  bounds.north += latMargin;
  bounds.south -= latMargin;
  bounds.east += lngMargin;
  bounds.west -= lngMargin;
  
  console.log(`📏 Limites calculées:`, bounds);
  return bounds;
};

/**
 * Géocoder plusieurs adresses en parallèle
 * @param {Array} addresses - Tableau d'adresses
 * @returns {Promise<Array>} - Tableau de coordonnées
 */
export async function geocodeMultipleAddresses(addresses) {
  const promises = addresses.map(async (address, index) => {
    const coords = await geocodeAddress(address)
    return { index, coords, address }
  })

  return Promise.all(promises)
}

/**
 * Coordonnées par défaut pour les grandes villes du Québec
 */
export const DEFAULT_COORDINATES = {
  montreal: { lat: 45.5017, lng: -73.5673 },
  quebec: { lat: 46.8139, lng: -71.2082 },
  laval: { lat: 45.6066, lng: -73.7124 },
  longueuil: { lat: 45.5312, lng: -73.5183 },
  sherbrooke: { lat: 45.4042, lng: -71.8929 },
  gatineau: { lat: 45.4765, lng: -75.7013 }
}

/**
 * Obtenir des coordonnées approximatives basées sur la ville
 * @param {string} city - Nom de la ville
 * @returns {Object|null} - Coordonnées approximatives
 */
export function getApproximateCoordinates(city) {
  if (!city) return null
  
  const cityLower = city.toLowerCase()
  
  // Correspondances exactes
  if (DEFAULT_COORDINATES[cityLower]) {
    return DEFAULT_COORDINATES[cityLower]
  }
  
  // Correspondances partielles
  for (const [key, coords] of Object.entries(DEFAULT_COORDINATES)) {
    if (cityLower.includes(key) || key.includes(cityLower)) {
      return coords
    }
  }
  
  // Par défaut, centre du Québec
  return { lat: 46.8139, lng: -71.2082 }
} 