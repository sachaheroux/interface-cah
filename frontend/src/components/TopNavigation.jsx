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
  Bell,
  User
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Tableau de bord', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Immeubles', href: '/buildings', icon: Building2 },
  { name: 'Locataires', href: '/tenants', icon: Users },
  { name: 'Entretien', href: '/maintenance', icon: Wrench },
  { name: 'Facturation', href: '/billing', icon: Receipt },
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
      <div className="flex items-center justify-between h-16 px-6">
        {/* Logo */}
        <div className="flex items-center">
          <Building2 className="h-8 w-8 text-primary-600 mr-3" />
          <h1 className="text-xl font-bold text-gray-900">Interface CAH</h1>
        </div>
        
        {/* Navigation horizontale */}
        <nav className="flex space-x-1">
          {navigation.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.href
            return (
              <Link
                key={item.name}
                to={item.href}
                className={clsx(
                  'flex items-center px-4 py-2 text-sm font-medium rounded-lg transition-colors duration-200',
                  isActive 
                    ? 'bg-primary-100 text-primary-700' 
                    : 'text-gray-600 hover:text-primary-600 hover:bg-gray-100'
                )}
              >
                <Icon className="h-4 w-4 mr-2" />
                {item.name}
              </Link>
            )
          })}
        </nav>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative">
            <Bell className="h-6 w-6" />
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="text-right">
              <div className="text-sm font-medium text-gray-900">Administrateur</div>
              <div className="text-xs text-gray-500">admin@interfacecah.com</div>
            </div>
            <button className="flex items-center p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100">
              <User className="h-8 w-8" />
            </button>
          </div>
        </div>
      </div>
    </header>
  )
} 