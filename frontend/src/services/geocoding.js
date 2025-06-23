// Service de géocodage pour convertir les adresses en coordonnées
// Utilise l'API Nominatim d'OpenStreetMap (gratuite)

const NOMINATIM_BASE_URL = 'https://nominatim.openstreetmap.org/search'

// Cache pour éviter les requêtes répétées
const geocodeCache = new Map()

/**
 * Géocoder une adresse en coordonnées lat/lng
 * @param {Object|string} address - Adresse à géocoder
 * @returns {Promise<{lat: number, lng: number}|null>}
 */
export async function geocodeAddress(address) {
  try {
    // Construire la chaîne d'adresse
    let addressString
    if (typeof address === 'string') {
      addressString = address
    } else {
      // Construire l'adresse à partir de l'objet
      const parts = []
      if (address.street) parts.push(address.street)
      if (address.city) parts.push(address.city)
      if (address.province) parts.push(address.province)
      if (address.country) parts.push(address.country)
      addressString = parts.join(', ')
    }

    // Vérifier le cache
    if (geocodeCache.has(addressString)) {
      return geocodeCache.get(addressString)
    }

    // Construire l'URL de requête
    const params = new URLSearchParams({
      q: addressString,
      format: 'json',
      limit: '1',
      countrycodes: 'ca', // Limiter au Canada
      addressdetails: '1'
    })

    const response = await fetch(`${NOMINATIM_BASE_URL}?${params}`)
    const data = await response.json()

    if (data && data.length > 0) {
      const result = {
        lat: parseFloat(data[0].lat),
        lng: parseFloat(data[0].lon)
      }
      
      // Mettre en cache
      geocodeCache.set(addressString, result)
      return result
    }

    // Si pas de résultat, mettre null en cache pour éviter de réessayer
    geocodeCache.set(addressString, null)
    return null

  } catch (error) {
    console.error('Erreur géocodage:', error)
    return null
  }
}

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