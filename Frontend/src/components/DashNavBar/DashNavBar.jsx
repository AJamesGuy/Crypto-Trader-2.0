import React from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'
import './DashNavBar.css'

const DashNavBar = () => {
  const { user, logout } = useAuth()
  const location = useLocation()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

  const isActive = (path) => location.pathname === path

  return (
    <nav className="dash-navbar">
      <div className="nav-brand">
        <Link to="/dashboard" className="brand-logo">
          🪙 CryptoTemple
        </Link>
      </div>

      <div className="nav-links">
        <Link
          to="/dashboard"
          className={`nav-link ${isActive('/dashboard') ? 'active' : ''}`}
        >
          Dashboard
        </Link>
        <Link
          to="/trade"
          className={`nav-link ${isActive('/trade') ? 'active' : ''}`}
        >
          Trade
        </Link>
        <Link
          to="/portfolio"
          className={`nav-link ${isActive('/portfolio') ? 'active' : ''}`}
        >
          Portfolio
        </Link>
        <Link
          to="/settings"
          className={`nav-link ${isActive('/settings') ? 'active' : ''}`}
        >
          Settings
        </Link>
      </div>

      <div className="nav-user">
        <span className="user-name">{user?.username}</span>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>
    </nav>
  )
}

export default DashNavBar