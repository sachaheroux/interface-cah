import React, { useState, useEffect } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  Plus, 
  List, 
  Grid, 
  Search, 
  Filter, 
  FileText, 
  Settings as SettingsIcon,
  BarChart3,
  Calendar,
  MapPin,
  Users,
  Wrench,
  DollarSign,
  Clock,
  Truck,
  Hammer,
  Upload,
  Download
} from 'lucide-react'

const getSecondaryNavigation = (pathname, viewMode = 'list', reportsMode = 'buildings') => {
  switch (pathname) {    
    case '/buildings':
      return [
        { name: 'Tous les immeubles', icon: List, active: viewMode === 'list' },
        { name: 'Toutes les unités', icon: Users, active: viewMode === 'units' },
        { name: 'Vue carte', icon: MapPin, active: viewMode === 'map' },
        { name: 'Rapports', icon: FileText },
        { name: 'Maintenance', icon: Wrench },
      ]
    
    case '/tenants':
      return [
        { name: 'Tous les locataires', icon: Users, active: true },
        { name: 'Actifs', icon: List },
        { name: 'En attente', icon: Clock },
        { name: 'Ajouter locataire', icon: Plus },
        { name: 'Contrats', icon: FileText },
        { name: 'Paiements', icon: DollarSign },
      ]
    
    case '/billing':
      return [
        { name: 'Vue d\'ensemble', icon: DollarSign, active: true },
        { name: 'Factures', icon: FileText },
        { name: 'Paiements', icon: List },
        { name: 'Dépenses', icon: BarChart3 },
        { name: 'Rapports', icon: Download },
        { name: 'Nouvelle facture', icon: Plus },
      ]
    
    case '/employees':
      return [
        { name: 'Tous les employés', icon: Users, active: true },
        { name: 'Feuilles de temps', icon: Clock },
        { name: 'Horaires', icon: Calendar },
        { name: 'Ajouter employé', icon: Plus },
        { name: 'Rapports RH', icon: FileText },
        { name: 'Paie', icon: DollarSign },
      ]
    
    case '/contractors':
      return [
        { name: 'Tous les sous-traitants', icon: Truck, active: true },
        { name: 'Contrats actifs', icon: FileText },
        { name: 'Évaluations', icon: BarChart3 },
        { name: 'Ajouter sous-traitant', icon: Plus },
        { name: 'Factures', icon: DollarSign },
        { name: 'Contacts', icon: List },
      ]
    
    case '/projects':
      return [
        { name: 'Tous les projets', icon: Hammer, active: true },
        { name: 'En planification', icon: Calendar },
        { name: 'En cours', icon: SettingsIcon },
        { name: 'Terminés', icon: List },
        { name: 'Nouveau projet', icon: Plus },
        { name: 'Budget', icon: DollarSign },
      ]
    
    case '/documents':
      return [
        { name: 'Tous les documents', icon: FileText, active: true },
        { name: 'Contrats', icon: List },
        { name: 'Plans', icon: Grid },
        { name: 'Factures', icon: DollarSign },
        { name: 'Photos', icon: Upload },
        { name: 'Rechercher', icon: Search },
      ]
    
    case '/settings':
      return [
        { name: 'Général', icon: SettingsIcon, active: true },
        { name: 'Utilisateurs', icon: Users },
        { name: 'Sécurité', icon: List },
        { name: 'Notifications', icon: Calendar },
        { name: 'Sauvegarde', icon: Download },
        { name: 'Support', icon: FileText },
      ]
    
    case '/reports':
      return [
        { name: 'Rapports d\'immeubles', icon: BarChart3, active: reportsMode === 'buildings' },
        { name: 'Rapports d\'unités', icon: Users, active: reportsMode === 'units' },
        { name: 'Retour aux immeubles', icon: List },
        { name: 'Exporter données', icon: Download },
        { name: 'Filtrer par année', icon: Calendar },
      ]
    
    default:
      return []
  }
}

