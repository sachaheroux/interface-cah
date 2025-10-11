import React from 'react'
import { Link, useLocation } from 'react-router-dom'
import { 
  Building2, 
  Users, 
  Receipt, 
  UserCheck, 
  Truck, 
  Hammer, 
  FileText, 
  Settings,
  Bell,
  User
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Immeubles', href: '/buildings', icon: Building2 },
  { name: 'Locataires', href: '/tenants', icon: Users },
  { name: 'Transactions', href: '/transactions', icon: Receipt },
  { name: 'Employés', href: '/employees', icon: UserCheck },
  { name: 'Sous-traitants', href: '/contractors', icon: Truck },
  { name: 'Projets', href: '/projects', icon: Hammer },
  { name: 'Documents', href: '/documents', icon: FileText },
  { name: 'Paramètres', href: '/settings', icon: Settings },
]

export default function TopNavigation() {
  const location = useLocation()

  return (
    <header className="bg-white shadow-sm border-b border-gray-200 fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between h-20 sm:h-16 px-3 lg:px-6">
        {/* Logo */}
        <div className="flex items-center flex-shrink-0">
          <Building2 className="h-6 w-6 lg:h-8 lg:w-8 text-primary-600 mr-2 lg:mr-3" />
          <h1 className="text-lg lg:text-xl font-bold text-gray-900 hidden sm:block">Interface CAH</h1>
          <h1 className="text-lg font-bold text-gray-900 sm:hidden">CAH</h1>
        </div>
        
        {/* Navigation horizontale - s'adapte automatiquement à la largeur */}
        <nav className="flex-1 overflow-x-auto scrollbar-hide mx-1 sm:mx-2">
          <div className="flex justify-center items-center h-full min-w-max" style={{ gap: 'max(0.2vw, 0.25rem)' }}>
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex flex-col sm:flex-row items-center justify-center rounded-lg transition-colors duration-200 whitespace-nowrap font-medium',
                    'py-1 sm:py-2',
                    isActive 
                      ? 'bg-primary-100 text-primary-700' 
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                  )}
                  style={{
                    paddingLeft: 'clamp(0.25rem, 0.8vw, 1rem)',
                    paddingRight: 'clamp(0.25rem, 0.8vw, 1rem)',
                    fontSize: 'clamp(0.7rem, 0.9vw, 1rem)'
                  }}
                >
                  <Icon 
                    className="sm:mr-1.5" 
                    style={{ 
                      width: 'clamp(0.8rem, 1vw, 1.25rem)', 
                      height: 'clamp(0.8rem, 1vw, 1.25rem)' 
                    }} 
                  />
                  <span>{item.name}</span>
                </Link>
              )
            })}
          </div>
        </nav>

        {/* Right side */}
        <div className="flex items-center space-x-2 lg:space-x-4 flex-shrink-0">
          {/* Notifications */}
          <button className="p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative">
            <Bell className="h-5 w-5 lg:h-6 lg:w-6" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-2 lg:space-x-3">
            <div className="text-right hidden lg:block">
              <div className="text-sm font-medium text-gray-900">Administrateur</div>
              <div className="text-xs text-gray-500">admin@interfacecah.com</div>
            </div>
            <button className="flex items-center p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100">
              <User className="h-6 w-6 lg:h-8 lg:w-8" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
} 