import React from 'react'
import { Receipt, Plus, DollarSign, FileText } from 'lucide-react'

export default function Billing() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Facturation & Dépenses</h1>
          <p className="text-gray-600 mt-1">Gestion financière et facturation</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouvelle Facture
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="card text-center">
          <DollarSign className="h-12 w-12 text-green-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Revenus Totaux</h3>
          <p className="text-2xl font-bold text-green-600">85 000$</p>
        </div>
        <div className="card text-center">
          <Receipt className="h-12 w-12 text-blue-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Factures en Attente</h3>
          <p className="text-2xl font-bold text-blue-600">12</p>
        </div>
        <div className="card text-center">
          <FileText className="h-12 w-12 text-yellow-500 mx-auto mb-4" />
          <h3 className="text-lg font-semibold mb-2">Dépenses ce Mois</h3>
          <p className="text-2xl font-bold text-yellow-600">15 750$</p>
        </div>
      </div>
    </div>
  )
} 