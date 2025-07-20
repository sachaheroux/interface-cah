import React, { useState } from 'react'
import { Upload, FileText, CheckCircle, AlertCircle } from 'lucide-react'

export default function DocumentUpload({ onUploadSuccess }) {
  const [uploading, setUploading] = useState(false)
  const [uploadStatus, setUploadStatus] = useState(null)

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    // Vérifier le type de fichier
    if (!file.name.toLowerCase().endsWith('.pdf')) {
      setUploadStatus({
        type: 'error',
        message: 'Seuls les fichiers PDF sont acceptés'
      })
      return
    }

    setUploading(true)
    setUploadStatus(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
      const response = await fetch(`${API_BASE_URL}/api/documents/upload`, {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const result = await response.json()
        setUploadStatus({
          type: 'success',
          message: `Fichier "${file.name}" uploadé avec succès`
        })
        if (onUploadSuccess) {
          onUploadSuccess(result)
        }
      } else {
        const error = await response.json()
        setUploadStatus({
          type: 'error',
          message: error.detail || 'Erreur lors de l\'upload'
        })
      }
    } catch (error) {
      setUploadStatus({
        type: 'error',
        message: 'Erreur de connexion lors de l\'upload'
      })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
      <div className="flex items-center mb-4">
        <Upload className="h-5 w-5 text-blue-600 mr-2" />
        <h3 className="text-lg font-medium text-gray-900">
          Upload de Documents PDF
        </h3>
      </div>

      <div className="space-y-4">
        {/* Zone de drop */}
        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-blue-400 transition-colors">
          <input
            type="file"
            accept=".pdf"
            onChange={handleFileUpload}
            disabled={uploading}
            className="hidden"
            id="pdf-upload"
          />
          <label
            htmlFor="pdf-upload"
            className="cursor-pointer flex flex-col items-center"
          >
            <FileText className="h-12 w-12 text-gray-400 mb-4" />
            <div className="text-gray-600">
              {uploading ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Upload en cours...
                </div>
              ) : (
                <>
                  <p className="text-sm font-medium">Cliquez pour sélectionner un fichier PDF</p>
                  <p className="text-xs text-gray-500 mt-1">ou glissez-déposez ici</p>
                </>
              )}
            </div>
          </label>
        </div>

        {/* Statut de l'upload */}
        {uploadStatus && (
          <div className={`flex items-center p-3 rounded-lg ${
            uploadStatus.type === 'success' 
              ? 'bg-green-50 text-green-800' 
              : 'bg-red-50 text-red-800'
          }`}>
            {uploadStatus.type === 'success' ? (
              <CheckCircle className="h-4 w-4 mr-2" />
            ) : (
              <AlertCircle className="h-4 w-4 mr-2" />
            )}
            <span className="text-sm">{uploadStatus.message}</span>
          </div>
        )}

        {/* Instructions */}
        <div className="text-xs text-gray-500">
          <p>• Seuls les fichiers PDF sont acceptés</p>
          <p>• Les fichiers sont stockés sur le serveur</p>
          <p>• Vous pouvez ensuite les associer aux baux des locataires</p>
        </div>
      </div>
    </div>
  )
} 