export default function SecondarySidebar() {
  const location = useLocation()
  const navigate = useNavigate()
  const [viewMode, setViewMode] = useState('list')
  const [reportsMode, setReportsMode] = useState('buildings')
  
  // Écouter les changements de vue pour mettre à jour l'état actif
  useEffect(() => {
    const handleViewChange = (event) => {
      setViewMode(event.detail)
    }
    
    const handleReportsViewChange = (event) => {
      setReportsMode(event.detail)
    }
    
    window.addEventListener('buildingsViewChange', handleViewChange)
    window.addEventListener('reportsViewChange', handleReportsViewChange)
    
    return () => {
      window.removeEventListener('buildingsViewChange', handleViewChange)
      window.removeEventListener('reportsViewChange', handleReportsViewChange)
    }
  }, [])
  
  const secondaryNav = getSecondaryNavigation(location.pathname, viewMode, reportsMode)

  // Ne pas afficher la sidebar sur la page d'accueil
  if (location.pathname === '/') {
    return null
  }

  return (
    <div className="w-48 lg:w-64 bg-white border-r border-gray-200 fixed left-0 top-20 sm:top-16 bottom-0 z-40 overflow-y-auto hidden md:block">
      <div className="p-3 lg:p-4">
        <h2 className="text-base lg:text-lg font-semibold text-gray-900 mb-3 lg:mb-4">
          {location.pathname === '/buildings' && 'Gestion Immeubles'}
          {location.pathname === '/tenants' && 'Gestion Locataires'}
          {location.pathname === '/billing' && 'Facturation & Dépenses'}
          {location.pathname === '/employees' && 'Employés & Temps'}
          {location.pathname === '/contractors' && 'Sous-traitants'}
          {location.pathname === '/projects' && 'Projets Construction'}
          {location.pathname === '/documents' && 'Documents'}
          {location.pathname === '/settings' && 'Paramètres'}
          {location.pathname === '/reports' && 'Rapports'}
        </h2>
        
        <nav className="space-y-1">
          {secondaryNav.map((item, index) => {
            const Icon = item.icon
            
            const handleClick = () => {
              // Gestion spéciale pour la page Buildings
              if (location.pathname === '/buildings') {
                if (item.name === 'Vue carte') {
                  window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: 'map' }))
                } else if (item.name === 'Tous les immeubles') {
                  window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: 'list' }))
                } else if (item.name === 'Toutes les unités') {
                  window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: 'units' }))
                } else if (item.name === 'Rapports') {
                  navigate('/reports')
                } else if (item.name === 'Maintenance') {
                  navigate('/maintenance')
                }
              }
              
              // Gestion spéciale pour la page Reports
              if (location.pathname === '/reports') {
                if (item.name === 'Rapports d\'immeubles') {
                  window.dispatchEvent(new CustomEvent('reportsViewChange', { detail: 'buildings' }))
                } else if (item.name === 'Rapports d\'unités') {
                  window.dispatchEvent(new CustomEvent('reportsViewChange', { detail: 'units' }))
                } else if (item.name === 'Retour aux immeubles') {
                  navigate('/buildings')
                } else if (item.name === 'Exporter données') {
                  // TODO: Implémenter l'export de données
                  console.log('Export des données des rapports')
                } else if (item.name === 'Filtrer par année') {
                  // TODO: Implémenter le filtre par année
                  console.log('Filtre par année')
                }
              }
            }
            
            return (
              <button
                key={index}
                onClick={handleClick}
                className={`w-full flex items-center px-2 lg:px-3 py-2 text-xs lg:text-sm font-medium rounded-lg transition-colors duration-200 ${
                  item.active 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-3 w-3 lg:h-4 lg:w-4 mr-2 lg:mr-3" />
                <span className="truncate">{item.name}</span>
              </button>
            )
          })}
        </nav>
      </div>
    </div>
  )
} 