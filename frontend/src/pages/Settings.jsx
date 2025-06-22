import React from 'react'
import { Settings as SettingsIcon, User, Shield, Bell, Database } from 'lucide-react'

export default function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Paramètres & Utilisateurs</h1>
        <p className="text-gray-600 mt-1">Configuration du système et gestion des accès</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card">
          <div className="flex items-center mb-4">
            <User className="h-6 w-6 text-blue-500 mr-3" />
            <h3 className="text-lg font-semibold">Gestion des Utilisateurs</h3>
          </div>
          <p className="text-gray-600 mb-4">Gérer les comptes utilisateurs et leurs permissions.</p>
          <button className="btn-primary">Gérer les Utilisateurs</button>
        </div>

        <div className="card">
          <div className="flex items-center mb-4">
            <Shield className="h-6 w-6 text-green-500 mr-3" />
            <h3 className="text-lg font-semibold">Sécurité</h3>
          </div>
          <p className="text-gray-600 mb-4">Configurer les paramètres de sécurité et d'authentification.</p>
          <button className="btn-secondary">Paramètres de Sécurité</button>
        </div>

        <div className="card">
          <div className="flex items-center mb-4">
            <Bell className="h-6 w-6 text-yellow-500 mr-3" />
            <h3 className="text-lg font-semibold">Notifications</h3>
          </div>
          <p className="text-gray-600 mb-4">Configurer les alertes et notifications système.</p>
          <button className="btn-secondary">Configurer Notifications</button>
        </div>

        <div className="card">
          <div className="flex items-center mb-4">
            <Database className="h-6 w-6 text-purple-500 mr-3" />
            <h3 className="text-lg font-semibold">Sauvegarde</h3>
          </div>
          <p className="text-gray-600 mb-4">Gérer les sauvegardes et la restauration des données.</p>
          <button className="btn-secondary">Gérer Sauvegardes</button>
        </div>
      </div>
    </div>
  )
} 