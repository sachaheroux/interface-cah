import React from 'react'
// Test deploiement - ligne propre
import { BrowserRouter as Router, Routes, Route, useLocation } from 'react-router-dom'
import TopNavigation from './components/TopNavigation'
import SecondarySidebar from './components/SecondarySidebar'
import './utils/cleanupMigration'
import Dashboard from './pages/Dashboard'
import Buildings from './pages/Buildings'
import Tenants from './pages/Tenants'
import Leases from './pages/Leases'
import Maintenance from './pages/Maintenance'
import Billing from './pages/Billing'
import Employees from './pages/Employees'
import Contractors from './pages/Contractors'
import Projects from './pages/Projects'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Reports from './pages/Reports'
import UnitReportDetails from './pages/UnitReportDetails'

function AppContent() {
  const location = useLocation()
  const showSecondarySidebar = location.pathname !== '/'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation horizontale fixe en haut */}
      <TopNavigation />
      
      
      {/* Contenu principal */}
      <div className="flex pt-20 sm:pt-16">
        {/* Sidebar secondaire conditionnelle */}
        <SecondarySidebar />
        
        {/* Zone de contenu principal */}
        <main className={`flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-3 lg:p-6 ${
          showSecondarySidebar ? 'md:ml-48 lg:ml-64' : ''
        }`}>
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/buildings" element={<Buildings />} />
            <Route path="/tenants" element={<Tenants />} />
            <Route path="/leases" element={<Leases />} />
            <Route path="/billing" element={<Billing />} />
            <Route path="/employees" element={<Employees />} />
            <Route path="/contractors" element={<Contractors />} />
            <Route path="/projects" element={<Projects />} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/settings" element={<Settings />} />
            <Route path="/reports" element={<Reports />} />
            <Route path="/unit-reports/:unitId/:year" element={<UnitReportDetails />} />
          </Routes>
        </main>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App 