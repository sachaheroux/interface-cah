import React, { useState, useEffect } from 'react'
import { Plus, Search, Filter, DollarSign, Calendar, FileText, Edit, Trash2, Eye, Building, User } from 'lucide-react'
import InvoiceSTForm from '../components/InvoiceSTForm'
import { invoicesSTService, projectsService, contractorsService } from '../services/api'

export default function InvoicesST() {
  const [invoices, setInvoices] = useState([])
  const [filteredInvoices, setFilteredInvoices] = useState([])
  const [showForm, setShowForm] = useState(false)
  const [editingInvoice, setEditingInvoice] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterProject, setFilterProject] = useState('')
  const [projects, setProjects] = useState([])
  const [contractors, setContractors] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadData()
  }, [])

  useEffect(() => {
    filterInvoices()
  }, [invoices, searchTerm, filterProject])

  const loadData = async () => {
    try {
      setLoading(true)
      const [invoicesRes, projectsRes, contractorsRes] = await Promise.all([
        invoicesSTService.getInvoices(),
        projectsService.getProjects(),
        contractorsService.getContractors()
      ])
      setInvoices(invoicesRes.data || [])
      setProjects(projectsRes.data || [])
      setContractors(contractorsRes.data || [])
    } catch (error) {
      console.error('Erreur lors du chargement des données:', error)
    } finally {
      setLoading(false)
    }
  }

  const filterInvoices = () => {
    let filtered = invoices

    if (searchTerm) {
      filtered = filtered.filter(invoice =>
        invoice.reference?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        getProjectName(invoice.id_projet)?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        getContractorName(invoice.id_st)?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (filterProject) {
      filtered = filtered.filter(invoice => invoice.id_projet === parseInt(filterProject))
    }

    // Trier par date de création décroissante
    filtered = filtered.sort((a, b) => {
      const dateA = new Date(a.date_creation || 0)
      const dateB = new Date(b.date_creation || 0)
      return dateB - dateA
    })

    setFilteredInvoices(filtered)
  }

  const handleCreateInvoice = () => {
    setEditingInvoice(null)
    setShowForm(true)
  }

  const handleEditInvoice = (invoice) => {
    setEditingInvoice(invoice)
    setShowForm(true)
  }

  const handleDeleteInvoice = async (invoiceId) => {
    if (window.confirm('Êtes-vous sûr de vouloir supprimer cette facture ?')) {
      try {
        await invoicesSTService.deleteInvoice(invoiceId)
        loadData()
      } catch (error) {
        console.error('Erreur lors de la suppression:', error)
      }
    }
  }

  const handleCloseForm = () => {
    setShowForm(false)
    setEditingInvoice(null)
  }

  const handleFormSuccess = () => {
    setShowForm(false)
    setEditingInvoice(null)
    loadData()
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'Non spécifié'
    const [year, month, day] = dateString.split('T')[0].split('-')
    const localDate = new Date(year, month - 1, day)
    return localDate.toLocaleDateString('fr-CA')
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

  const getContractorName = (contractorId) => {
    const contractor = contractors.find(c => c.id_st === contractorId)
    return contractor ? contractor.nom : `Sous-traitant ${contractorId}`
  }

  const totalAmount = invoices.reduce((sum, inv) => sum + (inv.montant || 0), 0)

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
        <h1 className="text-2xl font-bold text-gray-900">Factures Sous-traitants</h1>
        <button
          onClick={handleCreateInvoice}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
        >
          <Plus className="h-4 w-4" />
          <span>Nouvelle facture</span>
        </button>
      </div>

      {/* KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <DollarSign className="h-8 w-8 text-blue-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Factures</p>
              <p className="text-2xl font-bold text-blue-600">{formatAmount(totalAmount)}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <FileText className="h-8 w-8 text-green-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Total Factures</p>
              <p className="text-2xl font-bold text-green-600">{invoices.length}</p>
            </div>
          </div>
        </div>
        
        <div className="bg-white p-4 rounded-lg shadow">
          <div className="flex items-center">
            <Filter className="h-8 w-8 text-orange-600" />
            <div className="ml-3">
              <p className="text-sm font-medium text-gray-500">Filtrées</p>
              <p className="text-2xl font-bold text-orange-600">{filteredInvoices.length}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Filtres */}
      <div className="bg-white p-4 rounded-lg shadow mb-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Recherche</label>
            <div className="relative">
              <Search className="h-4 w-4 absolute left-3 top-3 text-gray-400" />
              <input
                type="text"
                placeholder="Référence, projet, sous-traitant..."
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
          
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('')
                setFilterProject('')
              }}
              className="w-full px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Effacer les filtres
            </button>
          </div>
        </div>
      </div>

      {/* Liste des factures */}
      {filteredInvoices.length === 0 ? (
        <div className="text-center py-12">
          <FileText className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Aucune facture</h3>
          <p className="text-gray-500 mb-4">
            {invoices.length === 0 
              ? "Commencez par créer votre première facture"
              : "Aucune facture ne correspond à vos filtres"
            }
          </p>
          {invoices.length === 0 && (
            <button
              onClick={handleCreateInvoice}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700"
            >
              Créer une facture
            </button>
          )}
        </div>
      ) : (
        <div className="grid gap-4">
          {filteredInvoices.map((invoice) => (
            <div key={invoice.id_facture} className="bg-white rounded-lg shadow p-6">
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="flex items-center space-x-3 mb-2">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {invoice.reference || `Facture #${invoice.id_facture}`}
                    </h3>
                    <span className="px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      Facture ST
                    </span>
                  </div>
                  
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-gray-600 mb-2">
                    <div>
                      <span className="font-medium">Projet:</span>
                      <span className="ml-1">{getProjectName(invoice.id_projet)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Sous-traitant:</span>
                      <span className="ml-1">{getContractorName(invoice.id_st)}</span>
                    </div>
                    <div>
                      <span className="font-medium">Montant:</span>
                      <span className="ml-1 font-semibold text-green-600">
                        {formatAmount(invoice.montant)}
                      </span>
                    </div>
                    <div>
                      <span className="font-medium">Date paiement:</span>
                      <span className="ml-1">{formatDate(invoice.date_de_paiement)}</span>
                    </div>
                  </div>
                  
                  {invoice.section && (
                    <div className="mt-2 text-sm text-gray-500">
                      <span className="font-medium">Section:</span>
                      <span className="ml-1">{invoice.section}</span>
                    </div>
                  )}
                  
                  {invoice.notes && (
                    <div className="mt-2 text-sm text-gray-500">
                      <span className="font-medium">Notes:</span>
                      <span className="ml-1">{invoice.notes}</span>
                    </div>
                  )}
                  
                  {invoice.pdf_facture && (
                    <div className="mt-3 p-3 bg-gray-50 rounded-lg border">
                      <div className="flex items-center space-x-2">
                        <FileText className="h-4 w-4 text-blue-600" />
                        <span className="text-sm font-medium text-gray-700">Document PDF:</span>
                        <a
                          href={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/documents/${invoice.pdf_facture}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-800 text-sm underline"
                        >
                          {invoice.pdf_facture}
                        </a>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center space-x-2 ml-4">
                  <button
                    onClick={() => handleEditInvoice(invoice)}
                    className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                    title="Modifier"
                  >
                    <Edit className="h-4 w-4" />
                  </button>
                  <button
                    onClick={() => handleDeleteInvoice(invoice.id_facture)}
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
      <InvoiceSTForm
        isOpen={showForm}
        onClose={handleCloseForm}
        invoice={editingInvoice}
        onSuccess={handleFormSuccess}
      />
    </div>
  )
}

