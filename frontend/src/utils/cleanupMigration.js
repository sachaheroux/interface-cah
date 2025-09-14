// Script de nettoyage pour supprimer toutes les données de migration
export const cleanupMigrationData = () => {
  try {
    // Supprimer toutes les données de migration du localStorage
    localStorage.removeItem('unitTenantAssignments')
    localStorage.removeItem('assignationsMigrated')
    localStorage.removeItem('migrationStatus')
    localStorage.removeItem('migrationCompleted')
    
    console.log('🧹 Données de migration nettoyées du localStorage')
    return true
  } catch (error) {
    console.error('❌ Erreur lors du nettoyage des données de migration:', error)
    return false
  }
}

// Nettoyer automatiquement au chargement
if (typeof window !== 'undefined') {
  cleanupMigrationData()
}
