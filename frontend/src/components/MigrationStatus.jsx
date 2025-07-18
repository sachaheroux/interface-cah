import React, { useState, useEffect } from 'react'
import { CheckCircle, AlertTriangle, RefreshCw, X } from 'lucide-react'
import { assignmentsService } from '../services/api'

export default function MigrationStatus() {
  const [migrationStatus, setMigrationStatus] = useState(null)
  const [isVisible, setIsVisible] = useState(false)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    checkMigrationStatus()
  }, [])

  const checkMigrationStatus = () => {
    // Vérifier s'il y a des assignations en localStorage
    const localAssignments = JSON.parse(localStorage.getItem('unitTenantAssignments') || '[]')
    const hasMigrated = assignmentsService.hasMigrated()
    
    if (localAssignments.length > 0 && !hasMigrated) {
      // Il y a des assignations à migrer
      setMigrationStatus({
        type: 'pending',
        message: `${localAssignments.length} assignation(s) en attente de migration`,
        count: localAssignments.length
      })
      setIsVisible(true)
    } else if (hasMigrated) {
      // Migration déjà effectuée
      setMigrationStatus({
        type: 'completed',
        message: 'Migration des assignations terminée',
        count: 0
      })
      
      // Masquer automatiquement après 3 secondes
      setTimeout(() => setIsVisible(false), 3000)
    }
  }

  const handleMigrate = async () => {
    setIsLoading(true)
    try {
      const result = await assignmentsService.migrateLocalStorageToBackend()
      
      if (result.success) {
        setMigrationStatus({
          type: 'completed',
          message: `Migration réussie: ${result.migrated} assignation(s) transférée(s)`,
          count: result.migrated
        })
        
        // Masquer après 5 secondes
        setTimeout(() => setIsVisible(false), 5000)
      } else {
        setMigrationStatus({
          type: 'error',
          message: `Migration partielle: ${result.migrated} réussies, ${result.errors} erreurs`,
          count: result.total
        })
      }
    } catch (error) {
      setMigrationStatus({
        type: 'error',
        message: 'Erreur lors de la migration',
        count: 0
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleDismiss = () => {
    setIsVisible(false)
  }

  if (!isVisible || !migrationStatus) {
    return null
  }

  const getStatusIcon = () => {
    switch (migrationStatus.type) {
      case 'pending':
        return <RefreshCw className="h-5 w-5 text-blue-600" />
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case 'error':
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      default:
        return <RefreshCw className="h-5 w-5 text-gray-600" />
    }
  }

  const getStatusColor = () => {
    switch (migrationStatus.type) {
      case 'pending':
        return 'bg-blue-50 border-blue-200 text-blue-800'
      case 'completed':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'error':
        return 'bg-red-50 border-red-200 text-red-800'
      default:
        return 'bg-gray-50 border-gray-200 text-gray-800'
    }
  }

  return (
    <div className={`fixed top-20 sm:top-16 right-4 z-40 max-w-md rounded-lg border p-4 shadow-lg ${getStatusColor()}`}>
      <div className="flex items-start justify-between">
        <div className="flex items-start space-x-3">
          {getStatusIcon()}
          <div className="flex-1">
            <h4 className="font-medium">Migration des Assignations</h4>
            <p className="text-sm mt-1">{migrationStatus.message}</p>
            
            {migrationStatus.type === 'pending' && (
              <div className="mt-3 flex space-x-2">
                <button
                  onClick={handleMigrate}
                  disabled={isLoading}
                  className="text-sm bg-blue-600 text-white px-3 py-1 rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw className="h-3 w-3 mr-1 animate-spin" />
                      Migration...
                    </>
                  ) : (
                    'Migrer maintenant'
                  )}
                </button>
                <button
                  onClick={handleDismiss}
                  className="text-sm text-blue-600 hover:text-blue-800"
                >
                  Plus tard
                </button>
              </div>
            )}
          </div>
        </div>
        
        <button
          onClick={handleDismiss}
          className="text-gray-400 hover:text-gray-600 ml-2"
        >
          <X className="h-4 w-4" />
        </button>
      </div>
    </div>
  )
} 