import React, { useState, useEffect, useCallback, useMemo } from 'react';
import api from '../services/api';

const InvoiceForm = ({ onClose, onSuccess, buildingId = null, unitId = null }) => {
  const [formData, setFormData] = useState({
    invoiceNumber: '',
    category: '',
    source: '',
    date: new Date().toISOString().split('T')[0],
    amount: 0,
    paymentType: '',
    buildingId: buildingId || '',
    unitId: unitId || '',
    pdfFilename: '',
    notes: '',
    type: 'rental_building'
  });

  const [buildings, setBuildings] = useState([]);
  const [units, setUnits] = useState([]);
  const [filteredBuildings, setFilteredBuildings] = useState([]);
  const [buildingSearchTerm, setBuildingSearchTerm] = useState('');
  const [showBuildingDropdown, setShowBuildingDropdown] = useState(false);
  const [selectedBuildingName, setSelectedBuildingName] = useState('');
  const [currency, setCurrency] = useState('CAD');
  const [filteredUnits, setFilteredUnits] = useState([]);
  const [unitSearchTerm, setUnitSearchTerm] = useState('');
  const [showUnitDropdown, setShowUnitDropdown] = useState(false);
  const [selectedUnitName, setSelectedUnitName] = useState('');
  const [constants, setConstants] = useState({
    categories: {
      "municipal_taxes": "Taxes municipales",
      "school_taxes": "Taxes scolaire",
      "insurance": "Assurance",
      "snow_removal": "Déneigement",
      "lawn_care": "Gazon",
      "management": "Gestion",
      "renovations": "Rénovations",
      "repairs": "Réparations",
      "wifi": "WiFi",
      "electricity": "Électricité",
      "other": "Autres"
    },
    paymentTypes: {
      "bank_transfer": "Virement bancaire",
      "check": "Chèque",
      "cash": "Espèces"
    },
    invoiceTypes: {
      "rental_building": "Immeuble en location",
      "construction_project": "Projet de construction"
    }
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    loadData();
  }, []);

  // Fermer les dropdowns quand on clique ailleurs
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (showBuildingDropdown && !event.target.closest('.building-search')) {
        setShowBuildingDropdown(false);
      }
      if (showUnitDropdown && !event.target.closest('.unit-search')) {
        setShowUnitDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, [showBuildingDropdown, showUnitDropdown]);

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      
      // Charger les immeubles
      const buildingsResponse = await api.get('/api/buildings');
      setBuildings(buildingsResponse.data || []);
      
      // Charger les constantes
      try {
        const constantsResponse = await api.get('/api/invoices/constants');
        if (constantsResponse.data) {
          setConstants(constantsResponse.data);
        }
      } catch (constantsError) {
        console.warn('Erreur chargement constantes, utilisation des valeurs par défaut:', constantsError);
        // Les constantes par défaut sont déjà définies dans useState
      }
      
      // Si un immeuble est spécifié, charger ses unités
      if (buildingId) {
        // Charger les unités directement ici pour éviter la référence circulaire
        const building = buildingsResponse.data?.find(b => b.id === buildingId);
        if (building && building.unitData) {
          const buildingUnits = Object.keys(building.unitData).map(unitId => ({
            id: unitId,
            name: unitId
          }));
          setUnits(buildingUnits);
        }
      }
    } catch (err) {
      console.error('Erreur lors du chargement des données:', err);
      // Ne pas afficher d'erreur pour les données optionnelles
      setError('');
    } finally {
      setLoading(false);
    }
  }, [buildingId]);

  const loadUnitsForBuilding = useCallback(async (buildingId) => {
    try {
      const building = buildings.find(b => b.id === buildingId);
      if (building && building.unitData) {
        const buildingUnits = Object.keys(building.unitData).map(unitId => ({
          id: unitId,
          name: unitId
        }));
        setUnits(buildingUnits);
      }
    } catch (err) {
      console.error('Erreur lors du chargement des unités:', err);
    }
  }, [buildings]);

  // Optimiser les options des menus déroulants
  const categoryOptions = useMemo(() => 
    Object.entries(constants.categories).map(([key, value]) => (
      <option key={key} value={key}>{value}</option>
    )), [constants.categories]
  );

  const paymentTypeOptions = useMemo(() => 
    Object.entries(constants.paymentTypes).map(([key, value]) => (
      <option key={key} value={key}>{value}</option>
    )), [constants.paymentTypes]
  );

  const buildingOptions = useMemo(() => 
    buildings.map(building => (
      <option key={building.id} value={building.id}>{building.name}</option>
    )), [buildings]
  );

  const unitOptions = useMemo(() => 
    units.map(unit => (
      <option key={unit.id} value={unit.id}>{unit.name}</option>
    )), [units]
  );

  // Logique de recherche d'immeubles
  const handleBuildingSearch = (searchTerm) => {
    setBuildingSearchTerm(searchTerm);
    if (searchTerm.length > 0) {
      const filtered = buildings.filter(building => 
        building.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredBuildings(filtered);
      setShowBuildingDropdown(true);
    } else {
      setFilteredBuildings([]);
      setShowBuildingDropdown(false);
    }
  };

  const selectBuilding = (building) => {
    setFormData(prev => ({
      ...prev,
      buildingId: building.id,
      unitId: '' // Reset unit selection
    }));
    setSelectedBuildingName(building.name);
    setBuildingSearchTerm(building.name);
    setShowBuildingDropdown(false);
    
    // Reset unit selection
    setSelectedUnitName('');
    setUnitSearchTerm('');
    setShowUnitDropdown(false);
    
    // Charger les unités pour cet immeuble
    console.log('Immeuble sélectionné:', building); // Debug
    
    if (building.unitData) {
      const buildingUnits = Object.keys(building.unitData).map(unitId => ({
        id: unitId,
        name: unitId
      }));
      setUnits(buildingUnits);
      setFilteredUnits(buildingUnits);
      console.log('Unités chargées depuis unitData:', buildingUnits);
    } else if (building.units && Array.isArray(building.units)) {
      // Fallback: si les unités sont dans un tableau
      const buildingUnits = building.units.map(unit => ({
        id: unit.id || unit,
        name: unit.name || unit
      }));
      setUnits(buildingUnits);
      setFilteredUnits(buildingUnits);
      console.log('Unités chargées depuis units array:', buildingUnits);
    } else {
      // Fallback: générer des unités par défaut basées sur le nombre d'unités
      const unitCount = building.unitCount || 0;
      const buildingUnits = [];
      for (let i = 1; i <= unitCount; i++) {
        buildingUnits.push({
          id: `unit-${i}`,
          name: `Unité ${i}`
        });
      }
      setUnits(buildingUnits);
      setFilteredUnits(buildingUnits);
      console.log('Unités générées par défaut:', buildingUnits);
    }
  };

  // Logique de recherche d'unités
  const handleUnitSearch = (searchTerm) => {
    setUnitSearchTerm(searchTerm);
    if (searchTerm.length > 0) {
      const filtered = units.filter(unit => 
        unit.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
      setFilteredUnits(filtered);
      setShowUnitDropdown(true);
    } else {
      setFilteredUnits(units);
      setShowUnitDropdown(true);
    }
  };

  const selectUnit = (unit) => {
    setFormData(prev => ({
      ...prev,
      unitId: unit.id
    }));
    setSelectedUnitName(unit.name);
    setUnitSearchTerm(unit.name);
    setShowUnitDropdown(false);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    // Gestion spéciale pour le montant avec virgules
    if (name === 'amount') {
      // Remplacer les points par des virgules et valider le format
      let cleanValue = value.replace(/\./g, ',');
      // Vérifier que c'est un nombre valide avec virgule
      if (cleanValue === '' || /^\d+([,]\d{1,2})?$/.test(cleanValue)) {
        setFormData(prev => ({
          ...prev,
          [name]: cleanValue
        }));
      }
      return;
    }
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Si l'immeuble change, charger ses unités
    if (name === 'buildingId') {
      const buildingId = parseInt(value);
      setFormData(prev => ({
        ...prev,
        buildingId: buildingId || null,
        unitId: '' // Reset unit selection
      }));
      if (buildingId) {
        loadUnitsForBuilding(buildingId);
      } else {
        setUnits([]);
      }
    }
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setFormData(prev => ({
        ...prev,
        pdfFilename: file.name
      }));
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      // Validation
      if (!formData.invoiceNumber.trim()) {
        throw new Error('Le numéro de facture est requis');
      }
      if (!formData.category) {
        throw new Error('La catégorie est requise');
      }
      if (!formData.date) {
        throw new Error('La date est requise');
      }
      if (formData.amount <= 0) {
        throw new Error('Le montant doit être supérieur à 0');
      }
      if (!formData.paymentType) {
        throw new Error('Le type de paiement est requis');
      }
      if (!formData.buildingId) {
        throw new Error('L\'immeuble est requis');
      }

      // Préparer les données
      const invoiceData = {
        ...formData,
        buildingId: parseInt(formData.buildingId),
        unitId: formData.unitId || null,
        amount: parseFloat(formData.amount.replace(',', '.')) // Convertir virgule en point pour l'API
      };

      // Créer la facture
      const response = await api.post('/api/invoices', invoiceData);
      
      console.log('Facture créée:', response.data);
      
      if (onSuccess) {
        onSuccess(response.data.data);
      }
      
      onClose();
    } catch (err) {
      console.error('Erreur lors de la création de la facture:', err);
      setError(err.response?.data?.detail || err.message || 'Erreur lors de la création de la facture');
    } finally {
      setLoading(false);
    }
  };

  if (loading && !buildings.length) {
    return (
      <div className="flex justify-center items-center p-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div 
      className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div className="bg-white rounded-lg p-6 w-full max-w-2xl max-h-[90vh] overflow-y-auto mx-4">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Nouvelle Facture</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {error && (
          <div className="mb-4 p-4 bg-red-100 border border-red-400 text-red-700 rounded">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Informations de base */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Numéro de facture *
              </label>
              <input
                type="text"
                name="invoiceNumber"
                value={formData.invoiceNumber}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="Ex: FAC-2024-001"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Catégorie *
              </label>
              <select
                name="category"
                value={formData.category}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Sélectionner une catégorie</option>
                {categoryOptions}
              </select>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Source (d'où vient la facture)
            </label>
            <input
              type="text"
              name="source"
              value={formData.source}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Ex: Ville de Montréal, Hydro-Québec, etc."
            />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Date *
              </label>
              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Montant *
              </label>
              <div className="flex max-w-sm">
                <select
                  value={currency}
                  onChange={(e) => setCurrency(e.target.value)}
                  className="px-3 py-2 border border-gray-300 border-r-0 rounded-l-md bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-28"
                >
                  <option value="CAD">$ CAD</option>
                  <option value="USD">$ USD</option>
                  <option value="EUR">€ EUR</option>
                </select>
                <input
                  type="text"
                  name="amount"
                  value={formData.amount}
                  onChange={handleInputChange}
                  className="flex-1 px-3 py-2 border border-gray-300 rounded-r-md focus:outline-none focus:ring-2 focus:ring-blue-500 w-24"
                  placeholder="0,00"
                  required
                />
              </div>
              <p className="text-xs text-gray-500 mt-1">Utilisez la virgule (,) pour les décimales</p>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Type de paiement *
            </label>
            <select
              name="paymentType"
              value={formData.paymentType}
              onChange={handleInputChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              required
            >
              <option value="">Sélectionner un type de paiement</option>
              {paymentTypeOptions}
            </select>
          </div>

          {/* Immeuble et unité */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="relative building-search">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Immeuble *
              </label>
              <input
                type="text"
                value={buildingSearchTerm}
                onChange={(e) => handleBuildingSearch(e.target.value)}
                onFocus={() => setShowBuildingDropdown(true)}
                placeholder="Rechercher un immeuble..."
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              />
              
              {/* Dropdown des immeubles filtrés */}
              {showBuildingDropdown && filteredBuildings.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                  {filteredBuildings.map(building => (
                    <div
                      key={building.id}
                      onClick={() => selectBuilding(building)}
                      className="px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900">{building.name}</div>
                      <div className="text-sm text-gray-500">{building.address?.street}, {building.address?.city}</div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Message si aucun immeuble trouvé */}
              {showBuildingDropdown && buildingSearchTerm.length > 0 && filteredBuildings.length === 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
                  <div className="px-3 py-2 text-gray-500 text-sm">
                    Aucun immeuble trouvé
                  </div>
                </div>
              )}
            </div>

            <div className="relative unit-search">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unité (optionnel)
              </label>
              <input
                type="text"
                value={unitSearchTerm}
                onChange={(e) => handleUnitSearch(e.target.value)}
                onFocus={() => formData.buildingId && setShowUnitDropdown(true)}
                placeholder={formData.buildingId ? "Rechercher une unité..." : "Sélectionnez d'abord un immeuble"}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
                disabled={!formData.buildingId}
              />
              
              {/* Dropdown des unités filtrées */}
              {showUnitDropdown && formData.buildingId && filteredUnits.length > 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
                  <div
                    onClick={() => {
                      setFormData(prev => ({ ...prev, unitId: '' }));
                      setSelectedUnitName('');
                      setUnitSearchTerm('');
                      setShowUnitDropdown(false);
                    }}
                    className="px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100"
                  >
                    <div className="font-medium text-gray-900">Tout l'immeuble</div>
                    <div className="text-sm text-gray-500">Facture pour l'ensemble de l'immeuble</div>
                  </div>
                  {filteredUnits.map(unit => (
                    <div
                      key={unit.id}
                      onClick={() => selectUnit(unit)}
                      className="px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
                    >
                      <div className="font-medium text-gray-900">{unit.name}</div>
                    </div>
                  ))}
                </div>
              )}
              
              {/* Message si aucune unité trouvée */}
              {showUnitDropdown && formData.buildingId && unitSearchTerm.length > 0 && filteredUnits.length === 0 && (
                <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg">
                  <div className="px-3 py-2 text-gray-500 text-sm">
                    Aucune unité trouvée
                  </div>
                </div>
              )}
              
              {/* Messages d'état */}
              {formData.buildingId && units.length === 0 && (
                <p className="text-xs text-gray-500 mt-1">Aucune unité disponible pour cet immeuble</p>
              )}
              {formData.buildingId && units.length > 0 && (
                <p className="text-xs text-green-600 mt-1">{units.length} unité(s) disponible(s)</p>
              )}
            </div>
          </div>

          {/* Upload PDF */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              PDF de la facture
            </label>
            <input
              type="file"
              accept=".pdf"
              onChange={handleFileChange}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            {formData.pdfFilename && (
              <p className="mt-1 text-sm text-gray-600">
                Fichier sélectionné: {formData.pdfFilename}
              </p>
            )}
          </div>

          {/* Notes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Notes
            </label>
            <textarea
              name="notes"
              value={formData.notes}
              onChange={handleInputChange}
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="Notes additionnelles..."
            />
          </div>

          {/* Boutons */}
          <div className="flex justify-end space-x-4 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 bg-gray-200 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50"
            >
              {loading ? 'Création...' : 'Créer la facture'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default InvoiceForm;
