import React, { useState, useEffect } from 'react'
import { 
  Calculator, 
  TrendingUp, 
  TrendingDown, 
  DollarSign, 
  Home, 
  Calendar,
  BarChart3,
  PieChart,
  FileText,
  Save,
  RefreshCw
} from 'lucide-react'

const PropertyAnalysis = () => {
  // États pour les données d'entrée
  const [formData, setFormData] = useState({
    prixAchat: '',
    miseDeFond: '',
    tauxInteret: '',
    anneesRemboursement: '',
    revenuLocatifAnnuel: '',
    taxesTotales: '',
    assurancesTotales: '',
    fraisOuverture: '',
    entretienTerrain: '',
    anneesAnalyse: '',
    tauxReparations: '1.5'  // 1.5% par défaut
  })

  // États pour les résultats
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(false)
  const [currentStep, setCurrentStep] = useState(1)
  const [errors, setErrors] = useState({})

  // Validation des données
  const validateForm = () => {
    const newErrors = {}
    
    if (!formData.prixAchat || parseFloat(formData.prixAchat) <= 0) {
      newErrors.prixAchat = 'Le prix d\'achat doit être supérieur à 0'
    }
    if (!formData.miseDeFond || parseFloat(formData.miseDeFond) <= 0) {
      newErrors.miseDeFond = 'La mise de fond doit être supérieure à 0'
    }
    if (!formData.tauxInteret || parseFloat(formData.tauxInteret) <= 0) {
      newErrors.tauxInteret = 'Le taux d\'intérêt doit être supérieur à 0'
    }
    if (!formData.anneesRemboursement || parseInt(formData.anneesRemboursement) <= 0) {
      newErrors.anneesRemboursement = 'Le nombre d\'années doit être supérieur à 0'
    }
    if (!formData.revenuLocatifAnnuel || parseFloat(formData.revenuLocatifAnnuel) < 0) {
      newErrors.revenuLocatifAnnuel = 'Le revenu locatif ne peut pas être négatif'
    }
    if (!formData.taxesTotales || parseFloat(formData.taxesTotales) < 0) {
      newErrors.taxesTotales = 'Les taxes ne peuvent pas être négatives'
    }
    if (!formData.assurancesTotales || parseFloat(formData.assurancesTotales) < 0) {
      newErrors.assurancesTotales = 'Les assurances ne peuvent pas être négatives'
    }
    if (!formData.fraisOuverture || parseFloat(formData.fraisOuverture) < 0) {
      newErrors.fraisOuverture = 'Les frais d\'ouverture ne peuvent pas être négatifs'
    }
    if (!formData.entretienTerrain || parseFloat(formData.entretienTerrain) < 0) {
      newErrors.entretienTerrain = 'L\'entretien ne peut pas être négatif'
    }
    if (!formData.anneesAnalyse || parseInt(formData.anneesAnalyse) <= 0) {
      newErrors.anneesAnalyse = 'Le nombre d\'années d\'analyse doit être supérieur à 0'
    }
    if (!formData.tauxReparations || parseFloat(formData.tauxReparations) < 0 || parseFloat(formData.tauxReparations) > 10) {
      newErrors.tauxReparations = 'Le taux de réparations doit être entre 0 et 10%'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  // Calculs basés sur le code VB
  const calculateAnalysis = () => {
    if (!validateForm()) return

    setLoading(true)
    
    // Conversion des données
    const prixAchat = parseFloat(formData.prixAchat)
    const miseDeFond = parseFloat(formData.miseDeFond)
    const tauxInteretAnnuel = parseFloat(formData.tauxInteret)
    const anneesRemboursement = parseInt(formData.anneesRemboursement)
    const revenuLocatifAnnuel = parseFloat(formData.revenuLocatifAnnuel)
    const taxesTotales = parseFloat(formData.taxesTotales)
    const assurancesTotales = parseFloat(formData.assurancesTotales)
    const fraisOuverture = parseFloat(formData.fraisOuverture)
    const entretienTerrain = parseFloat(formData.entretienTerrain)
    const anneesAnalyse = parseInt(formData.anneesAnalyse)
    const tauxReparations = parseFloat(formData.tauxReparations) / 100  // Convertir % en décimal

    // Calculs du prêt hypothécaire
    const capital = prixAchat - miseDeFond
    const tauxInteretMensuel = tauxInteretAnnuel / 12
    const nombreMensualites = anneesRemboursement * 12
    
    // Calcul de la mensualité
    const mensualite = (capital * tauxInteretMensuel) / (1 - Math.pow(1 + tauxInteretMensuel, -nombreMensualites))

    // Simulation sur les années d'analyse
    let capitalRestant = capital
    let totalInteretsPayes = 0
    let totalMensualitesPayees = 0
    
    for (let i = 1; i <= anneesAnalyse * 12; i++) {
      const interetMensuel = capitalRestant * tauxInteretMensuel
      const amortissementCapital = mensualite - interetMensuel
      capitalRestant -= amortissementCapital
      totalInteretsPayes += interetMensuel
      totalMensualitesPayees += mensualite
    }

    // Calculs des revenus et dépenses
    const revenusLocatifsCumules = revenuLocatifAnnuel * anneesAnalyse
    const fraisGestion = revenusLocatifsCumules * 0.05 // 5% comme dans le code VB
    const totalMensualites = mensualite * 12 * anneesAnalyse
    const taxesCumulees = taxesTotales * anneesAnalyse
    const entretienCumule = entretienTerrain * 12 * anneesAnalyse
    const reparations = prixAchat * tauxReparations * anneesAnalyse // % annuel défini par l'utilisateur

    // Appréciation de la propriété (1.9% par an comme dans le code VB)
    let valeurRevente = prixAchat
    for (let j = 1; j <= anneesAnalyse; j++) {
      valeurRevente *= 1.019
    }

    // Inflation des assurances (2% par an comme dans le code VB)
    let assurancesCumulees = assurancesTotales
    for (let k = 1; k <= anneesAnalyse; k++) {
      assurancesCumulees += assurancesTotales * Math.pow(1.02, k - 1)
    }

    // Calcul du cash flow net (avec frais d'ouverture comme dépense, sans mise de fond qui est l'investissement)
    const capitalRembourse = capital - capitalRestant
    const cashFlowNet = revenusLocatifsCumules - taxesCumulees - totalMensualites - assurancesCumulees - fraisOuverture - entretienCumule - fraisGestion - reparations

    // Calculs pour les graphiques
    const donneesAnnueles = []
    let capitalAnnee = capital
    let valeurProprieteAnnee = prixAchat
    let revenusCumules = 0
    let depensesCumules = 0  // Commencer à 0 (sans l'investissement initial)

    for (let annee = 1; annee <= anneesAnalyse; annee++) {
      // Calculs pour cette année
      const revenusAnnee = revenuLocatifAnnuel
      const taxesAnnee = taxesTotales
      const assurancesAnnee = assurancesTotales * Math.pow(1.02, annee - 1)
      const mensualitesAnnee = mensualite * 12
      const entretienAnnee = entretienTerrain * 12
      const gestionAnnee = revenusAnnee * 0.05
      const reparationsAnnee = prixAchat * tauxReparations  // Réparations annuelles selon le taux

      // Mise à jour des totaux
      revenusCumules += revenusAnnee
      // Ajouter frais d'ouverture seulement la première année
      const fraisOuvertureAnnee = annee === 1 ? fraisOuverture : 0
      depensesCumules += taxesAnnee + assurancesAnnee + mensualitesAnnee + entretienAnnee + gestionAnnee + reparationsAnnee + fraisOuvertureAnnee

      // Calcul du capital restant
      for (let mois = 1; mois <= 12; mois++) {
        const interetMensuel = capitalAnnee * tauxInteretMensuel
        const amortissementCapital = mensualite - interetMensuel
        capitalAnnee -= amortissementCapital
      }

      // Appréciation de la propriété
      valeurProprieteAnnee *= 1.019

      donneesAnnueles.push({
        annee,
        revenusCumules,
        depensesCumules,
        capitalRestant: capitalAnnee,
        valeurPropriete: valeurProprieteAnnee,
        cashFlowCumule: revenusCumules - depensesCumules
      })
    }

    const analysisResults = {
      // Données de base
      prixAchat,
      miseDeFond,
      capital,
      tauxInteretAnnuel,
      anneesRemboursement,
      anneesAnalyse,

      // Résultats financiers
      mensualite,
      capitalRestant,
      capitalRembourse,
      totalInteretsPayes,
      totalMensualitesPayees,

      // Revenus et dépenses
      revenusLocatifsCumules,
      taxesCumulees,
      assurancesCumulees,
      fraisGestion,
      entretienCumule,
      reparations,
      fraisOuverture,

      // Résultats finaux
      valeurRevente,
      cashFlowNet,
      investissementInitial: miseDeFond,  // Seulement la mise de fond est l'investissement
      rendementBrut: ((cashFlowNet + valeurRevente - miseDeFond) / miseDeFond) * 100,
      rendementNet: (cashFlowNet / miseDeFond) * 100,

      // Données pour graphiques
      donneesAnnueles
    }

    setResults(analysisResults)
    setLoading(false)
  }

  // Gestion des changements de formulaire
  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    // Effacer l'erreur pour ce champ
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: ''
      }))
    }
  }

  // Formatage des montants
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('fr-CA', {
      style: 'currency',
      currency: 'CAD'
    }).format(amount)
  }

  // Étapes du formulaire
  const steps = [
    { id: 1, title: 'Informations de base', icon: Home },
    { id: 2, title: 'Financement', icon: DollarSign },
    { id: 3, title: 'Revenus locatifs', icon: TrendingUp },
    { id: 4, title: 'Dépenses', icon: TrendingDown },
    { id: 5, title: 'Analyse', icon: Calendar }
  ]

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Calculator className="h-8 w-8 text-primary-600" />
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Analyse d'Achat de Propriété</h1>
            <p className="text-gray-600">
              Calculez la rentabilité d'un investissement immobilier
            </p>
          </div>
        </div>
      </div>

      {/* Configuration */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Configuration de l'analyse</h2>
        
        {/* Indicateur de progression */}
        <div className="mb-8">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => {
              const Icon = step.icon
              const isActive = currentStep === step.id
              const isCompleted = currentStep > step.id
              
              return (
                <div key={step.id} className="flex items-center">
                  <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                    isActive ? 'bg-blue-600 border-blue-600 text-white' :
                    isCompleted ? 'bg-green-500 border-green-500 text-white' :
                    'bg-white border-gray-300 text-gray-400'
                  }`}>
                    <Icon className="h-5 w-5" />
                  </div>
                  <div className="ml-3">
                    <p className={`text-sm font-medium ${
                      isActive ? 'text-blue-600' : 'text-gray-500'
                    }`}>
                      {step.title}
                    </p>
                  </div>
                  {index < steps.length - 1 && (
                    <div className={`flex-1 h-0.5 mx-4 ${
                      isCompleted ? 'bg-green-500' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              )
            })}
          </div>
        </div>

        {currentStep === 1 && (
          <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Informations de base</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Prix d'achat de l'immeuble *
                  </label>
                  <input
                    type="number"
                    value={formData.prixAchat}
                    onChange={(e) => handleInputChange('prixAchat', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.prixAchat ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 500000"
                  />
                  {errors.prixAchat && <p className="text-red-500 text-sm mt-1">{errors.prixAchat}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Mise de fond *
                  </label>
                  <input
                    type="number"
                    value={formData.miseDeFond}
                    onChange={(e) => handleInputChange('miseDeFond', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.miseDeFond ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 100000"
                  />
                  {errors.miseDeFond && <p className="text-red-500 text-sm mt-1">{errors.miseDeFond}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre d'années d'analyse *
                  </label>
                  <input
                    type="number"
                    value={formData.anneesAnalyse}
                    onChange={(e) => handleInputChange('anneesAnalyse', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.anneesAnalyse ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 5"
                  />
                  {errors.anneesAnalyse && <p className="text-red-500 text-sm mt-1">{errors.anneesAnalyse}</p>}
                </div>
              </div>
            </div>
          )}

        {currentStep === 2 && (
          <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Financement</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Taux d'intérêt annuel (décimal) *
                  </label>
                  <input
                    type="number"
                    step="0.001"
                    value={formData.tauxInteret}
                    onChange={(e) => handleInputChange('tauxInteret', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.tauxInteret ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 0.05 pour 5%"
                  />
                  {errors.tauxInteret && <p className="text-red-500 text-sm mt-1">{errors.tauxInteret}</p>}
                  <p className="text-gray-500 text-sm mt-1">Exemple: 0.05 pour 5%</p>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Nombre d'années de remboursement *
                  </label>
                  <input
                    type="number"
                    value={formData.anneesRemboursement}
                    onChange={(e) => handleInputChange('anneesRemboursement', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.anneesRemboursement ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 25"
                  />
                  {errors.anneesRemboursement && <p className="text-red-500 text-sm mt-1">{errors.anneesRemboursement}</p>}
                </div>
              </div>
            </div>
          )}

        {currentStep === 3 && (
          <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Revenus locatifs</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Revenu locatif annuel *
                  </label>
                  <input
                    type="number"
                    value={formData.revenuLocatifAnnuel}
                    onChange={(e) => handleInputChange('revenuLocatifAnnuel', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.revenuLocatifAnnuel ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 36000"
                  />
                  {errors.revenuLocatifAnnuel && <p className="text-red-500 text-sm mt-1">{errors.revenuLocatifAnnuel}</p>}
                </div>
              </div>
            </div>
          )}

        {currentStep === 4 && (
          <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Dépenses</h2>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Taxes totales annuelles (scolaire + municipale) *
                  </label>
                  <input
                    type="number"
                    value={formData.taxesTotales}
                    onChange={(e) => handleInputChange('taxesTotales', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.taxesTotales ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 6000"
                  />
                  {errors.taxesTotales && <p className="text-red-500 text-sm mt-1">{errors.taxesTotales}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Assurances totales annuelles *
                  </label>
                  <input
                    type="number"
                    value={formData.assurancesTotales}
                    onChange={(e) => handleInputChange('assurancesTotales', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.assurancesTotales ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 1200"
                  />
                  {errors.assurancesTotales && <p className="text-red-500 text-sm mt-1">{errors.assurancesTotales}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Frais d'ouverture de dossier (notaire, taxes de bienvenue) *
                  </label>
                  <input
                    type="number"
                    value={formData.fraisOuverture}
                    onChange={(e) => handleInputChange('fraisOuverture', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.fraisOuverture ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 15000"
                  />
                  {errors.fraisOuverture && <p className="text-red-500 text-sm mt-1">{errors.fraisOuverture}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Entretien du terrain mensuel (déneigement, gazon) *
                  </label>
                  <input
                    type="number"
                    value={formData.entretienTerrain}
                    onChange={(e) => handleInputChange('entretienTerrain', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.entretienTerrain ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 200"
                  />
                  {errors.entretienTerrain && <p className="text-red-500 text-sm mt-1">{errors.entretienTerrain}</p>}
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Taux de réparations annuel (% de la valeur) *
                  </label>
                  <input
                    type="number"
                    step="0.1"
                    value={formData.tauxReparations}
                    onChange={(e) => handleInputChange('tauxReparations', e.target.value)}
                    className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 ${
                      errors.tauxReparations ? 'border-red-500' : 'border-gray-300'
                    }`}
                    placeholder="Ex: 1.5"
                  />
                  {errors.tauxReparations && <p className="text-red-500 text-sm mt-1">{errors.tauxReparations}</p>}
                  <p className="text-gray-500 text-sm mt-1">Recommandé: 1-2% (1.5% par défaut)</p>
                </div>
              </div>
            </div>
          )}

        {currentStep === 5 && (
          <div>
              <h2 className="text-xl font-semibold text-gray-900 mb-6">Analyse</h2>
              <div className="text-center">
                <button
                  onClick={calculateAnalysis}
                  disabled={loading}
                  className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
                >
                  {loading ? (
                    <RefreshCw className="h-5 w-5 animate-spin" />
                  ) : (
                    <Calculator className="h-5 w-5" />
                  )}
                  {loading ? 'Calcul en cours...' : 'Analyser la propriété'}
                </button>
              </div>
            </div>
          )}

        {/* Navigation */}
        <div className="flex justify-between mt-8">
            <button
              onClick={() => setCurrentStep(Math.max(1, currentStep - 1))}
              disabled={currentStep === 1}
              className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Précédent
            </button>
            
            {currentStep < 5 ? (
              <button
                onClick={() => setCurrentStep(Math.min(5, currentStep + 1))}
                className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Suivant
              </button>
            ) : (
              <button
                onClick={calculateAnalysis}
                disabled={loading}
                className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                <Calculator className="h-4 w-4" />
                Analyser
              </button>
            )}
        </div>
      </div>

      {/* Résultats */}
      {results && (
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center gap-2">
            <BarChart3 className="h-6 w-6" />
            Résultats de l'analyse
          </h2>

          {/* Métriques principales */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className="bg-blue-50 p-6 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <DollarSign className="h-6 w-6 text-blue-600" />
                <h3 className="text-lg font-semibold text-blue-900">Cash Flow Net</h3>
              </div>
              <p className={`text-2xl font-bold ${
                results.cashFlowNet >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {formatCurrency(results.cashFlowNet)}
              </p>
            </div>

            <div className="bg-green-50 p-6 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <TrendingUp className="h-6 w-6 text-green-600" />
                <h3 className="text-lg font-semibold text-green-900">Valeur de revente</h3>
              </div>
              <p className="text-2xl font-bold text-green-600">
                {formatCurrency(results.valeurRevente)}
              </p>
            </div>

            <div className="bg-purple-50 p-6 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <PieChart className="h-6 w-6 text-purple-600" />
                <h3 className="text-lg font-semibold text-purple-900">Rendement brut</h3>
              </div>
              <p className="text-2xl font-bold text-purple-600">
                {results.rendementBrut.toFixed(2)}%
              </p>
            </div>

            <div className="bg-orange-50 p-6 rounded-lg">
              <div className="flex items-center gap-3 mb-2">
                <Calculator className="h-6 w-6 text-orange-600" />
                <h3 className="text-lg font-semibold text-orange-900">Rendement net</h3>
              </div>
              <p className={`text-2xl font-bold ${
                results.rendementNet >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {results.rendementNet.toFixed(2)}%
              </p>
            </div>
          </div>

          {/* Détails financiers */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Détails du prêt</h3>
              <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Mensualité:</span>
                      <span className="font-semibold">{formatCurrency(results.mensualite)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Capital restant:</span>
                      <span className="font-semibold">{formatCurrency(results.capitalRestant)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Capital remboursé:</span>
                      <span className="font-semibold text-green-600">{formatCurrency(results.capitalRembourse)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Intérêts payés:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.totalInteretsPayes)}</span>
                    </div>
              </div>
            </div>

            <div>
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Revenus et dépenses</h3>
              <div className="space-y-3">
                    <div className="flex justify-between">
                      <span className="text-gray-600">Revenus locatifs:</span>
                      <span className="font-semibold text-green-600">{formatCurrency(results.revenusLocatifsCumules)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Taxes:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.taxesCumulees)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Assurances:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.assurancesCumulees)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Frais de gestion:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.fraisGestion)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Entretien:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.entretienCumule)}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-600">Réparations:</span>
                      <span className="font-semibold text-red-600">{formatCurrency(results.reparations)}</span>
                    </div>
              </div>
            </div>
          </div>

          {/* Graphique d'évolution */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Évolution sur {results.anneesAnalyse} ans</h3>
            <div className="bg-gray-50 p-6 rounded-lg">
              <div className="flex gap-4">
                {/* Axe Y avec les montants */}
                <div className="flex flex-col justify-between h-96 py-2">
                  {(() => {
                    // Calculer la hauteur totale maximale (somme des 3 segments)
                    const maxTotalValue = Math.max(
                      ...results.donneesAnnueles.map(d => d.revenusCumules + d.depensesCumules + d.valeurPropriete)
                    )
                    
                    // Arrondir au million supérieur pour des chiffres ronds
                    const roundedMax = Math.ceil(maxTotalValue / 100000) * 100000
                    const step = roundedMax / 5
                    
                    const labels = []
                    for (let i = 5; i >= 0; i--) {
                      const value = step * i
                      labels.push(
                        <div key={i} className="text-xs text-gray-600 text-right pr-2 whitespace-nowrap">
                          {new Intl.NumberFormat('fr-CA', {
                            style: 'currency',
                            currency: 'CAD',
                            maximumFractionDigits: 0
                          }).format(value)}
                        </div>
                      )
                    }
                    return labels
                  })()}
                </div>

                {/* Graphique avec barres empilées */}
                <div className="flex-1 overflow-x-auto">
                  <div className="h-96 flex items-end justify-start gap-4 min-w-full">
                    {results.donneesAnnueles.map((data, index) => {
                      // Calculer la hauteur totale maximale (somme des 3 segments)
                      const maxTotalValue = Math.max(
                        ...results.donneesAnnueles.map(d => d.revenusCumules + d.depensesCumules + d.valeurPropriete)
                      )
                      const roundedMax = Math.ceil(maxTotalValue / 100000) * 100000
                      
                      // Calculer la hauteur de chaque segment proportionnellement à la somme totale
                      const totalHeight = 360
                      const revenusHeight = (data.revenusCumules / roundedMax) * totalHeight
                      const depensesHeight = (data.depensesCumules / roundedMax) * totalHeight
                      const valeurHeight = (data.valeurPropriete / roundedMax) * totalHeight
                      
                      return (
                        <div key={index} className="flex flex-col items-center flex-1" style={{ minWidth: '80px' }}>
                          <div className="flex flex-col items-center w-full h-full justify-end mb-2">
                            <div className="w-full flex flex-col justify-end items-center" style={{ height: '360px' }}>
                              {/* Valeur propriété (bleu) - en haut */}
                              <div 
                                className="w-full bg-blue-500 rounded-t flex items-center justify-center"
                                style={{ height: `${valeurHeight}px`, minHeight: '2px' }}
                                title={`Valeur propriété: ${formatCurrency(data.valeurPropriete)}`}
                              >
                                {valeurHeight > 30 && (
                                  <span className="text-xs text-white font-semibold">
                                    {formatCurrency(data.valeurPropriete)}
                                  </span>
                                )}
                              </div>
                              
                              {/* Dépenses (rouge) - au milieu */}
                              <div 
                                className="w-full bg-red-500 flex items-center justify-center"
                                style={{ height: `${depensesHeight}px`, minHeight: '2px' }}
                                title={`Dépenses: ${formatCurrency(data.depensesCumules)}`}
                              >
                                {depensesHeight > 30 && (
                                  <span className="text-xs text-white font-semibold">
                                    {formatCurrency(data.depensesCumules)}
                                  </span>
                                )}
                              </div>
                              
                              {/* Revenus (vert) - en bas */}
                              <div 
                                className="w-full bg-green-500 rounded-b flex items-center justify-center"
                                style={{ height: `${revenusHeight}px`, minHeight: '2px' }}
                                title={`Revenus: ${formatCurrency(data.revenusCumules)}`}
                              >
                                {revenusHeight > 30 && (
                                  <span className="text-xs text-white font-semibold">
                                    {formatCurrency(data.revenusCumules)}
                                  </span>
                                )}
                              </div>
                            </div>
                          </div>
                          
                          <div className="text-sm font-medium text-gray-700 mt-2">Année {index + 1}</div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              </div>
              <div className="flex justify-center gap-8 mt-6">
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-green-500 rounded"></div>
                      <span className="text-sm text-gray-600">Revenus</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-red-500 rounded"></div>
                      <span className="text-sm text-gray-600">Dépenses</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <div className="w-4 h-4 bg-blue-500 rounded"></div>
                      <span className="text-sm text-gray-600">Valeur propriété</span>
                    </div>
              </div>
            </div>
          </div>

          {/* Boutons d'action */}
          <div className="flex justify-center gap-4">
            <button
              onClick={() => {
                setResults(null)
                setCurrentStep(1)
                setFormData({
                  prixAchat: '',
                  miseDeFond: '',
                  tauxInteret: '',
                  anneesRemboursement: '',
                  revenuLocatifAnnuel: '',
                  taxesTotales: '',
                  assurancesTotales: '',
                  fraisOuverture: '',
                  entretienTerrain: '',
                  anneesAnalyse: '',
                  tauxReparations: '1.5'
                })
              }}
              className="px-6 py-3 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 flex items-center gap-2"
            >
              <RefreshCw className="h-4 w-4" />
              Nouvelle analyse
            </button>
                
            <button
              onClick={() => {
                // TODO: Implémenter l'export PDF
                alert('Export PDF à implémenter')
              }}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
            >
              <FileText className="h-4 w-4" />
              Exporter PDF
            </button>
          </div>
        </div>
      )}
    </div>
  )
}

export default PropertyAnalysis
