import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter, DollarSign, Calendar, FileText, Edit, Trash2, Eye } from 'lucide-react'
import TransactionForm from '../components/TransactionForm'
import api from '../services/api'

export default function Transactions() {
  const [transactions, setTransactions] = useState([])
  const [filteredTransactions, setFilteredTransactions] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingTransaction, setEditingTransaction] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterType, setFilterType] = useState('')
  const [filterStatus, setFilterStatus] = useState('')
  const [buildings, setBuildings] = useState([])
  const [constants, setConstants] = useState({})

  useEffect(() => {
    loadTransactions()
    loadBuildings()
    loadConstants()
  }, [])

  useEffect(() => {
    filterTransactions()
  }, [transactions, searchTerm, filterType, filterStatus])

  const loadTransactions = async () => {
    try {
      const response = await api.get('/api/transactions')
      setTransactions(response.data.data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des transactions:', error)
    }
  }

  const loadBuildings = async () => {
    try {
      const response = await api.get('/api/buildings')
      setBuildings(response.data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des immeubles:', error)
    }
  }

  const loadConstants = async () => {
    try {
      const response = await api.get('/api/transactions/constants')
      setConstants(response.data)
    } catch (error) {
      console.error('Erreur lors du chargement des constantes:', error)
    }
  }

  const filterTransactions = () => {
    let filtered = transactions

    if (searchTerm) {
      filtered = filtered.filter(transaction =>
        transaction.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        transaction.type_transaction?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (filterType) {
      filtered = filtered.filter(transaction => transaction.type_transaction === filterType)
    }

    if (filterStatus) {
      filtered = filtered.filter(transaction => transaction.statut === filterStatus)
    }

    setFilteredTransactions(filtered)
  }

  const handleCreateTransaction = () => {
    setEditingTransaction(null)
    setShowForm(true)
  }

  const handleEditTransaction = (transaction) => {
    setEditingTransaction(transaction)
    setShowForm(true)
  }

  const handleDeleteTransaction = async (transactionId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette transaction ?')) {
      try {
        await api.delete(`/api/transactions/${transactionId}`)
        setTransactions(prev => prev.filter(t => t.id_transaction !== transactionId))
        console.log('✅ Transaction supprimée avec succès')
      } catch (error) {
        console.error('❌ Erreur lors de la suppression:', error)
      }
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingTransaction(null)
  }

  const handleTransactionSaved = (savedTransaction) => {
    if (editingTransaction) {
      setTransactions(prev => prev.map(t => 
        t.id_transaction === savedTransaction.id_transaction ? savedTransaction : t
      ))
    } else {
      setTransactions(prev => [...prev, savedTransaction])
    }
    setShowForm(false)
    setEditingTransaction(null)
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifié'
    return new Date(dateString).toLocaleDateString('fr-CA')
  }

  const formatAmount = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  const getBuildingName = (buildingId) => {
    const building = buildings.find(b => b.id_immeuble === buildingId)
    return building ? building.nom_immeuble : `Immeuble ${buildingId}`
  }

  const getTypeLabel = (type) => {
    const typeLabels = {
      'loyer': 'Loyer',
      'facture': 'Facture',
      'maintenance': 'Maintenance',
      'revenus': 'Revenus',
      'depenses': 'Dépenses',
      'investissement': 'Investissement',
      'frais': 'Frais',
      'autre': 'Autre'
    }
    return typeLabels[type] || type
  }

  const getStatusLabel = (status) => {
    const statusLabels = {
      'en_attente': 'En attente',
      'paye': 'Payé',
      'annule': 'Annulé'
    }
    return statusLabels[status] || status
  }

  const getStatusColor = (status) => {
    const colors = {
      'en_attente': 'text-yellow-600 bg-yellow-100',
      'paye': 'text-green-600 bg-green-100',
      'annule': 'text-red-600 bg-red-100'
    }
    return colors[status] || 'text-gray-600 bg-gray-100'
  }

  const totalAmount = transactions.reduce((sum, t) => sum + (t.montant || 0), 0)
  const thisMonthTransactions = transactions.filter(t => {
    const transactionDate = new Date(t.date_transaction)
    const now = new Date()
    return transactionDate.getMonth() === now.getMonth() && 
           transactionDate.getFullYear() === now.getFullYear()
  })
  const thisMonthAmount = thisMonthTransactions.reduce((sum, t) => sum + (t.montant || 0), 0)

  if (showForm) {
    return (
      <TransactionForm
        transaction={editingTransaction}
        buildings={buildings}
        constants={constants}
        onSave={handleTransactionSaved}
        onCancel={handleCloseForm}
      />
    )
  }

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold text-gray-900">Transactions</h1>
        <button
          onClick={handleCreateTransaction}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Nouvelle transaction</span>
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Portfolio</p>
              <p className="text-2xl font-bold text-blue-600">{formatAmount(totalAmount)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Transactions</p>
              <p className="text-2xl font-bold text-green-600">{transactions.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <Calendar className="h-8 w-8 text-purple-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Ce mois</p>
              <p className="text-2xl font-bold text-purple-600">{formatAmount(thisMonthAmount)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <Filter className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Filtrées</p>
              <p className="text-2xl font-bold text-orange-600">{filteredTransactions.length}</p>
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
                placeholder="Description, référence..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            >
              <option value="">Tous les types</option>
              {constants.types?.map(type => (
                <option key={type} value={type}>{getTypeLabel(type)}</option>
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
              {constants.statuses?.map(status => (
                <option key={status} value={status}>{getStatusLabel(status)}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setFilterType('')
                setFilterStatus('')
              }}
              className="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Effacer les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Liste des transactions */}
      {filteredTransactions.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune transaction</h3>
          <p className="text-gray-500 mb-4">
            {transactions.length === 0 
              ? "Commencez par créer votre première transaction"
              : "Aucune transaction ne correspond à vos filtres"
            }
          </p>
          {transactions.length === 0 && (
            <button
              onClick={handleCreateTransaction}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Créer une transaction
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredTransactions.map((transaction) => (
            <div key={transaction.id_transaction} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {transaction.description || 'Transaction sans description'}
                    </h3>
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(transaction.statut)}`}>
                      {getStatusLabel(transaction.statut)}
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600">
                    <div>
                      <span className="font-medium">Type:</span>
                      <span className="ml-1">{getTypeLabel(transaction.type_transaction)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Montant:</span>
                      <span className="ml-1 font-semibold text-gray-900">{formatAmount(transaction.montant)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Date:</span>
                      <span className="ml-1">{formatDate(transaction.date_transaction)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Immeuble:</span>
                      <span className="ml-1">{getBuildingName(transaction.id_immeuble)}</span>
                    </div>
                  </div>
                  
                  {transaction.reference && (
                    <div className="mt-2 text-sm text-gray-500">
                      <span className="font-medium">Référence:</span>
                      <span className="ml-1">{transaction.reference}</span>
                    </div>
                  )}
                  
                  {transaction.notes && (
                    <div className="mt-2 text-sm text-gray-500">
                      <span className="font-medium">Notes:</span>
                      <span className="ml-1">{transaction.notes}</span>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleEditTransaction(transaction)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteTransaction(transaction.id_transaction)}
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
    </div>
  )
}
