import React from 'react'
import { Truck, Plus, Phone, Mail } from 'lucide-react'

export default function Contractors() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Sous-traitants</h1>
          <p className="text-gray-600 mt-1">Gestion des fournisseurs et sous-traitants</p>
        </div>
        <button className="btn-primary flex items-center">
          <Plus className="h-5 w-5 mr-2" />
          Nouveau Sous-traitant
        </button>
      </div>

      <div className="card text-center py-12">
        <Truck className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-lg font-medium text-gray-900 mb-2">Aucun sous-traitant</h3>
        <p className="text-gray-600 mb-4">Commencez par ajouter vos fournisseurs et sous-traitants.</p>
        <button className="btn-primary">
          <Plus className="h-5 w-5 mr-2" />
          Ajouter un Sous-traitant
        </button>
      </div>
    </div>
  )
} 