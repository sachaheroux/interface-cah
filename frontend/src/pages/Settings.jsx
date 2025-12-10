import React from 'react'
import { Settings as SettingsIcon, User, Shield, Bell, Database, Moon, Sun } from 'lucide-react'
import { useTheme } from '../hooks/useTheme'

export default function Settings() {
  const { theme, toggleTheme } = useTheme()

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Paramètres & Utilisateurs</h1>
        <p className="text-gray-600 dark:text-gray-400 mt-1">Configuration du système et gestion des accès</p>
      </div>

      {/* Section Apparence */}
      <div className="card dark:bg-gray-800 dark:border-gray-700">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center">
            {theme === 'dark' ? (
              <Moon className="h-6 w-6 text-blue-500 mr-3" />
            ) : (
              <Sun className="h-6 w-6 text-yellow-500 mr-3" />
            )}
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Apparence</h3>
          </div>
        </div>
        <p className="text-gray-600 dark:text-gray-400 mb-4">
          Choisissez entre le mode jour et le mode nuit pour reposer vos yeux.
        </p>
        
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Mode {theme === 'dark' ? 'Nuit' : 'Jour'}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
              {theme === 'dark' 
                ? 'Fond sombre pour réduire la fatigue oculaire' 
                : 'Fond clair pour une meilleure visibilité'}
            </p>
          </div>
          <button
            onClick={toggleTheme}
            className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 ${
              theme === 'dark' ? 'bg-blue-600' : 'bg-gray-300'
            }`}
            role="switch"
            aria-checked={theme === 'dark'}
            aria-label="Basculer le thème"
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                theme === 'dark' ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <User className="h-6 w-6 text-blue-500 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Gestion des Utilisateurs</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Gérer les comptes utilisateurs et leurs permissions.</p>
          <button className="btn-primary">Gérer les Utilisateurs</button>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <Shield className="h-6 w-6 text-green-500 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sécurité</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Configurer les paramètres de sécurité et d'authentification.</p>
          <button className="btn-secondary">Paramètres de Sécurité</button>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <Bell className="h-6 w-6 text-yellow-500 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Configurer les alertes et notifications système.</p>
          <button className="btn-secondary">Configurer Notifications</button>
        </div>

        <div className="card dark:bg-gray-800 dark:border-gray-700">
          <div className="flex items-center mb-4">
            <Database className="h-6 w-6 text-purple-500 mr-3" />
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Sauvegarde</h3>
          </div>
          <p className="text-gray-600 dark:text-gray-400 mb-4">Gérer les sauvegardes et la restauration des données.</p>
          <button className="btn-secondary">Gérer Sauvegardes</button>
        </div>
      </div>
    </div>
  )
} 