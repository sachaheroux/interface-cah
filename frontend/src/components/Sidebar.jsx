import React, { useState, useEffect } from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  LayoutDashboard, 
  Building2, 
  Users, 
  Wrench, 
  Receipt, 
  UserCheck, 
  Truck, 
  Hammer, 
  FileText, 
  Settings,
  X,
  Clock,
  Calendar,
  DollarSign,
  ChevronDown,
  ChevronRight
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Immeubles', href: '/buildings', icon: Building2 },
  { name: 'Locataires', href: '/tenants', icon: Users },
  { name: 'Entretien & Réparations', href: '/maintenance', icon: Wrench },
  { name: 'Facturation & Dépenses', href: '/billing', icon: Receipt },
  { name: 'Employés & Temps', href: '/employees', icon: UserCheck },
  { name: 'Sous-traitants', href: '/contractors', icon: Truck },
  { name: 'Projets de Construction', href: '/projects', icon: Hammer },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Paramètres', href: '/settings', icon: Settings },
]

export default function Sidebar({ sidebarOpen, setSidebarOpen }) {
  const location = useLocation()
  
  // Vérifier si on est sur une page liée aux employés
  const isEmployeesSection = location.pathname.startsWith('/employees') || location.pathname.startsWith('/punch-management')
  
  // État pour gérer l'ouverture/fermeture des sous-menus
  const [expandedMenus, setExpandedMenus] = useState({
    employees: isEmployeesSection
  })

  // S'assurer que le menu est ouvert quand on est sur une page d'employés
  useEffect(() => {
    if (isEmployeesSection) {
      setExpandedMenus(prev => ({
        ...prev,
        employees: true
      }))
    }
  }, [location.pathname, isEmployeesSection])

  const toggleMenu = (menuName) => {
    setExpandedMenus(prev => ({
      ...prev,
      [menuName]: !prev[menuName]
    }))
  }

  return (
    <>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-gray-600 bg-opacity-75" onClick={() => setSidebarOpen(false)} />
          <div className="fixed inset-y-0 left-0 flex w-full max-w-xs flex-col bg-white">
            <div className="flex h-16 items-center justify-between px-4">
              <h1 className="text-xl font-bold text-gray-900">Interface CAH</h1>
              <button
                onClick={() => setSidebarOpen(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                <X className="h-6 w-6" />
              </button>
            </div>
            <nav className="flex-1 space-y-1 px-2 py-4">
              {navigation.map((item) => {
                const Icon = item.icon
                const isActive = location.pathname === item.href
                const isEmployeesItem = item.name === 'Employés & Temps'
                const isExpanded = expandedMenus.employees
                
                return (
                  <div key={item.name}>
                    {isEmployeesItem ? (
                      <button
                        onClick={(e) => {
                          e.preventDefault()
                          toggleMenu('employees')
                        }}
                        className={clsx(
                          'nav-item w-full text-left',
                          (isActive || isExpanded) && 'active'
                        )}
                      >
                        <Icon className="mr-3 h-5 w-5" />
                        {item.name}
                        {isExpanded ? (
                          <ChevronDown className="ml-auto h-4 w-4" />
                        ) : (
                          <ChevronRight className="ml-auto h-4 w-4" />
                        )}
                      </button>
                    ) : (
                      <Link
                        to={item.href}
                        onClick={() => setSidebarOpen(false)}
                        className={clsx(
                          'nav-item',
                          isActive && 'active'
                        )}
                      >
                        <Icon className="mr-3 h-5 w-5" />
                        {item.name}
                      </Link>
                    )}
                    
                    {/* Sous-menus pour Employés & Temps */}
                    {isEmployeesItem && isExpanded && (
                      <div className="ml-8 mt-1 space-y-1">
                        <Link
                          to="/employees"
                          onClick={() => setSidebarOpen(false)}
                          className={clsx(
                            'nav-item text-sm',
                            location.pathname === '/employees' && 'active'
                          )}
                        >
                          <UserCheck className="mr-3 h-4 w-4" />
                          Tous les employés
                        </Link>
                      <Link
                        to="/punch-management"
                        onClick={(e) => {
                          setSidebarOpen(false)
                          // S'assurer que le menu reste ouvert
                          setExpandedMenus(prev => ({
                            ...prev,
                            employees: true
                          }))
                        }}
                        className={clsx(
                          'nav-item text-sm',
                          location.pathname === '/punch-management' && 'active'
                        )}
                      >
                        <FileText className="mr-3 h-4 w-4" />
                        Feuilles de temps
                      </Link>
                        <div className="nav-item text-sm cursor-not-allowed opacity-50">
                          <Calendar className="mr-3 h-4 w-4" />
                          Horaires
                        </div>
                        <div className="nav-item text-sm cursor-not-allowed opacity-50">
                          <FileText className="mr-3 h-4 w-4" />
                          Rapports RH
                        </div>
                        <div className="nav-item text-sm cursor-not-allowed opacity-50">
                          <DollarSign className="mr-3 h-4 w-4" />
                          Paie
                        </div>
                      </div>
                    )}
                  </div>
                )
              })}
            </nav>
          </div>
        </div>
      )}

      {/* Desktop sidebar */}
      <div className="hidden lg:flex lg:w-64 lg:flex-col lg:fixed lg:inset-y-0">
        <div className="flex flex-col flex-grow bg-white border-r border-gray-200">
          {/* Logo */}
          <div className="flex items-center h-16 px-4 bg-primary-600">
            <Building2 className="h-8 w-8 text-white mr-3" />
            <h1 className="text-xl font-bold text-white">Interface CAH</h1>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-2 py-4">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              const isEmployeesItem = item.name === 'Employés & Temps'
              const isExpanded = expandedMenus.employees
              
              return (
                <div key={item.name}>
                  {isEmployeesItem ? (
                    <button
                      onClick={(e) => {
                        e.preventDefault()
                        toggleMenu('employees')
                      }}
                      className={clsx(
                        'nav-item w-full text-left',
                        (isActive || isExpanded) && 'active'
                      )}
                    >
                      <Icon className="mr-3 h-5 w-5" />
                      {item.name}
                      {isExpanded ? (
                        <ChevronDown className="ml-auto h-4 w-4" />
                      ) : (
                        <ChevronRight className="ml-auto h-4 w-4" />
                      )}
                    </button>
                  ) : (
                    <Link
                      to={item.href}
                      className={clsx(
                        'nav-item',
                        isActive && 'active'
                      )}
                    >
                      <Icon className="mr-3 h-5 w-5" />
                      {item.name}
                    </Link>
                  )}
                  
                  {/* Sous-menus pour Employés & Temps */}
                  {isEmployeesItem && isExpanded && (
                    <div className="ml-8 mt-1 space-y-1">
                      <Link
                        to="/employees"
                        className={clsx(
                          'nav-item text-sm',
                          location.pathname === '/employees' && 'active'
                        )}
                      >
                        <UserCheck className="mr-3 h-4 w-4" />
                        Tous les employés
                      </Link>
                      <Link
                        to="/punch-management"
                        onClick={(e) => {
                          // S'assurer que le menu reste ouvert et que la navigation fonctionne
                          setExpandedMenus(prev => ({
                            ...prev,
                            employees: true
                          }))
                          // Ne pas empêcher la navigation par défaut
                          // Le Link de React Router gère déjà la navigation
                        }}
                        className={clsx(
                          'nav-item text-sm cursor-pointer',
                          location.pathname === '/punch-management' && 'active'
                        )}
                      >
                        <FileText className="mr-3 h-4 w-4" />
                        Feuilles de temps
                      </Link>
                      <div className="nav-item text-sm cursor-not-allowed opacity-50">
                        <Calendar className="mr-3 h-4 w-4" />
                        Horaires
                      </div>
                      <div className="nav-item text-sm cursor-not-allowed opacity-50">
                        <FileText className="mr-3 h-4 w-4" />
                        Rapports RH
                      </div>
                      <div className="nav-item text-sm cursor-not-allowed opacity-50">
                        <DollarSign className="mr-3 h-4 w-4" />
                        Paie
                      </div>
                    </div>
                  )}
                </div>
              )
            })}
          </nav>
          
          {/* Footer */}
          <div className="p-4 border-t border-gray-200">
            <div className="text-xs text-gray-500">
              Interface CAH v1.0.0
              <br />
              Gestion de Construction
            </div>
          </div>
        </div>
      </div>
    </>
  )
} 