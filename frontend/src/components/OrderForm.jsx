import React, { useState, useEffect } from 'react'
import { X, Save, Building, Package, DollarSign, FileText, Plus, Trash2, Tag } from 'lucide-react'
import { ordersService, projectsService, suppliersService, materialsService } from '../services/api'

export default function OrderForm({ isOpen, onClose, order, onSuccess }) {
  const [formData, setFormData] = useState({
    id_projet: '',
    id_fournisseur: '',
    statut: 'en_attente',
    type_de_paiement: '',
    notes: ''
  })
  
  const [lignes, setLignes] = useState([
    {
      id_matiere_premiere: '',
      quantite: '',
      unite: '',
      montant: '',
      section: ''
    }
  ])
  
  const [projects, setProjects] = useState([])
  const [suppliers, setSuppliers] = useState([])
  const [materials, setMaterials] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (isOpen) {
      fetchProjects()
      fetchSuppliers()
      fetchMaterials()
      
      if (order) {
        setFormData({
          id_projet: order.id_projet || '',
          id_fournisseur: order.id_fournisseur || '',
          statut: order.statut || 'en_attente',
          type_de_paiement: order.type_de_paiement || '',
          notes: order.notes || ''
        })
        
        if (order.lignes_commande && order.lignes_commande.length > 0) {
          setLignes(order.lignes_commande.map(ligne => ({
            id_ligne: ligne.id_ligne || null, // Garder l'ID pour la modification
            id_matiere_premiere: ligne.id_matiere_premiere || '',
            quantite: ligne.quantite || '',
            unite: ligne.unite || '',
            montant: ligne.montant || '',
            section: ligne.section || ''
          })))
        } else {
          setLignes([{
            id_matiere_premiere: '',
            quantite: '',
            unite: '',
            montant: '',
            section: ''
          }])
        }
      } else {
        setFormData({
          id_projet: '',
          id_fournisseur: '',
          statut: 'en_attente',
          type_de_paiement: '',
          notes: ''
        })
        setLignes([{
          id_matiere_premiere: '',
          quantite: '',
          unite: '',
          montant: '',
          section: ''
        }])
      }
    }
  }, [isOpen, order])

  const fetchProjects = async () => {
    try {
      const response = await projectsService.getProjects()
      setProjects(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des projets:', err)
    }
  }

  const fetchSuppliers = async () => {
    try {
      const response = await suppliersService.getSuppliers()
      setSuppliers(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des fournisseurs:', err)
    }
  }

  const fetchMaterials = async () => {
    try {
      const response = await materialsService.getMaterials()
      setMaterials(response.data || [])
    } catch (err) {
      console.error('Erreur lors du chargement des matières premières:', err)
    }
  }

  const handleChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleLigneChange = (index, field, value) => {
    const newLignes = [...lignes]
    newLignes[index] = {
      ...newLignes[index],
      [field]: value
    }
    
    // Si on change la section de la première ligne, remplir automatiquement les autres (mais modifiable)
    if (index === 0 && field === 'section' && value) {
      for (let i = 1; i < newLignes.length; i++) {
        // Remplir seulement si la section est vide
        if (!newLignes[i].section) {
          newLignes[i].section = value
        }
      }
    }
    
    setLignes(newLignes)
  }

  const addLigne = () => {
    setLignes([...lignes, {
      id_matiere_premiere: '',
      quantite: '',
      unite: '',
      montant: '',
      section: lignes[0]?.section || '' // Remplir avec la section de la première ligne si elle existe
    }])
  }

  const removeLigne = (index) => {
    if (lignes.length > 1) {
      setLignes(lignes.filter((_, i) => i !== index))
    }
  }

  const calculateTotal = () => {
    return lignes.reduce((sum, ligne) => {
      const montant = parseFloat(ligne.montant) || 0
      return sum + montant
    }, 0)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    // Validation
    if (!formData.id_projet) {
      setError('Veuillez sélectionner un projet')
      setLoading(false)
      return
    }
    
    if (!formData.id_fournisseur) {
      setError('Veuillez sélectionner un fournisseur')
      setLoading(false)
      return
    }
    
    if (lignes.length === 0) {
      setError('Veuillez ajouter au moins une ligne de commande')
      setLoading(false)
      return
    }
    
    for (let i = 0; i < lignes.length; i++) {
      const ligne = lignes[i]
      if (!ligne.id_matiere_premiere || !ligne.quantite || !ligne.unite || !ligne.montant) {
        setError(`Veuillez remplir tous les champs de la ligne ${i + 1}`)
        setLoading(false)
        return
      }
    }

    try {
      const submitData = {
        id_projet: parseInt(formData.id_projet),
        id_fournisseur: parseInt(formData.id_fournisseur),
        statut: formData.statut,
        type_de_paiement: formData.type_de_paiement || null,
        notes: formData.notes || null,
        lignes_commande: lignes.map(ligne => ({
          id_matiere_premiere: parseInt(ligne.id_matiere_premiere),
          quantite: parseFloat(ligne.quantite),
          unite: ligne.unite,
          montant: parseFloat(ligne.montant),
          section: ligne.section || null
        }))
      }

      if (order) {
        // Pour la modification, on doit mettre à jour la commande et gérer les lignes
        // D'abord, supprimer toutes les lignes existantes
        const existingLines = order.lignes_commande || []
        for (const existingLine of existingLines) {
          if (existingLine.id_ligne || existingLine.id_ligne_commande) {
            const lineId = existingLine.id_ligne || existingLine.id_ligne_commande
            await ordersService.deleteOrderLine(lineId)
          }
        }
        
        // Mettre à jour la commande
        await ordersService.updateOrder(order.id_commande, {
          id_projet: submitData.id_projet,
          id_fournisseur: submitData.id_fournisseur,
          statut: submitData.statut,
          type_de_paiement: submitData.type_de_paiement,
          notes: submitData.notes,
          montant: calculateTotal()
        })
        
        // Créer les nouvelles lignes
        for (const ligne of submitData.lignes_commande) {
          await ordersService.createOrderLine({
            id_commande: order.id_commande,
            id_matiere_premiere: ligne.id_matiere_premiere,
            quantite: ligne.quantite,
            unite: ligne.unite,
            montant: ligne.montant,
            section: ligne.section
          })
        }
        
        onSuccess()
      } else {
        await ordersService.createOrder(submitData)
        onSuccess()
      }
      onClose()
    } catch (error) {
      console.error('Erreur lors de la sauvegarde:', error)
      setError(error.response?.data?.detail || 'Erreur lors de la sauvegarde')
    } finally {
      setLoading(false)
    }
  }

  if (!isOpen) return null

  const total = calculateTotal()
  const sections = [
    'Admin',
    'Excavation et fondation',
    'Structure du batiment',
    'Toiture',
    'Préparation intérieur',
    'Fenêtres',
    'Gypse',
    'Joint',
    'Portes',
    'Peinture',
    'Plancher',
    'Armoire',
    'Revêtement souple',
    'Patio arrière',
    'Autres'
  ]

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl w-full max-w-5xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900">
            {order ? 'Modifier la commande' : 'Nouvelle commande'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Formulaire */}
        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Informations de la commande */}
          <div className="space-y-4">
            <h3 className="text-lg font-semibold text-gray-900">Informations de la commande</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Building className="h-4 w-4 inline mr-1" />
                  Projet *
                </label>
                <select
                  value={formData.id_projet}
                  onChange={(e) => handleChange('id_projet', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Sélectionner un projet</option>
                  {projects.map((project) => (
                    <option key={project.id_projet} value={project.id_projet}>
                      {project.nom}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  <Package className="h-4 w-4 inline mr-1" />
                  Fournisseur *
                </label>
                <select
                  value={formData.id_fournisseur}
                  onChange={(e) => handleChange('id_fournisseur', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="">Sélectionner un fournisseur</option>
                  {suppliers.map((supplier) => (
                    <option key={supplier.id_fournisseur} value={supplier.id_fournisseur}>
                      {supplier.nom}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Statut *
                </label>
                <select
                  value={formData.statut}
                  onChange={(e) => handleChange('statut', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                >
                  <option value="en_attente">En attente</option>
                  <option value="confirmee">Confirmée</option>
                  <option value="livree">Livrée</option>
                  <option value="facturee">Facturée</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Type de paiement
                </label>
                <select
                  value={formData.type_de_paiement}
                  onChange={(e) => handleChange('type_de_paiement', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="">Sélectionner un type</option>
                  <option value="comptant">Comptant</option>
                  <option value="credit">Crédit</option>
                  <option value="cheque">Chèque</option>
                </select>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                <FileText className="h-4 w-4 inline mr-1" />
                Notes
              </label>
              <textarea
                value={formData.notes}
                onChange={(e) => handleChange('notes', e.target.value)}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                placeholder="Notes sur la commande..."
              />
            </div>
          </div>

          {/* Lignes de commande */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-semibold text-gray-900">Lignes de commande</h3>
            </div>
            
            {lignes.map((ligne, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4 space-y-4">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium text-gray-700">Ligne {index + 1}</span>
                  {lignes.length > 1 && (
                    <button
                      type="button"
                      onClick={() => removeLigne(index)}
                      className="text-red-600 hover:text-red-800"
                    >
                      <Trash2 className="h-4 w-4" />
                    </button>
                  )}
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Matière première *
                    </label>
                    <select
                      value={ligne.id_matiere_premiere}
                      onChange={(e) => handleLigneChange(index, 'id_matiere_premiere', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value="">Sélectionner</option>
                      {materials.map((material) => (
                        <option key={material.id_matiere_premiere} value={material.id_matiere_premiere}>
                          {material.nom}
                        </option>
                      ))}
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Quantité *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={ligne.quantite}
                      onChange={(e) => handleLigneChange(index, 'quantite', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Unité *
                    </label>
                    <select
                      value={ligne.unite}
                      onChange={(e) => handleLigneChange(index, 'unite', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    >
                      <option value="">Sélectionner</option>
                      <option value="kg">kg</option>
                      <option value="m²">m²</option>
                      <option value="m³">m³</option>
                      <option value="pieces">Pièces</option>
                      <option value="m">m</option>
                      <option value="L">L</option>
                    </select>
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Montant ($) *
                    </label>
                    <input
                      type="number"
                      step="0.01"
                      value={ligne.montant}
                      onChange={(e) => handleLigneChange(index, 'montant', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      required
                    />
                  </div>
                  
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Section
                    </label>
                    <select
                      value={ligne.section}
                      onChange={(e) => handleLigneChange(index, 'section', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Sélectionner</option>
                      {sections.map((section) => (
                        <option key={section} value={section}>{section}</option>
                      ))}
                    </select>
                  </div>
                </div>
              </div>
            ))}
            
            <button
              type="button"
              onClick={addLigne}
              className="w-full py-2 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors flex items-center justify-center"
            >
              <Plus className="h-4 w-4 mr-2" />
              Ajouter une ligne
            </button>
          </div>

          {/* Total */}
          <div className="border-t border-gray-200 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-lg font-semibold text-gray-900">Total:</span>
              <span className="text-2xl font-bold text-blue-600">
                {new Intl.NumberFormat('fr-CA', {
                  style: 'currency',
                  currency: 'CAD'
                }).format(total)}
              </span>
            </div>
          </div>

          {/* Erreur */}
          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
              {error}
            </div>
          )}

          {/* Boutons */}
          <div className="flex justify-end space-x-3 pt-6 border-t border-gray-200">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors flex items-center"
            >
              {loading ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Sauvegarde...
                </>
              ) : (
                <>
                  <Save className="h-4 w-4 mr-2" />
                  {order ? 'Mettre à jour' : 'Créer la commande'}
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

