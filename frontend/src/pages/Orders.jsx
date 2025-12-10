import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter, DollarSign, Calendar, FileText, Edit, Trash2, Building, Package, Tag, Download } from 'lucide-react'
import OrderForm from '../components/OrderForm'
import { ordersService, projectsService, suppliersService } from '../services/api'

export default function Orders() {
  const [orders, setOrders] = useState([])
  const [filteredOrders, setFilteredOrders] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingOrder, setEditingOrder] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterProject, setFilterProject] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [projects, setProjects] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterOrders()
  }, [orders, searchTerm, filterProject, filterStatus])

  const loadData = async () => {
    try {
      setLoading(true)
      const [ordersRes, projectsRes, suppliersRes] = await Promise.all([
        ordersService.getOrders(),
        projectsService.getProjects(),
        suppliersService.getSuppliers()
      ])
      setOrders(ordersRes.data || [])
      setProjects(projectsRes.data || [])
      setSuppliers(suppliersRes.data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterOrders = () => {
    let filtered = orders

    if (searchTerm) {
      filtered = filtered.filter(order =>
        getProjectName(order.id_projet)?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        getSupplierName(order.id_fournisseur)?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        order.notes?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (filterProject) {
      filtered = filtered.filter(order => order.id_projet === parseInt(filterProject))
    }

    if (filterStatus) {
      filtered = filtered.filter(order => order.statut === filterStatus)
    }

    // Trier par date de création décroissante
    filtered = filtered.sort((a, b) => {
      const dateA = new Date(a.date_creation || 0)
      const dateB = new Date(b.date_creation || 0)
      return dateB - dateA
    })

    setFilteredOrders(filtered)
  }

  const handleCreateOrder = () => {
    setEditingOrder(null)
    setShowForm(true)
  }

  const handleEditOrder = (order) => {
    setEditingOrder(order)
    setShowForm(true)
  }

  const handleDeleteOrder = async (orderId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette commande ?')) {
      try {
        await ordersService.deleteOrder(orderId)
        loadData()
      } catch (error) {
        console.error('Erreur lors de la suppression:', error)
      }
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingOrder(null)
  }

  const handleFormSuccess = () => {
    setShowForm(false)
    setEditingOrder(null)
    loadData()
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifié'
    try {
      const [year, month, day] = dateString.split('T')[0].split('-')
      const localDate = new Date(year, month - 1, day)
      return localDate.toLocaleDateString('fr-CA')
    } catch {
      return 'Date invalide'
    }
  }

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  const getProjectName = (projectId) => {
    const project = projects.find(p => p.id_projet === projectId)
    return project ? project.nom : `Projet ${projectId}`
  }

  const getSupplierName = (supplierId) => {
    const supplier = suppliers.find(s => s.id_fournisseur === supplierId)
    return supplier ? supplier.nom : `Fournisseur ${supplierId}`
  }

  const getStatusLabel = (status) => {
    const labels = {
      'en_attente': 'En attente',
      'confirmee': 'Confirmée',
      'livree': 'Livrée',
      'facturee': 'Facturée'
    }
    return labels[status] || status
  }

  const getStatusColor = (status) => {
    const colors = {
      'en_attente': 'bg-yellow-100 text-yellow-800',
      'confirmee': 'bg-blue-100 text-blue-800',
      'livree': 'bg-green-100 text-green-800',
      'facturee': 'bg-gray-100 text-gray-800'
    }
    return colors[status] || 'bg-gray-100 text-gray-800'
  }

  const totalAmount = orders.reduce((sum, order) => sum + (order.montant || 0), 0)

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Commandes</h1>
        <button
          onClick={handleCreateOrder}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Nouvelle commande</span>
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Commandes</p>
              <p className="text-2xl font-bold text-blue-600">{formatAmount(totalAmount)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Commandes</p>
              <p className="text-2xl font-bold text-green-600">{orders.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <Filter className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Filtrées</p>
              <p className="text-2xl font-bold text-orange-600">{filteredOrders.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recherche</label>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Projet, fournisseur, notes..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Projet</label>
            <select
              value={filterProject}
              onChange={(e) => setFilterProject(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les projets</option>
              {projects.map(project => (
                <option key={project.id_projet} value={project.id_projet}>{project.nom}</option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Statut</label>
            <select
              value={filterStatus}
              onChange={(e) => setFilterStatus(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les statuts</option>
              <option value="en_attente">En attente</option>
              <option value="confirmee">Confirmée</option>
              <option value="livree">Livrée</option>
              <option value="facturee">Facturée</option>
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setFilterProject('')
                setFilterStatus('')
              }}
              className="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Effacer les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Liste des commandes */}
      {filteredOrders.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune commande</h3>
          <p className="text-gray-500 mb-4">
            {orders.length === 0 
              ? "Commencez par créer votre première commande"
              : "Aucune commande ne correspond à vos filtres"
            }
          </p>
          {orders.length === 0 && (
            <button
              onClick={handleCreateOrder}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Créer une commande
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredOrders.map((order) => (
            <div key={order.id_commande} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      Commande #{order.id_commande}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(order.statut)}`}>
                      {getStatusLabel(order.statut)}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                    <div>
                      <span className="font-medium">Projet:</span>
                      <span className="ml-1">{getProjectName(order.id_projet)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Fournisseur:</span>
                      <span className="ml-1">{getSupplierName(order.id_fournisseur)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Montant total:</span>
                      <span className="ml-1 font-semibold text-green-600">
                        {formatAmount(
                          order.lignes_commande && order.lignes_commande.length > 0
                            ? order.lignes_commande.reduce((sum, ligne) => sum + (parseFloat(ligne.montant) || 0), 0)
                            : (order.montant || 0)
                        )}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Type paiement:</span>
                      <span className="ml-1">{order.type_de_paiement || 'Non spécifié'}</span>
                    </div>
                  </div>
                  
                  {order.lignes_commande && order.lignes_commande.length > 0 && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
                      <p className="text-sm font-medium text-gray-700 mb-2">
                        Lignes de commande ({order.lignes_commande.length}):
                      </p>
                      <div className="space-y-1">
                        {order.lignes_commande.map((ligne, idx) => (
                          <div key={idx} className="text-xs text-gray-600">
                            • {ligne.matiere_premiere?.nom || `Matière ${ligne.id_matiere_premiere}`} - 
                            {ligne.quantite} {ligne.unite} - 
                            {formatAmount(ligne.montant)}
                            {ligne.section && ` (${ligne.section})`}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  
                  {order.notes && (
                    <div className="mt-2 text-sm text-gray-500">
                      <span className="font-medium">Notes:</span>
                      <span className="ml-1">{order.notes}</span>
                    </div>
                  )}
                  
                  {order.pdf_commande && (
                    <div className="mt-2">
                      <a
                        href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${order.pdf_commande}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-800"
                      >
                        <Download className="h-4 w-4 mr-1" />
                        Télécharger le PDF
                      </a>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleEditOrder(order)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteOrder(order.id_commande)}
                    className="p-2 text-gray-400 hover:text-red-600 transition-colors"
                    title="Supprimer"
                  >
                    <Trash2 className="h-4 w-4" />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Formulaire modal */}
      <OrderForm
        isOpen={showForm}
        onClose={handleCloseForm}
        order={editingOrder}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
}

