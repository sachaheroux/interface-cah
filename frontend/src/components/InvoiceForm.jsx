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

  const handleInputChange = (e) => {
    const { name, value } = e.target;
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
        amount: parseFloat(formData.amount)
      };

      // Créer la facture
      const response = await api.post('/invoices', invoiceData);
      
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
              <input
                type="number"
                name="amount"
                value={formData.amount}
                onChange={handleInputChange}
                step="0.01"
                min="0"
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                placeholder="0.00"
                required
              />
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
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Immeuble *
              </label>
              <select
                name="buildingId"
                value={formData.buildingId}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                required
              >
                <option value="">Sélectionner un immeuble</option>
                {buildingOptions}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Unité (optionnel)
              </label>
              <select
                name="unitId"
                value={formData.unitId}
                onChange={handleInputChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                disabled={!formData.buildingId}
              >
                <option value="">Tout l'immeuble</option>
                {unitOptions}
              </select>
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
