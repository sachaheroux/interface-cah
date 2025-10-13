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
import CompanySetup from './pages/CompanySetup'
import PendingApproval from './pages/PendingApproval'

// Composant pour protéger les routes (authentification requise)
function ProtectedRoute({ children }) {
  const token = localStorage.getItem('auth_token')
  
  if (!token) {
    return <Navigate to="/login" replace />
  }
  
  return children
}

// Composant pour vérifier le statut de l'utilisateur
function StatusProtectedRoute({ children }) {
  const [userStatus, setUserStatus] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  
  React.useEffect(() => {
    const checkUserStatus = async () => {
      try {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          setLoading(false)
          return
        }
        
        // Appeler l'API pour vérifier le statut de l'utilisateur
        const response = await fetch('https://interface-cah-backend.onrender.com/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const userData = await response.json()
          setUserStatus(userData.user.statut)
        } else {
          // Token invalide, rediriger vers login
          localStorage.removeItem('auth_token')
          setUserStatus('invalid')
        }
      } catch (error) {
        console.error('Erreur vérification statut:', error)
        setUserStatus('error')
      } finally {
        setLoading(false)
      }
    }
    
    checkUserStatus()
  }, [])
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification du statut...</p>
        </div>
      </div>
    )
  }
  
  if (userStatus === 'invalid' || userStatus === 'error') {
    return <Navigate to="/login" replace />
  }
  
  if (userStatus === 'en_attente') {
    return <Navigate to="/pending-approval" replace />
  }
  
  if (userStatus === 'refuse') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Accès refusé</h1>
          <p className="text-gray-600">Votre demande d'accès a été refusée.</p>
        </div>
      </div>
    )
  }
  
  if (userStatus === 'inactif') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Compte inactif</h1>
          <p className="text-gray-600">Votre compte a été désactivé.</p>
        </div>
      </div>
    )
  }
  
  // Statut 'actif' - autoriser l'accès
  return children
}

function AppContent() {
  const location = useLocation()
  const showSecondarySidebar = location.pathname !== '/' && location.pathname !== '/login'
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/setup-company'

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
            <Route path="/setup-company" element={<CompanySetup />} />
            <Route path="/pending-approval" element={<PendingApproval />} />
            
            {/* Pages protégées */}
            <Route path="/" element={<StatusProtectedRoute><Dashboard /></StatusProtectedRoute>} />
            <Route path="/buildings" element={<StatusProtectedRoute><Buildings /></StatusProtectedRoute>} />
            <Route path="/buildings/analysis" element={<StatusProtectedRoute><ProfitabilityAnalysis /></StatusProtectedRoute>} />
            <Route path="/buildings/mortgage" element={<StatusProtectedRoute><MortgageAnalysis /></StatusProtectedRoute>} />
            <Route path="/buildings/property-analysis" element={<StatusProtectedRoute><PropertyAnalysis /></StatusProtectedRoute>} />
            <Route path="/tenants" element={<StatusProtectedRoute><Tenants /></StatusProtectedRoute>} />
            <Route path="/leases" element={<StatusProtectedRoute><Leases /></StatusProtectedRoute>} />
            <Route path="/rent-payments" element={<StatusProtectedRoute><RentPayments /></StatusProtectedRoute>} />
            <Route path="/transactions" element={<StatusProtectedRoute><Transactions /></StatusProtectedRoute>} />
            <Route path="/employees" element={<StatusProtectedRoute><Employees /></StatusProtectedRoute>} />
            <Route path="/contractors" element={<StatusProtectedRoute><Contractors /></StatusProtectedRoute>} />
            <Route path="/projects" element={<StatusProtectedRoute><Projects /></StatusProtectedRoute>} />
            <Route path="/documents" element={<StatusProtectedRoute><Documents /></StatusProtectedRoute>} />
            <Route path="/settings" element={<StatusProtectedRoute><Settings /></StatusProtectedRoute>} />
            <Route path="/reports" element={<StatusProtectedRoute><Reports /></StatusProtectedRoute>} />
            <Route path="/unit-reports/:unitId/:year" element={<StatusProtectedRoute><UnitReportDetails /></StatusProtectedRoute>} />
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