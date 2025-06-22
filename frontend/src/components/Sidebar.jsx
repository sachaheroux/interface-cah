import React from 'react'
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
  X
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
                return (
                  <Link
                    key={item.name}
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
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'nav-item',
                    isActive && 'active'
                  )}
                >
                  <Icon className="mr-3 h-5 w-5" />
                  {item.name}
                </Link>
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