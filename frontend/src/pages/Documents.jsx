import React, { useState } from 'react'
import { FileText, Plus, Upload, Folder } from 'lucide-react'
import DocumentUpload from '../components/DocumentUpload'

export default function Documents() {
  const [showUpload, setShowUpload] = useState(false)

  const handleUploadSuccess = (result) => {
    console.log('✅ Document uploadé avec succès:', result)
    setShowUpload(false)
    // Ici on pourrait rafraîchir la liste des documents
  }

  const handleToggleUpload = () => {
    console.log('🔘 Bouton Téléverser Document cliqué')
    console.log('📊 État actuel showUpload:', showUpload)
    setShowUpload(!showUpload)
    console.log('📊 Nouvel état showUpload:', !showUpload)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
          <p className="text-gray-600 mt-1">Bibliothèque de fichiers et documents</p>
        </div>
        <button 
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg flex items-center transition-colors"
          onClick={handleToggleUpload}
        >
          <Upload className="h-5 w-5 mr-2" />
          Téléverser Document
        </button>
      </div>

      {/* Section Upload */}
      {showUpload && (
        <DocumentUpload onUploadSuccess={handleUploadSuccess} />
      )}

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