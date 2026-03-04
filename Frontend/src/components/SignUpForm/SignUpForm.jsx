import "./SignUpForm.css"

const SignUpForm = ({ formData, onChange, onSubmit, error, loading }) => {
  return (
    <div className="signup">
    <form onSubmit={onSubmit} className="signup-form">
      <div>
        <label htmlFor="username">Username:</label>
        <input
          type="text"
          id="username"
          name="username"
          value={formData.username}
          onChange={onChange}
          minLength="3"
          required
        />
      </div>
      <div>
        <label htmlFor="email">Email:</label>
        <input
          type="email"
          id="email"
          name="email"
          value={formData.email}
          onChange={onChange}
          required
        />
      </div>
      <div>
        <label htmlFor="password">Password:</label>
        <input
          type="password"
          id="password"
          name="password"
          value={formData.password}
          onChange={onChange}
          minLength="8"
          required
        />
      </div>
      <div>
        <label htmlFor="password_confirm">Confirm Password:</label>
        <input
          type="password"
          id="password_confirm"
          name="password_confirm"
          value={formData.password_confirm}
          onChange={onChange}
          minLength="8"
          required
        />
      </div>
      {error && <p className="error">{error}</p>}
      <button type="submit" disabled={loading}>
        {loading ? 'Signing Up...' : 'Sign Up'}
      </button>
    </form>
    </div>
  );
}

export default SignUpForm