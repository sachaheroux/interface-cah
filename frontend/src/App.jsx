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
import Suppliers from './pages/Suppliers'
import Materials from './pages/Materials'
import Projects from './pages/Projects'
import InvoicesST from './pages/InvoicesST'
import Documents from './pages/Documents'
import Settings from './pages/Settings'
import Reports from './pages/Reports'
import UnitReportDetails from './pages/UnitReportDetails'
import Login from './pages/Login'
import Register from './pages/Register'
import CompanySetup from './pages/CompanySetup'
import PendingApproval from './pages/PendingApproval'
import EmployeePunchMobile from './pages/EmployeePunchMobile'
import PunchManagement from './pages/PunchManagement'

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
  const [userRole, setUserRole] = React.useState(null)
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
          setUserRole(userData.user.role)
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

// Composant pour protéger les routes admin
function AdminProtectedRoute({ children }) {
  const [userRole, setUserRole] = React.useState(null)
  const [loading, setLoading] = React.useState(true)
  
  React.useEffect(() => {
    const checkUserRole = async () => {
      try {
        const token = localStorage.getItem('auth_token')
        if (!token) {
          setLoading(false)
          return
        }
        
        const response = await fetch('https://interface-cah-backend.onrender.com/api/auth/me', {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        })
        
        if (response.ok) {
          const userData = await response.json()
          setUserRole(userData.user.role)
        } else {
          setUserRole('invalid')
        }
      } catch (error) {
        console.error('Erreur vérification rôle:', error)
        setUserRole('error')
      } finally {
        setLoading(false)
      }
    }
    
    checkUserRole()
  }, [])
  
  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Vérification des permissions...</p>
        </div>
      </div>
    )
  }
  
  if (userRole !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <h1 className="text-2xl font-bold text-red-600 mb-4">Accès refusé</h1>
          <p className="text-gray-600">Cette section est réservée aux administrateurs.</p>
          <button 
            onClick={() => window.location.href = '/employees'}
            className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retour aux Employés
          </button>
        </div>
      </div>
    )
  }
  
  return children
}

function AppContent() {
  const location = useLocation()
  const showSecondarySidebar = location.pathname !== '/' && location.pathname !== '/login'
  const isAuthPage = location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/setup-company' || location.pathname === '/pending-approval'

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
            <Route path="/" element={<ProtectedRoute><AdminProtectedRoute><Dashboard /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/buildings" element={<ProtectedRoute><AdminProtectedRoute><Buildings /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/buildings/analysis" element={<ProtectedRoute><AdminProtectedRoute><ProfitabilityAnalysis /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/buildings/mortgage" element={<ProtectedRoute><AdminProtectedRoute><MortgageAnalysis /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/buildings/property-analysis" element={<ProtectedRoute><AdminProtectedRoute><PropertyAnalysis /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/tenants" element={<ProtectedRoute><AdminProtectedRoute><Tenants /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/leases" element={<ProtectedRoute><AdminProtectedRoute><Leases /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/rent-payments" element={<ProtectedRoute><AdminProtectedRoute><RentPayments /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/transactions" element={<ProtectedRoute><AdminProtectedRoute><Transactions /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/employees" element={<ProtectedRoute><StatusProtectedRoute><Employees /></StatusProtectedRoute></ProtectedRoute>} />
            <Route path="/employee-punch" element={<ProtectedRoute><StatusProtectedRoute><EmployeePunchMobile /></StatusProtectedRoute></ProtectedRoute>} />
            <Route path="/punch-management" element={<ProtectedRoute><AdminProtectedRoute><PunchManagement /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/contractors" element={<ProtectedRoute><AdminProtectedRoute><Contractors /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/suppliers" element={<ProtectedRoute><AdminProtectedRoute><Suppliers /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/materials" element={<ProtectedRoute><AdminProtectedRoute><Materials /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/projects" element={<ProtectedRoute><AdminProtectedRoute><Projects /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/invoices-st" element={<ProtectedRoute><AdminProtectedRoute><InvoicesST /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/documents" element={<ProtectedRoute><AdminProtectedRoute><Documents /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><AdminProtectedRoute><Settings /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/reports" element={<ProtectedRoute><AdminProtectedRoute><Reports /></AdminProtectedRoute></ProtectedRoute>} />
            <Route path="/unit-reports/:unitId/:year" element={<ProtectedRoute><AdminProtectedRoute><UnitReportDetails /></AdminProtectedRoute></ProtectedRoute>} />
            
            {/* Route catch-all : rediriger vers login pour toutes les routes non définies */}
            <Route path="*" element={<Navigate to="/login" replace />} />
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