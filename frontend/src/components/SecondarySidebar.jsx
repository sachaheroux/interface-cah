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
  DollarSign,
  Clock,
  Truck,
  Package,
  Hammer,
  Upload,
  Download,
  TrendingUp,
  TrendingDown,
  Calculator,
  Home
} from 'lucide-react'

const getSecondaryNavigation = (pathname, viewMode = 'list', reportsMode = 'buildings') => {
  // Gérer les routes avec paramètres pour l'analyse de projet AVANT le switch
  if (pathname.startsWith('/project-analysis')) {
    return [
      { name: 'Tous les projets', icon: Hammer, href: '/projects' },
      { name: 'Commandes', icon: FileText, href: '/orders' },
      { name: 'Analyse de projet', icon: BarChart3, active: true, href: '/project-analysis' },
    ]
  }
  
  switch (pathname) {    
    case '/buildings':
      return [
        { name: 'Tous les immeubles', icon: List, active: viewMode === 'list' },
        { name: 'Toutes les unités', icon: Users, active: viewMode === 'units' },
        { name: 'Analyse de rentabilité', icon: BarChart3, href: '/buildings/analysis' },
        { name: 'Analyse de dette', icon: Calculator, href: '/buildings/mortgage' },
        { name: 'Analyse d\'achat', icon: TrendingUp, href: '/buildings/property-analysis' },
      ]
    
    case '/buildings/analysis':
    case '/buildings/mortgage':
    case '/buildings/property-analysis':
      // Utiliser la même sidebar que /buildings
      return [
        { name: 'Tous les immeubles', icon: List, href: '/buildings' },
        { name: 'Toutes les unités', icon: Users, href: '/buildings' },
        { name: 'Analyse de rentabilité', icon: BarChart3, href: '/buildings/analysis', active: pathname === '/buildings/analysis' },
        { name: 'Analyse de dette', icon: Calculator, href: '/buildings/mortgage', active: pathname === '/buildings/mortgage' },
        { name: 'Analyse d\'achat', icon: TrendingUp, href: '/buildings/property-analysis', active: pathname === '/buildings/property-analysis' },
      ]
    
    case '/tenants':
    case '/leases':
    case '/rent-payments':
      // Utiliser la même sidebar pour toutes les pages liées aux locataires
      return [
        { name: 'Tous les locataires', icon: Users, href: '/tenants', active: pathname === '/tenants' },
        { name: 'Gérer les baux', icon: FileText, href: '/leases', active: pathname === '/leases' },
        { name: 'Suivi des paiements', icon: DollarSign, href: '/rent-payments', active: pathname === '/rent-payments' },
      ]
    
    case '/transactions':
      // Sidebar dédiée pour les transactions
      return [
        { name: 'Toutes les transactions', icon: DollarSign, active: true },
      ]
    
    
    case '/employees':
      return [
        { name: 'Tous les employés', icon: Users, active: true, href: '/employees' },
        { name: 'Feuilles de temps', icon: Clock, href: '/punch-management' },
        { name: 'Paie', icon: DollarSign },
      ]
    
    case '/punch-management':
      return [
        { name: 'Tous les employés', icon: Users, href: '/employees' },
        { name: 'Feuilles de temps', icon: Clock, active: true, href: '/punch-management' },
        { name: 'Paie', icon: DollarSign },
      ]
    
    case '/contractors':
    case '/suppliers':
    case '/materials':
      return [
        { name: 'Sous-traitants', icon: Truck, active: pathname === '/contractors', href: '/contractors' },
        { name: 'Fournisseurs', icon: Package, active: pathname === '/suppliers', href: '/suppliers' },
        { name: 'Matières premières', icon: Package, active: pathname === '/materials', href: '/materials' },
        { name: 'Factures', icon: DollarSign, href: '/invoices-st', active: pathname === '/invoices-st' },
      ]
    
    case '/invoices-st':
      return [
        { name: 'Sous-traitants', icon: Truck, href: '/contractors' },
        { name: 'Fournisseurs', icon: Package, href: '/suppliers' },
        { name: 'Matières premières', icon: Package, href: '/materials' },
        { name: 'Factures', icon: DollarSign, active: true, href: '/invoices-st' },
      ]
    
    case '/projects':
    case '/orders':
      return [
        { name: 'Tous les projets', icon: Hammer, active: pathname === '/projects', href: '/projects' },
        { name: 'Commandes', icon: FileText, active: pathname === '/orders', href: '/orders' },
        { name: 'Analyse de projet', icon: BarChart3, active: pathname.startsWith('/project-analysis'), href: '/project-analysis' },
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

// Fonction pour déterminer le titre de la sidebar selon la section principale
const getSidebarTitle = (pathname) => {
  // Section Immeubles
  if (pathname === '/buildings' || pathname.startsWith('/buildings/')) {
    return 'Gestion Immeubles'
  }
  
  // Section Locataires
  if (pathname === '/tenants' || pathname === '/leases' || pathname === '/rent-payments') {
    return 'Gestion Locataires'
  }
  
  // Section Transactions
  if (pathname === '/transactions') {
    return 'Gestion Transactions'
  }
  
  // Section Employés & Temps
  if (pathname === '/employees' || pathname === '/punch-management') {
    return 'Employés & Temps'
  }
  
  // Section Fournisseurs & ST
  if (pathname === '/contractors' || pathname === '/suppliers' || pathname === '/materials' || pathname === '/invoices-st') {
    return 'Fournisseurs & ST'
  }
  
  // Section Projets
  if (pathname === '/projects' || pathname === '/orders' || pathname.startsWith('/project-analysis')) {
    return 'Projets Construction'
  }
  
  // Section Documents
  if (pathname === '/documents') {
    return 'Documents'
  }
  
  // Section Mon profil
  if (pathname === '/settings') {
    return 'Mon profil'
  }
  
  // Section Rapports
  if (pathname === '/reports') {
    return 'Rapports'
  }
  
  return ''
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
  const sidebarTitle = getSidebarTitle(location.pathname)

  // Ne pas afficher la sidebar sur la page d'accueil
  if (location.pathname === '/') {
    return null
  }

  return (
    <div className="w-48 lg:w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 fixed left-0 top-20 sm:top-16 bottom-0 z-40 overflow-y-auto hidden md:block">
      <div className="p-3 lg:p-4">
        <h2 className="text-base lg:text-lg font-semibold text-gray-900 dark:text-white mb-3 lg:mb-4">
          {sidebarTitle}
        </h2>
        
        <nav className="space-y-1">
          {secondaryNav.map((item, index) => {
            const Icon = item.icon
            
            const handleClick = () => {
              // Si l'item a un href, naviguer vers cette page
              if (item.href) {
                navigate(item.href)
                return
              }
              
              // Gestion spéciale pour la page Buildings
              if (location.pathname === '/buildings') {
                if (item.name === 'Tous les immeubles') {
                  window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: 'list' }))
                } else if (item.name === 'Toutes les unités') {
                  window.dispatchEvent(new CustomEvent('buildingsViewChange', { detail: 'units' }))
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
              
              // Gestion spéciale pour la page Tenants
              if (location.pathname === '/tenants') {
                if (item.name === 'Tous les locataires') {
                  // Déclencher un événement pour recharger la liste
                  window.dispatchEvent(new CustomEvent('tenantsViewChange', { detail: 'all' }))
                } else if (item.name === 'Actifs') {
                  window.dispatchEvent(new CustomEvent('tenantsViewChange', { detail: 'active' }))
                } else if (item.name === 'En attente') {
                  window.dispatchEvent(new CustomEvent('tenantsViewChange', { detail: 'pending' }))
                } else if (item.name === 'Ajouter locataire') {
                  window.dispatchEvent(new CustomEvent('addTenant'))
                } else if (item.name === 'Paiements') {
                  // TODO: Implémenter la gestion des paiements
                  console.log('Gestion des paiements')
                }
              }
              
              // Gestion spéciale pour la page Leases
              if (location.pathname === '/leases') {
                if (item.name === 'Tous les baux') {
                  window.dispatchEvent(new CustomEvent('leasesViewChange', { detail: 'all' }))
                } else if (item.name === 'Actifs') {
                  window.dispatchEvent(new CustomEvent('leasesViewChange', { detail: 'active' }))
                } else if (item.name === 'Expirés') {
                  window.dispatchEvent(new CustomEvent('leasesViewChange', { detail: 'expired' }))
                } else if (item.name === 'À venir') {
                  window.dispatchEvent(new CustomEvent('leasesViewChange', { detail: 'upcoming' }))
                } else if (item.name === 'Nouveau bail') {
                  window.dispatchEvent(new CustomEvent('addLease'))
                }
              }
            }
            
            return (
              <button
                key={index}
                onClick={handleClick}
                className={`w-full flex items-center px-2 lg:px-3 py-2 text-xs lg:text-sm font-medium rounded-lg transition-colors duration-200 ${
                  item.active 
                    ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300' 
                    : 'text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700'
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