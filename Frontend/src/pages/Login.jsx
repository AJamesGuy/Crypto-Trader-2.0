import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'
import { authAPI } from '../services/api'
import LoginPortal from '../components/LoginPortal/LoginPortal'
import "../styles/Login.css"

const Login = () => {
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')
    const [loading, setLoading] = useState(false)
    const navigate = useNavigate()
    const { login } = useAuth()

    const handleLogin = async (e) => {
        e.preventDefault()
        setLoading(true)
        setError('')

        try {
            const data = await authAPI.login(username, password)
            login(data.token, data.user)
            navigate('/dashboard')
        } catch (err) {
            setError(err.message || 'Login failed')
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="login-page">
            <LoginPortal
                onSubmit={handleLogin}
                email={username}
                setEmail={setUsername}
                password={password}
                setPassword={setPassword}
                error={error}
                loading={loading}
                />
        </div>
    )
}

export default Login