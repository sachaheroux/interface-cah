import React from 'react'
import { useLocation } from 'react-router-dom'
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

const getSecondaryNavigation = (pathname) => {
  switch (pathname) {
    case '/dashboard':
      return [
        { name: 'Vue d\'ensemble', icon: BarChart3, active: true },
        { name: 'Statistiques', icon: BarChart3 },
        { name: 'Rapports', icon: FileText },
        { name: 'Alertes', icon: Calendar },
      ]
    
    case '/buildings':
      return [
        { name: 'Tous les immeubles', icon: List, active: true },
        { name: 'Vue carte', icon: MapPin },
        { name: 'Ajouter immeuble', icon: Plus },
        { name: 'Filtres', icon: Filter },
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
    
    case '/maintenance':
      return [
        { name: 'Toutes interventions', icon: Wrench, active: true },
        { name: 'En attente', icon: Clock },
        { name: 'En cours', icon: Settings },
        { name: 'Terminées', icon: List },
        { name: 'Nouvelle demande', icon: Plus },
        { name: 'Planification', icon: Calendar },
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
        { name: 'En cours', icon: Settings },
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
    
    default:
      return []
  }
}

export default function SecondarySidebar() {
  const location = useLocation()
  const secondaryNav = getSecondaryNavigation(location.pathname)

  // Ne pas afficher la sidebar sur le tableau de bord principal
  if (location.pathname === '/dashboard' || location.pathname === '/') {
    return null
  }

  return (
    <div className="w-64 bg-white border-r border-gray-200 fixed left-0 top-16 bottom-0 z-40 overflow-y-auto">
      <div className="p-4">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">
          {location.pathname === '/buildings' && 'Gestion Immeubles'}
          {location.pathname === '/tenants' && 'Gestion Locataires'}
          {location.pathname === '/maintenance' && 'Entretien & Réparations'}
          {location.pathname === '/billing' && 'Facturation & Dépenses'}
          {location.pathname === '/employees' && 'Employés & Temps'}
          {location.pathname === '/contractors' && 'Sous-traitants'}
          {location.pathname === '/projects' && 'Projets Construction'}
          {location.pathname === '/documents' && 'Documents'}
          {location.pathname === '/settings' && 'Paramètres'}
        </h2>
        
        <nav className="space-y-1">
          {secondaryNav.map((item, index) => {
            const Icon = item.icon
            return (
              <button
                key={index}
                className={`w-full flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-200 ${
                  item.active 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                }`}
              >
                <Icon className="h-4 w-4 mr-3" />
                {item.name}
              </button>
            )
          })}
        </nav>
      </div>
    </div>
  )
} 