import React from 'react'
import { FileText, Plus, Upload, Folder } from 'lucide-react'

export default function Documents() {
  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Bibliothèque de fichiers et documents</p>
        </div>
        <button className="btn-primary flex items-center">
          <Upload className="h-5 w-5 mr-2" />
          Téléverser Document
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <div className="card text-center cursor-pointer hover:bg-gray-50">
          <Folder className="h-12 w-12 text-blue-500 mx-auto mb-3" />
          <h3 className="font-medium">Contrats</h3>
          <p className="text-sm text-gray-500">12 fichiers</p>
        </div>
        <div className="card text-center cursor-pointer hover:bg-gray-50">
          <Folder className="h-12 w-12 text-green-500 mx-auto mb-3" />
          <h3 className="font-medium">Plans</h3>
          <p className="text-sm text-gray-500">8 fichiers</p>
        </div>
        <div className="card text-center cursor-pointer hover:bg-gray-50">
          <Folder className="h-12 w-12 text-yellow-500 mx-auto mb-3" />
          <h3 className="font-medium">Factures</h3>
          <p className="text-sm text-gray-500">24 fichiers</p>
        </div>
        <div className="card text-center cursor-pointer hover:bg-gray-50">
          <Folder className="h-12 w-12 text-purple-500 mx-auto mb-3" />
          <h3 className="font-medium">Photos</h3>
          <p className="text-sm text-gray-500">156 fichiers</p>
        </div>
      </div>
    </div>
  )
} 