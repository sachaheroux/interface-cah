import React, { useState, useEffect } from 'react'
import { 
  X, 
  Edit, 
  Trash2, 
  User, 
  Mail, 
  Phone, 
  Home, 
  MapPin, 
  DollarSign, 
  UserCheck,
  FileText,
  Calendar,
  AlertTriangle
} from 'lucide-react'
import { getTenantStatusLabel, getTenantStatusColor } from '../types/tenant'
import { unitsService, assignmentsService } from '../services/api'

export default function TenantDetails({ tenant, isOpen, onClose, onEdit, onDelete }) {
  const [tenantUnit, setTenantUnit] = useState(null)
  const [loadingUnit, setLoadingUnit] = useState(false)

  // Charger les informations de l'unité du locataire
  useEffect(() => {
    if (isOpen && tenant?.id) {
      loadTenantUnit()
    }
  }, [isOpen, tenant])

  const loadTenantUnit = async () => {
    try {
      setLoadingUnit(true)
      // Récupérer les assignations depuis le backend
      const assignmentsResponse = await assignmentsService.getAssignments()
      const allAssignments = assignmentsResponse.data || []
      
      // Trouver l'assignation active pour ce locataire
      // Une assignation est active si la date d'aujourd'hui est entre la date de début et de fin
      const today = new Date()
      const activeAssignment = allAssignments.find(a => {
        if (parseInt(a.tenantId) !== parseInt(tenant.id_locataire)) return false
        
        const startDate = a.leaseStartDate ? new Date(a.leaseStartDate) : null
        const endDate = a.leaseEndDate ? new Date(a.leaseEndDate) : null
        
        // Si pas de dates, considérer comme inactive
        if (!startDate || !endDate) return false
        
        // Vérifier si aujourd'hui est entre startDate et endDate
        const isActive = today >= startDate && today <= endDate
        
        console.log('🔍 Vérification assignation active:', {
          id: a.id,
          startDate: startDate,
          endDate: endDate,
          today: today,
          isActive: isActive
        })
        
        return isActive
      })
      
      console.log('🔍 DEBUG - TenantDetails loadTenantUnit:', {
        tenantId: tenant.id_locataire,
        allAssignments: allAssignments.map(a => ({ id: a.id, tenantId: a.tenantId, unitId: a.unitId })),
        activeAssignment: activeAssignment
      })
      
      if (activeAssignment) {
        // Récupérer les détails de l'unité
        const unitsResponse = await unitsService.getUnits()
        const allUnits = unitsResponse.data || []
        const unit = allUnits.find(u => parseInt(u.id) === parseInt(activeAssignment.unitId))
        
        if (unit) {
          setTenantUnit({
            ...unit,
            assignment: activeAssignment,
            rental: {
              monthlyRent: activeAssignment.rentAmount || 0,
              startDate: activeAssignment.leaseStartDate,
              endDate: activeAssignment.leaseEndDate
            }
          })
        } else {
          setTenantUnit(null)
        }
      } else {
        setTenantUnit(null)
      }
    } catch (error) {
      console.error('Error loading tenant unit:', error)
      setTenantUnit(null)
    } finally {
      setLoadingUnit(false)
    }
  }

  if (!isOpen || !tenant) return null

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifiée'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  const formatAddress = (address) => {
    if (!address || !address.street) return 'Non spécifiée'
    const parts = [
      address.street,
      address.city,
      address.province,
      address.postalCode
    ].filter(Boolean)
    return parts.join(', ')
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        {/* En-tête */}
        <div className="flex items-center justify-between p-6 border-b">
          <div className="flex items-center">
            <div className="p-3 bg-green-100 rounded-lg mr-4">
              <User className="h-8 w-8 text-green-600" />
            </div>
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{tenant.nom} {tenant.prenom}</h2>
              <span className={`inline-flex px-3 py-1 text-sm font-medium rounded-full ${getTenantStatusColor(tenant.statut)}`}>
                {getTenantStatusLabel(tenant.statut)}
              </span>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <div className="p-6 space-y-8">
          {/* Statistiques rapides */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center">
                <Calendar className="h-8 w-8 text-blue-600 mr-3" />
                <div>
                  <p className="text-sm text-blue-600">Locataire depuis</p>
                  <p className="text-lg font-semibold text-blue-900">
                    {tenant.createdAt ? new Date(tenant.createdAt).toLocaleDateString('fr-CA') : 'N/A'}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <div className="flex items-center">
                <Home className="h-8 w-8 text-green-600 mr-3" />
                <div>
                  <p className="text-sm text-green-600">Unité assignée</p>
                  <div className="flex items-center">
                    <Home className="h-4 w-4 text-gray-400 mr-2" />
                    <span className="text-sm text-gray-600">
                      {tenantUnit ? (tenantUnit.unitAddress || tenantUnit.simpleTitle || 'Unité assignée') : 'Aucune unité'}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <div className="flex items-center">
                <DollarSign className="h-8 w-8 text-purple-600 mr-3" />
                <div>
                  <p className="text-sm text-purple-600">Revenu mensuel</p>
                  <p className="text-lg font-semibold text-purple-900">
                    {tenant.financial?.monthlyIncome ? `${tenant.financial.monthlyIncome.toLocaleString('fr-CA')} $` : 'N/A'}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Informations de contact */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <User className="h-5 w-5 mr-2" />
              Informations de Contact
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {tenant.email && (
                  <div className="flex items-center">
                    <Mail className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="text-gray-900">{tenant.email}</p>
                    </div>
                  </div>
                )}
                
                {tenant.telephone && (
                  <div className="flex items-center">
                    <Phone className="h-5 w-5 text-gray-400 mr-3" />
                    <div>
                      <p className="text-sm text-gray-500">Téléphone</p>
                      <p className="text-gray-900">{tenant.telephone}</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Informations de l'unité */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center">
              <Home className="h-5 w-5 mr-2" />
              Unité de Résidence
            </h3>
            <div className="bg-gray-50 rounded-lg p-4">
              {loadingUnit ? (
                <div className="flex items-center justify-center py-4">
                  <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600"></div>
                  <span className="ml-2 text-gray-600">Chargement des informations de l'unité...</span>
                </div>
              ) : tenantUnit ? (
                <div className="space-y-3">
                  <div className="flex items-start">
                    <MapPin className="h-5 w-5 text-gray-400 mr-3 mt-0.5" />
                    <div>
                      <p className="text-sm text-gray-500">Adresse complète</p>
                      <p className="text-gray-900">{tenantUnit.unitAddress || tenantUnit.simpleTitle || 'Adresse non disponible'}</p>
                    </div>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
                    <div>
                      <p className="text-sm text-gray-500">Type d'unité</p>
                      <p className="text-gray-900">{tenantUnit.type || 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Superficie</p>
                      <p className="text-gray-900">{tenantUnit.area ? `${tenantUnit.area} pi²` : 'N/A'}</p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500">Loyer mensuel</p>
                      <p className="text-gray-900">
                        {tenantUnit.rental?.monthlyRent ? `${tenantUnit.rental.monthlyRent} $` : 'N/A'}
                      </p>
                    </div>
                  </div>
                </div>
              ) : (
                <div className="flex items-center justify-center py-8 text-gray-500">
                  <AlertTriangle className="h-8 w-8 mr-3" />
                  <div>
                    <p className="font-medium">Aucune unité assignée</p>
                    <p className="text-sm">Ce locataire n'est pas encore assigné à une unité.</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Contact d'urgence */}
          {tenant.emergencyContact && (tenant.emergencyContact.name || tenant.emergencyContact.phone) && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <Phone className="h-5 w-5 mr-2" />
                Contact d'Urgence
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {tenant.emergencyContact.name && (
                    <div>
                      <p className="text-sm text-gray-500">Nom</p>
                      <p className="text-gray-900">{tenant.emergencyContact.name}</p>
                    </div>
                  )}
                  
                  {tenant.emergencyContact.relationship && (
                    <div>
                      <p className="text-sm text-gray-500">Relation</p>
                      <p className="text-gray-900">{tenant.emergencyContact.relationship || 'Non spécifié'}</p>
                    </div>
                  )}
                  
                  {tenant.emergencyContact.phone && (
                    <div>
                      <p className="text-sm text-gray-500">Téléphone</p>
                      <p className="text-gray-900">{tenant.emergencyContact.phone}</p>
                    </div>
                  )}
                  
                  {tenant.emergencyContact.email && (
                    <div>
                      <p className="text-sm text-gray-500">Email</p>
                      <p className="text-gray-900">{tenant.emergencyContact.email}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Informations financières */}
          {tenant.financial && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <DollarSign className="h-5 w-5 mr-2" />
                Informations Financières
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {tenant.financial.monthlyIncome > 0 && (
                    <div>
                      <p className="text-sm text-gray-500">Revenu mensuel</p>
                      <p className="text-gray-900">{tenant.financial.monthlyIncome.toLocaleString('fr-CA')} $</p>
                    </div>
                  )}
                  
                  {tenant.financial.creditScore > 0 && (
                    <div>
                      <p className="text-sm text-gray-500">Cote de crédit</p>
                      <p className="text-gray-900">{tenant.financial.creditScore}</p>
                    </div>
                  )}
                  
                  {tenant.financial.employer && (
                    <div>
                      <p className="text-sm text-gray-500">Employeur</p>
                      <p className="text-gray-900">{tenant.financial.employer}</p>
                    </div>
                  )}
                  
                  {tenant.financial.employerPhone && (
                    <div>
                      <p className="text-sm text-gray-500">Téléphone employeur</p>
                      <p className="text-gray-900">{tenant.financial.employerPhone}</p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* Notes */}
          {tenant.notes && (
            <div className="space-y-4">
              <h3 className="text-lg font-semibold text-gray-900 flex items-center">
                <FileText className="h-5 w-5 mr-2" />
                Notes
              </h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-gray-900 whitespace-pre-wrap">{tenant.notes}</p>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="flex justify-end space-x-3 p-6 border-t bg-gray-50">
          <button
            onClick={onClose}
            className="px-4 py-2 text-gray-700 bg-white border border-gray-300 hover:bg-gray-50 rounded-lg transition-colors"
          >
            Fermer
          </button>
          <button
            onClick={() => onEdit(tenant)}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center"
          >
            <Edit className="h-4 w-4 mr-2" />
            Modifier
          </button>
          <button
            onClick={() => onDelete(tenant)}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 text-white rounded-lg transition-colors flex items-center"
          >
            <Trash2 className="h-4 w-4 mr-2" />
            Supprimer
          </button>
        </div>
      </div>
    </div>
  )
} 