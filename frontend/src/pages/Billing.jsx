import React, { useState, useEffect } from 'react'
import { Receipt, Plus, DollarSign, FileText, Eye, Trash2, Edit, Calendar, Building, Hash } from 'lucide-react'
import { api } from '../services/api'
import InvoiceForm from '../components/InvoiceForm'

export default function Billing() {
  const [invoices, setInvoices] = useState([])
  const [buildings, setBuildings] = useState([])
  const [loading, setLoading] = useState(true)
  const [showInvoiceForm, setShowInvoiceForm] = useState(false)
  const [selectedBuilding, setSelectedBuilding] = useState('')
  const [selectedCategory, setSelectedCategory] = useState('')
  const [constants, setConstants] = useState({
    categories: {},
    paymentTypes: {},
    invoiceTypes: {}
  })

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    try {
      setLoading(true)
      
      // Charger les factures
      const invoicesResponse = await api.get('/invoices')
      setInvoices(invoicesResponse.data.data || [])
      
      // Charger les immeubles
      const buildingsResponse = await api.get('/buildings')
      setBuildings(buildingsResponse.data || [])
      
      // Charger les constantes
      const constantsResponse = await api.get('/invoices/constants')
      setConstants(constantsResponse.data)
      
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err)
    } finally {
      setLoading(false)
    }
  }

  const handleCreateInvoice = (newInvoice) => {
    setInvoices(prev => [newInvoice, ...prev])
    setShowInvoiceForm(false)
  }

  const handleDeleteInvoice = async (invoiceId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette facture ?')) {
      try {
        await api.delete(`/invoices/${invoiceId}`)
        setInvoices(prev => prev.filter(inv => inv.id !== invoiceId))
      } catch (err) {
        console.error('Erreur lors de la suppression:', err)
        alert('Erreur lors de la suppression de la facture')
      }
    }
  }

  const filteredInvoices = invoices.filter(invoice => {
    const buildingMatch = !selectedBuilding || invoice.buildingId === parseInt(selectedBuilding)
    const categoryMatch = !selectedCategory || invoice.category === selectedCategory
    return buildingMatch && categoryMatch
  })

  const getBuildingName = (buildingId) => {
    const building = buildings.find(b => b.id === buildingId)
    return building ? building.name : `Immeuble ${buildingId}`
  }

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  // Calculer les statistiques
  const totalAmount = invoices.reduce((sum, inv) => sum + inv.amount, 0)
  const thisMonth = new Date().getMonth()
  const thisYear = new Date().getFullYear()
  const thisMonthInvoices = invoices.filter(inv => {
    const invDate = new Date(inv.date)
    return invDate.getMonth() === thisMonth && invDate.getFullYear() === thisYear
  })
  const thisMonthAmount = thisMonthInvoices.reduce((sum, inv) => sum + inv.amount, 0)

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturation & Dépenses</h1>
          <p className="text-gray-600 mt-1">Gestion financière et facturation</p>
        </div>
        <button 
          onClick={() => setShowInvoiceForm(true)}
          className="btn-primary flex items-center"
        >
          <Plus className="h-5 w-5 mr-2" />
          Nouvelle Facture
        </button>
      </div>

      {/* Statistiques */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <DollarSign className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Total Factures</h3>
          <p className="text-2xl font-bold text-green-600">{formatCurrency(totalAmount)}</p>
        </div>
        <div className="card text-center">
          <Receipt className="h-12 w-12 text-blue-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Nombre de Factures</h3>
          <p className="text-2xl font-bold text-blue-600">{invoices.length}</p>
        </div>
        <div className="card text-center">
          <FileText className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Ce Mois</h3>
          <p className="text-2xl font-bold text-yellow-600">{formatCurrency(thisMonthAmount)}</p>
        </div>
      </div>

      {/* Filtres */}
      <div className="card">
        <div className="flex flex-wrap gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filtrer par immeuble
            </label>
            <select
              value={selectedBuilding}
              onChange={(e) => setSelectedBuilding(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Tous les immeubles</option>
              {buildings.map(building => (
                <option key={building.id} value={building.id}>
                  {building.name}
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Filtrer par catégorie
            </label>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Toutes les catégories</option>
              {Object.entries(constants.categories).map(([key, value]) => (
                <option key={key} value={key}>{value}</option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Liste des factures */}
      <div className="card">
        <h2 className="text-xl font-semibold mb-4">Factures ({filteredInvoices.length})</h2>
        
        {filteredInvoices.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            Aucune facture trouvée
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Numéro
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Catégorie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Immeuble
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Unité
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Montant
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Date
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Actions
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {filteredInvoices.map((invoice) => (
                  <tr key={invoice.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Hash className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm font-medium text-gray-900">
                          {invoice.invoiceNumber}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {constants.categories[invoice.category] || invoice.category}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Building className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {getBuildingName(invoice.buildingId)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {invoice.unitId || 'Tout l\'immeuble'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {formatCurrency(invoice.amount)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <Calendar className="h-4 w-4 text-gray-400 mr-2" />
                        <span className="text-sm text-gray-900">
                          {formatDate(invoice.date)}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                      <div className="flex space-x-2">
                        {invoice.pdfFilename && (
                          <button
                            onClick={() => window.open(`/api/documents/${invoice.pdfFilename}`, '_blank')}
                            className="text-blue-600 hover:text-blue-900"
                            title="Voir le PDF"
                          >
                            <Eye className="h-4 w-4" />
                          </button>
                        )}
                        <button
                          onClick={() => handleDeleteInvoice(invoice.id)}
                          className="text-red-600 hover:text-red-900"
                          title="Supprimer"
                        >
                          <Trash2 className="h-4 w-4" />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Modal de création de facture */}
      {showInvoiceForm && (
        <InvoiceForm
          onClose={() => setShowInvoiceForm(false)}
          onSuccess={handleCreateInvoice}
        />
      )}
    </div>
  )
} 