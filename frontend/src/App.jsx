import React, { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Dashboard from './pages/Dashboard'
import Buildings from './pages/Buildings'
import Tenants from './pages/Tenants'
import Maintenance from './pages/Maintenance'
import Billing from './pages/Billing'
import Employees from './pages/Employees'
import Contractors from './pages/Contractors'
import Projects from './pages/Projects'
import Documents from './pages/Documents'
import Settings from './pages/Settings'

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false)

  return (
    <Router>
      <div className="flex h-screen bg-gray-50">
        {/* Sidebar */}
        <Sidebar sidebarOpen={sidebarOpen} setSidebarOpen={setSidebarOpen} />
        
        {/* Main content */}
        <div className="flex-1 flex flex-col overflow-hidden">
          {/* Header */}
          <Header setSidebarOpen={setSidebarOpen} />
          
          {/* Page content */}
          <main className="flex-1 overflow-x-hidden overflow-y-auto bg-gray-50 p-6">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/buildings" element={<Buildings />} />
              <Route path="/tenants" element={<Tenants />} />
              <Route path="/maintenance" element={<Maintenance />} />
              <Route path="/billing" element={<Billing />} />
              <Route path="/employees" element={<Employees />} />
              <Route path="/contractors" element={<Contractors />} />
              <Route path="/projects" element={<Projects />} />
              <Route path="/documents" element={<Documents />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </main>
        </div>
      </div>
    </Router>
  )
}

export default App 