import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI, settingsAPI } from '../services/api'
import "../styles/Settings.css"

const Settings = () => {
  const { user, token, logout } = useAuth()
  const navigate = useNavigate()

  const [profile, setProfile] = useState(null)
  const [loading, setLoading] = useState(true)
  const [message, setMessage] = useState('')
  const [activeTab, setActiveTab] = useState('profile')

  // Profile form state
  const [profileForm, setProfileForm] = useState({ username: '', email: '' })

  // Password form state
  const [passwordForm, setPasswordForm] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  })

  // Account deletion state
  const [deletePassword, setDeletePassword] = useState('')
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false)

  useEffect(() => {
    if (!user?.id || !token) return

    const fetchProfile = async () => {
      try {
        const data = await authAPI.getProfile(user.id)
        setProfile(data)
        setProfileForm({
          username: data.username || '',
          email: data.email || ''
        })
      } catch (err) {
        console.error('Error fetching profile:', err)
        setMessage('Error loading profile')
      } finally {
        setLoading(false)
      }
    }

    fetchProfile()
  }, [user?.id, token])

  const handleProfileUpdate = async (e) => {
    e.preventDefault()
    setMessage('')
    setLoading(true)

    try {
      const response = await settingsAPI.updateProfile(user.id, profileForm)
      setMessage('Profile updated successfully!')
      setProfile(response)
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to update profile'}`)
    } finally {
      setLoading(false)
    }
  }

  const handlePasswordChange = async (e) => {
    e.preventDefault()
    setMessage('')

    if (passwordForm.new_password !== passwordForm.confirm_password) {
      setMessage('New passwords do not match')
      return
    }

    setLoading(true)
    try {
      await settingsAPI.changePassword(user.id, {
        currentPassword: passwordForm.current_password,
        newPassword: passwordForm.new_password,
        confirmPassword: passwordForm.confirm_password
      })
      setMessage('Password changed successfully!')
      setPasswordForm({
        current_password: '',
        new_password: '',
        confirm_password: ''
      })
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to change password'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleResetBalance = async () => {
    if (!window.confirm('Are you sure you want to reset your balance? This action cannot be undone.')) {
      return
    }

    setLoading(true)
    try {
      await settingsAPI.resetBalance(user.id)
      setMessage('Balance reset successfully!')
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to reset balance'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleDeleteAccount = async () => {
    if (!deletePassword) {
      setMessage('Please enter your password to confirm')
      return
    }

    setLoading(true)
    try {
      await settingsAPI.deleteAccount(user.id, {
        password: deletePassword,
        confirm: true
      })
      setMessage('Account deleted successfully. Logging out...')
      setTimeout(() => {
        logout()
        navigate('/login')
      }, 2000)
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to delete account'}`)
    } finally {
      setLoading(false)
    }
  }

  if (loading && !profile) return <p>Loading settings...</p>

  return (
    <div className="settings-container">
      <h1>Settings</h1>

      {message && (
        <div className={`message ${message.includes('Error') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}
    <div className="settings-container-2">

      <div className="settings-tabs">
        <button
          className={`tab ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profile
        </button>
        <button
          className={`tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => setActiveTab('security')}
        >
          Security
        </button>
        <button
          className={`tab ${activeTab === 'danger' ? 'active' : ''}`}
          onClick={() => setActiveTab('danger')}
        >
          Danger Zone
        </button>
      </div>

      {activeTab === 'profile' && profile && (
        <div className="settings-section profile-section">
          <h2>Profile Settings</h2>
          <form onSubmit={handleProfileUpdate} className="settings-form">
            <div className="form-group">
              <label htmlFor="username">Username:</label>
              <input
                type="text"
                id="username"
                value={profileForm.username}
                onChange={(e) =>
                  setProfileForm({ ...profileForm, username: e.target.value })
                }
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email:</label>
              <input
                type="email"
                id="email"
                value={profileForm.email}
                onChange={(e) =>
                  setProfileForm({ ...profileForm, email: e.target.value })
                }
                required
              />
            </div>

            <button type="submit" disabled={loading} className="submit-btn">
              {loading ? 'Updating...' : 'Update Profile'}
            </button>
          </form>
        </div>
      )}

      {activeTab === 'security' && (
        <div className="settings-section security-section">
          <h2>Security Settings</h2>

          <div className="subsection">
            <h3>Change Password</h3>
            <form onSubmit={handlePasswordChange} className="settings-form">
              <div className="form-group">
                <label htmlFor="current_password">Current Password:</label>
                <input
                  type="password"
                  id="current_password"
                  value={passwordForm.current_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      current_password: e.target.value
                    })
                  }
                  required
                />
              </div>

              <div className="form-group">
                <label htmlFor="new_password">New Password:</label>
                <input
                  type="password"
                  id="new_password"
                  value={passwordForm.new_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      new_password: e.target.value
                    })
                  }
                  required
                  minLength="8"
                />
              </div>

              <div className="form-group">
                <label htmlFor="confirm_password">Confirm New Password:</label>
                <input
                  type="password"
                  id="confirm_password"
                  value={passwordForm.confirm_password}
                  onChange={(e) =>
                    setPasswordForm({
                      ...passwordForm,
                      confirm_password: e.target.value
                    })
                  }
                  required
                  minLength="8"
                />
              </div>

              <button type="submit" disabled={loading} className="submit-btn">
                {loading ? 'Changing...' : 'Change Password'}
              </button>
            </form>
          </div>

          <div className="subsection">
            <h3>Reset Balance</h3>
            <p>Reset your account balance to starting amount.</p>
            <button
              onClick={handleResetBalance}
              disabled={loading}
              className="reset-btn"
            >
              Reset Balance
            </button>
          </div>
        </div>
      )}

      {activeTab === 'danger' && (
        <div className="settings-section danger-section">
          <h2>Danger Zone</h2>

          <div className="subsection danger">
            <h3>Delete Account</h3>
            <p className="warning">
              ⚠️ This action is permanent and cannot be undone. All your data will be
              deleted.
            </p>

            {!showDeleteConfirm ? (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="delete-btn danger"
              >
                Delete My Account
              </button>
            ) : (
              <div className="delete-confirm-form">
                <p>
                  Are you sure? This will permanently delete your account and all associated data.
                </p>
                <div className="form-group">
                  <label htmlFor="delete_password">
                    Enter your password to confirm:
                  </label>
                  <input
                    type="password"
                    id="delete_password"
                    value={deletePassword}
                    onChange={(e) => setDeletePassword(e.target.value)}
                    placeholder="Enter your password"
                    required
                  />
                </div>
                <div className="button-group">
                  <button
                    onClick={handleDeleteAccount}
                    disabled={loading}
                    className="delete-btn danger"
                  >
                    {loading ? 'Deleting...' : 'Yes, Delete My Account'}
                  </button>
                  <button
                    onClick={() => {
                      setShowDeleteConfirm(false)
                      setDeletePassword('')
                    }}
                    className="cancel-btn"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
</div>
  )
}

export default Settings