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
        
        {/* Navigation horizontale */}
        <nav className="flex space-x-0.5 sm:space-x-1 lg:space-x-2 flex-1 justify-center mx-1 sm:mx-4 overflow-x-auto md:overflow-x-visible scrollbar-hide">
          <div className="flex space-x-0.5 sm:space-x-1 lg:space-x-2 min-w-max md:min-w-0 md:justify-center md:flex-1">
            {navigation.map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={clsx(
                    'flex flex-col sm:flex-row items-center px-1 sm:px-2 lg:px-4 py-1 sm:py-2 text-xs sm:text-sm lg:text-base font-medium rounded-lg transition-colors duration-200 whitespace-nowrap',
                    isActive 
                      ? 'bg-primary-100 text-primary-700' 
                      : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                  )}
                >
                  <Icon className="h-3 w-3 sm:h-4 sm:w-4 lg:h-5 lg:w-5 sm:mr-2" />
                  <span className="text-xs sm:text-sm lg:text-base">{item.name}</span>
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