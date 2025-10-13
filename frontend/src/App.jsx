import React from 'react'
// Test deploiement - ligne propre
import { BrowserRouter as Router, Routes, Route, useLocation, Navigate } from 'react-router-dom'
import TopNavigation from './components/TopNavigation'
import SecondarySidebar from './components/SecondarySidebar'
import './utils/cleanupMigration'
import Dashboard from './pages/Dashboard'
import Buildings from './pages/Buildings'
import Tenants from './pages/Tenants'
import Leases from './pages/Leases'
import RentPayments from './pages/RentPayments'
import Transactions from './pages/Transactions'
import ProfitabilityAnalysis from './pages/ProfitabilityAnalysis'
import MortgageAnalysis from './pages/MortgageAnalysis'
import PropertyAnalysis from './pages/PropertyAnalysis'
import Maintenance from './pages/Maintenance'
import Employees from './pages/Employees'
import Contractors from './pages/Contractors'
import Projects from './pages/Projects'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Reports from './pages/Reports'
import UnitReportDetails from './pages/UnitReportDetails'
import Login from './pages/Login'
import Register from './pages/Register'

// Composant pour protéger les routes (authentification requise)
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('auth_token')
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

function AppContent() {
  const location = useLocation()
  const showSecondarySidebar = location.pathname !== '/' && location.pathname !== '/login'
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register'

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation horizontale fixe en haut (sauf pages auth) */}
      {!isAuthPage && <TopNavigation />}
      
      
      {/* Contenu principal */}
      <div className={`flex ${!isAuthPage ? 'pt-20 sm:pt-16' : ''}`}>
        {/* Sidebar secondaire conditionnelle */}
        {!isAuthPage && <SecondarySidebar />}
        
        {/* Zone de contenu principal */}
        <main className={`flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 ${
          isAuthPage ? '' : 'p-3 lg:p-6'
        } ${
          showSecondarySidebar ? 'md:ml-48 lg:ml-64' : ''
        }`}>
          <Routes>
            {/* Pages publiques */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            
            {/* Pages protégées */}
            <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/buildings" element={<ProtectedRoute><Buildings /></ProtectedRoute>} />
            <Route path="/buildings/analysis" element={<ProtectedRoute><ProfitabilityAnalysis /></ProtectedRoute>} />
            <Route path="/buildings/mortgage" element={<ProtectedRoute><MortgageAnalysis /></ProtectedRoute>} />
            <Route path="/buildings/property-analysis" element={<ProtectedRoute><PropertyAnalysis /></ProtectedRoute>} />
            <Route path="/tenants" element={<ProtectedRoute><Tenants /></ProtectedRoute>} />
            <Route path="/leases" element={<ProtectedRoute><Leases /></ProtectedRoute>} />
            <Route path="/rent-payments" element={<ProtectedRoute><RentPayments /></ProtectedRoute>} />
            <Route path="/transactions" element={<ProtectedRoute><Transactions /></ProtectedRoute>} />
            <Route path="/employees" element={<ProtectedRoute><Employees /></ProtectedRoute>} />
            <Route path="/contractors" element={<ProtectedRoute><Contractors /></ProtectedRoute>} />
            <Route path="/projects" element={<ProtectedRoute><Projects /></ProtectedRoute>} />
            <Route path="/documents" element={<ProtectedRoute><Documents /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="/reports" element={<ProtectedRoute><Reports /></ProtectedRoute>} />
            <Route path="/unit-reports/:unitId/:year" element={<ProtectedRoute><UnitReportDetails /></ProtectedRoute>} />
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