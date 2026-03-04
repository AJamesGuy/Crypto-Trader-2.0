import { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import SignUpForm from '../components/SignUpForm/SignUpForm'
import { authAPI } from '../services/api'
import "../styles/SignUp.css"


const Signup = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        password_confirm: ''
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    const handleSignUp = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (formData.password !== formData.password_confirm) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        try {
            await authAPI.signup(
                formData.username,
                formData.email,
                formData.password,
                formData.password_confirm
            );

            // Redirect to login page after successful signup
            navigate('/login', { state: { message: 'Signup successful! Please log in.' } });
        } catch (err) {
            setError(err.message || 'Signup failed');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prev => ({ ...prev, [name]: value }));
    };

  return (
    <div className='signup'>
        <SignUpForm
            formData={formData}
            onChange={handleChange}
            onSubmit={handleSignUp}
            error={error}
            loading={loading}
        />
        <p className='login-link'>Already have an account? <Link to="/login" className='link'>Login here</Link></p>
    </div>
  );
}

export default Signup