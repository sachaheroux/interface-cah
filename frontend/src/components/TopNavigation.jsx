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
  Bell,
  User,
  LogOut,
  UserCircle,
  Clock,
  X,
  CheckCircle
} from 'lucide-react'
import clsx from 'clsx'
import { notificationsService } from '../services/api'

const navigation = [
  { name: 'Immeubles', href: '/buildings', icon: Building2, role: 'admin', matchPaths: ['/buildings'] },
  { name: 'Locataires', href: '/tenants', icon: Users, role: 'admin', matchPaths: ['/tenants', '/leases', '/rent-payments'] },
  { name: 'Transactions', href: '/transactions', icon: Receipt, role: 'admin' },
  { name: 'Employés', href: '/employees', icon: UserCheck, role: 'admin', matchPaths: ['/employees', '/punch-management'] },
  { name: 'Fournisseurs & ST', href: '/contractors', icon: Truck, role: 'admin', matchPaths: ['/contractors', '/suppliers', '/materials', '/invoices-st'] },
  { name: 'Projets', href: '/projects', icon: Hammer, role: 'admin', matchPaths: ['/projects', '/orders', '/project-analysis'] },
  { name: 'Documents', href: '/documents', icon: FileText, role: 'admin' },
  // Pointages uniquement pour les employés
  { name: 'Pointages', href: '/employee-punch', icon: Clock, role: 'employe' },
]

