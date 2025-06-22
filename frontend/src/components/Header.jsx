import React from 'react'
import { Menu, Bell, User } from 'lucide-react'

export default function Header({ setSidebarOpen }) {
  return (
    <header className="bg-white shadow-sm border-b border-gray-200 lg:ml-64">
      <div className="flex items-center justify-between h-16 px-4 sm:px-6 lg:px-8">
        {/* Mobile menu button */}
        <button
          onClick={() => setSidebarOpen(true)}
          className="lg:hidden p-2 rounded-md text-gray-400 hover:text-gray-500 hover:bg-gray-100"
        >
          <Menu className="h-6 w-6" />
        </button>

        {/* Page title - will be dynamic later */}
        <div className="hidden lg:block">
          <h1 className="text-2xl font-semibold text-gray-900">Tableau de bord</h1>
        </div>

        {/* Right side */}
        <div className="flex items-center space-x-4">
          {/* Notifications */}
          <button className="p-2 rounded-full text-gray-400 hover:text-gray-500 hover:bg-gray-100 relative">
            <Bell className="h-6 w-6" />
            {/* Notification badge */}
            <span className="absolute top-0 right-0 block h-2 w-2 rounded-full bg-red-400 ring-2 ring-white"></span>
          </button>

          {/* User menu */}
          <div className="flex items-center space-x-3">
            <div className="hidden md:block text-right">
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