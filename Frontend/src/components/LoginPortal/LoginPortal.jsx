import React from 'react'
import "./LoginPortal.css"

const LoginPortal = ({ onSubmit, email, setEmail, password, setPassword, error, loading }) => {

  return (
    <div className='login'>
    <form onSubmit={onSubmit} className='login-form'>
      <h1>CryptoTemple</h1>
      <div>
        <label htmlFor="email">Email/Username:</label>
        <input
          type="text"
          id="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
          />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
          />
      </div>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Logging in...' : 'Login'}
      </button>
    </form>
    </div>
  )
}

export default LoginPortal