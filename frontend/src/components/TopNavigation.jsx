import React, { useState, useEffect } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
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
  User,
  LogOut,
  UserCircle,
  Clock
} from 'lucide-react'
import clsx from 'clsx'

const navigation = [
  { name: 'Immeubles', href: '/buildings', icon: Building2, role: 'admin' },
  { name: 'Locataires', href: '/tenants', icon: Users, role: 'admin' },
  { name: 'Transactions', href: '/transactions', icon: Receipt, role: 'admin' },
  { name: 'Employés', href: '/employees', icon: UserCheck, role: 'admin' },
  { name: 'Fournisseurs & ST', href: '/contractors', icon: Truck, role: 'admin' },
  { name: 'Projets', href: '/projects', icon: Hammer, role: 'admin' },
  { name: 'Documents', href: '/documents', icon: FileText, role: 'admin' },
  { name: 'Paramètres', href: '/settings', icon: Settings, role: 'admin' },
  // Pointages uniquement pour les employés
  { name: 'Pointages', href: '/employee-punch', icon: Clock, role: 'employe' },
]

export default function TopNavigation() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showUserMenu, setShowUserMenu] = useState(false)

  useEffect(() => {
    // Récupérer les infos utilisateur depuis localStorage
    const userStr = localStorage.getItem('user')
    if (userStr) {
      try {
        setUser(JSON.parse(userStr))
      } catch (e) {
        console.error('Erreur parsing user:', e)
      }
    }
  }, [])

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

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
            {navigation
              .filter((item) => {
                // Filtrer selon le rôle utilisateur
                if (!user) return false
                
                // Si l'utilisateur est admin, il voit tout SAUF Pointages
                if (user.role === 'admin') {
                  return item.role !== 'employe'
                }
                
                // Si l'utilisateur est employé, il ne voit que l'onglet Pointages
                if (user.role === 'employe') {
                  return item.name === 'Pointages'
                }
                
                return false
              })
              .map((item) => {
              const Icon = item.icon
              const isActive = location.pathname === item.href
              
              // Pour les employés, rediriger vers la page mobile de pointage
              const href = (user?.role === 'employe' && item.name === 'Pointages') 
                ? '/employee-punch' 
                : item.href
              
              return (
                <Link
                  key={item.name}
                  to={href}
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
          <div className="relative">
            <div className="flex items-center space-x-2 lg:space-x-3">
              {user && (
                <div className="text-right hidden lg:block">
                  <div className="text-sm font-medium text-gray-900">
                    {user.prenom} {user.nom}
                  </div>
                  <div className="text-xs text-gray-500">{user.email}</div>
                </div>
              )}
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100"
              >
                <User className="h-6 w-6 lg:h-8 lg:w-8" />
              </button>
            </div>

            {/* Dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 py-1 z-50">
                <div className="px-4 py-2 border-b border-gray-200">
                  <p className="text-sm font-medium text-gray-900">
                    {user?.prenom} {user?.nom}
                  </p>
                  <p className="text-xs text-gray-500 truncate">{user?.email}</p>
                </div>
                
                <Link
                  to="/settings"
                  onClick={() => setShowUserMenu(false)}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                >
                  <UserCircle className="h-4 w-4 mr-2" />
                  Mon profil
                </Link>
                
                <button
                  onClick={handleLogout}
                  className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                >
                  <LogOut className="h-4 w-4 mr-2" />
                  Déconnexion
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  )
} 