export default function TopNavigation() {
  const location = useLocation()
  const navigate = useNavigate()
  const [user, setUser] = useState(null)
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [showNotifications, setShowNotifications] = useState(false)
  const [notifications, setNotifications] = useState([])
  const [unreadCount, setUnreadCount] = useState(0)
  const [loadingNotifications, setLoadingNotifications] = useState(false)

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

  // Charger les notifications
  useEffect(() => {
    // Vérifier que l'utilisateur est authentifié et a un token
    const token = localStorage.getItem('auth_token')
    if (user && user.role === 'admin' && token) {
      loadNotifications()
      // Recharger toutes les 30 secondes
      const interval = setInterval(() => {
        // Vérifier à nouveau le token avant chaque requête
        const currentToken = localStorage.getItem('auth_token')
        if (currentToken) {
          loadNotifications()
        }
      }, 30000)
      return () => clearInterval(interval)
    }
  }, [user])

  const loadNotifications = async () => {
    // Vérifier que le token existe avant de faire la requête
    const token = localStorage.getItem('auth_token')
    if (!token) {
      return
    }

    try {
      setLoadingNotifications(true)
      const response = await notificationsService.getNotifications(false, 10) // 10 dernières non lues
      if (response.data.success) {
        setNotifications(response.data.data || [])
        setUnreadCount(response.data.unread_count || 0)
      }
    } catch (error) {
      // Ne pas logger les erreurs 401 pour éviter le spam dans la console
      // Si l'utilisateur n'est plus authentifié, on arrête simplement de charger
      if (error.response?.status !== 401) {
        console.error('Erreur chargement notifications:', error)
      }
    } finally {
      setLoadingNotifications(false)
    }
  }

  const handleMarkAsRead = async (notificationId) => {
    try {
      await notificationsService.markAsRead(notificationId)
      // Mettre à jour localement
      setNotifications(prev => prev.map(n => 
        n.id_notification === notificationId ? { ...n, lue: true } : n
      ))
      setUnreadCount(prev => Math.max(0, prev - 1))
    } catch (error) {
      console.error('Erreur marquer notification lue:', error)
    }
  }

  const handleMarkAllAsRead = async () => {
    try {
      await notificationsService.markAllAsRead()
      setNotifications(prev => prev.map(n => ({ ...n, lue: true })))
      setUnreadCount(0)
    } catch (error) {
      console.error('Erreur marquer toutes lues:', error)
    }
  }

  const getPriorityColor = (priorite) => {
    switch (priorite) {
      case 'urgent':
        return 'bg-red-100 dark:bg-red-900/20 text-red-800 dark:text-red-300 border-red-200 dark:border-red-800'
      case 'important':
        return 'bg-orange-100 dark:bg-orange-900/20 text-orange-800 dark:text-orange-300 border-orange-200 dark:border-orange-800'
      default:
        return 'bg-blue-100 dark:bg-blue-900/20 text-blue-800 dark:text-blue-300 border-blue-200 dark:border-blue-800'
    }
  }

  const handleLogout = () => {
    localStorage.removeItem('auth_token')
    localStorage.removeItem('user')
    navigate('/login')
  }

  return (
    <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 fixed top-0 left-0 right-0 z-50">
      <div className="flex items-center justify-between h-20 sm:h-16 px-3 lg:px-6">
        {/* Logo */}
        <Link 
          to="/" 
          className="flex items-center flex-shrink-0 cursor-pointer hover:opacity-80 transition-opacity"
        >
          <Building2 className="h-6 w-6 lg:h-8 lg:w-8 text-primary-600 mr-2 lg:mr-3" />
          <h1 className="text-lg lg:text-xl font-bold text-gray-900 dark:text-white hidden sm:block">Interface CAH</h1>
          <h1 className="text-lg font-bold text-gray-900 dark:text-white sm:hidden">CAH</h1>
        </Link>
        
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
              
              // Déterminer si l'item est actif
              // Si matchPaths est défini, vérifier si le pathname correspond à l'un de ces chemins
              // Sinon, utiliser la correspondance exacte avec href
              const isActive = item.matchPaths
                ? item.matchPaths.some(path => location.pathname === path || location.pathname.startsWith(path + '/'))
                : location.pathname === item.href || location.pathname.startsWith(item.href + '/')
              
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
                      ? 'bg-primary-100 dark:bg-primary-900 text-primary-700 dark:text-primary-300' 
                      : 'text-gray-600 dark:text-gray-300 hover:text-primary-600 dark:hover:text-primary-400 hover:bg-gray-100 dark:hover:bg-gray-700'
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
          {/* Notifications - seulement pour les admins */}
          {user && user.role === 'admin' && (
            <div className="relative">
              <button 
                onClick={() => setShowNotifications(!showNotifications)}
                className="p-2 rounded-full text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700 relative"
              >
                <Bell className="h-5 w-5 lg:h-6 lg:w-6" />
                {unreadCount > 0 && (
                  <span className="absolute top-0 right-0 flex items-center justify-center h-5 w-5 text-xs font-bold text-white bg-red-500 rounded-full">
                    {unreadCount > 9 ? '9+' : unreadCount}
                  </span>
                )}
              </button>

              {/* Dropdown notifications */}
              {showNotifications && (
                <div className="absolute right-0 mt-2 w-80 sm:w-96 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50 max-h-96 overflow-hidden flex flex-col">
                  {/* Header */}
                  <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-gray-700">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Notifications</h3>
                    <div className="flex items-center space-x-2">
                      {unreadCount > 0 && (
                        <button
                          onClick={handleMarkAllAsRead}
                          className="text-xs text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                        >
                          Tout marquer comme lu
                        </button>
                      )}
                      <button
                        onClick={() => setShowNotifications(false)}
                        className="text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                  </div>

                  {/* Liste des notifications */}
                  <div className="overflow-y-auto flex-1">
                    {loadingNotifications ? (
                      <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
                      </div>
                    ) : notifications.length === 0 ? (
                      <div className="p-8 text-center">
                        <Bell className="h-12 w-12 text-gray-400 dark:text-gray-500 mx-auto mb-2" />
                        <p className="text-sm text-gray-500 dark:text-gray-400">Aucune notification</p>
                      </div>
                    ) : (
                      <div className="divide-y divide-gray-200 dark:divide-gray-700">
                        {notifications.map((notif) => (
                          <div
                            key={notif.id_notification}
                            className={`p-4 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer transition-colors ${
                              !notif.lue ? 'bg-blue-50 dark:bg-blue-900/10' : ''
                            }`}
                            onClick={() => {
                              if (!notif.lue) {
                                handleMarkAsRead(notif.id_notification)
                              }
                              if (notif.lien) {
                                navigate(notif.lien)
                                setShowNotifications(false)
                              }
                            }}
                          >
                            <div className="flex items-start justify-between">
                              <div className="flex-1">
                                <div className="flex items-center space-x-2 mb-1">
                                  <span className={`px-2 py-0.5 rounded text-xs font-medium border ${getPriorityColor(notif.priorite)}`}>
                                    {notif.priorite === 'urgent' ? 'Urgent' : notif.priorite === 'important' ? 'Important' : 'Info'}
                                  </span>
                                  {!notif.lue && (
                                    <span className="h-2 w-2 bg-blue-500 rounded-full"></span>
                                  )}
                                </div>
                                <h4 className="text-sm font-semibold text-gray-900 dark:text-white mb-1">
                                  {notif.titre}
                                </h4>
                                <p className="text-xs text-gray-600 dark:text-gray-400 mb-2">
                                  {notif.message}
                                </p>
                                <p className="text-xs text-gray-500 dark:text-gray-500">
                                  {new Date(notif.date_creation).toLocaleDateString('fr-CA', {
                                    day: 'numeric',
                                    month: 'short',
                                    hour: '2-digit',
                                    minute: '2-digit'
                                  })}
                                </p>
                              </div>
                              {!notif.lue && (
                                <button
                                  onClick={(e) => {
                                    e.stopPropagation()
                                    handleMarkAsRead(notif.id_notification)
                                  }}
                                  className="ml-2 p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                                  title="Marquer comme lu"
                                >
                                  <CheckCircle className="h-4 w-4" />
                                </button>
                              )}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Footer */}
                  {notifications.length > 0 && (
                    <div className="p-3 border-t border-gray-200 dark:border-gray-700 text-center">
                      <Link
                        to="/settings"
                        onClick={() => setShowNotifications(false)}
                        className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-800 dark:hover:text-blue-300"
                      >
                        Voir tout l'historique
                      </Link>
                    </div>
                  )}
                </div>
              )}
            </div>
          )}

          {/* User menu */}
          <div className="relative">
            <div className="flex items-center space-x-2 lg:space-x-3">
              {user && (
                <div className="text-right hidden lg:block">
                  <div className="text-sm font-medium text-gray-900 dark:text-white">
                    {user.prenom} {user.nom}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400">{user.email}</div>
                </div>
              )}
              <button 
                onClick={() => setShowUserMenu(!showUserMenu)}
                className="flex items-center p-2 rounded-full text-gray-400 dark:text-gray-500 hover:text-gray-500 dark:hover:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700"
              >
                <User className="h-6 w-6 lg:h-8 lg:w-8" />
              </button>
            </div>

            {/* Dropdown menu */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 py-1 z-50">
                <div className="px-4 py-2 border-b border-gray-200 dark:border-gray-700">
                  <p className="text-sm font-medium text-gray-900 dark:text-white">
                    {user?.prenom} {user?.nom}
                  </p>
                  <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user?.email}</p>
                </div>
                
                <Link
                  to="/settings"
                  onClick={() => setShowUserMenu(false)}
                  className="flex items-center px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <UserCircle className="h-4 w-4 mr-2" />
                  Mon profil
                </Link>
                
                <button
                  onClick={handleLogout}
                  className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20"
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