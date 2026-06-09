import React, { useState } from 'react';
import { authAPI } from '../api/client';

function Login({ onLogin }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [registrationSuccess, setRegistrationSuccess] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    e.stopPropagation(); 
    
    console.log('Form submitted');
    
    setRegistrationSuccess(false);
    
    if (!isLogin && password.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    
    setLoading(true);

    try {
      if (isLogin) {
        const response = await authAPI.login(email, password);
        const { access_token, user } = response.data;
        localStorage.setItem('access_token', access_token);
        localStorage.setItem('user', JSON.stringify(user));
        onLogin(user);
      } else {
        await authAPI.register(email, password, fullName);
        setRegistrationSuccess(true);
        setError('');
        setEmail('');
        setPassword('');
        setFullName('');
        setTimeout(() => {
          setIsLogin(true);
          setRegistrationSuccess(false);
        }, 3000);
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Authentication failed';
      setError(errorMessage);
      console.log('Error set:', errorMessage);
    } finally {
      setLoading(false);
    }
    
    return false; 
  };

  const handleToggleMode = () => {
    setIsLogin(!isLogin);
    setError('');
    setRegistrationSuccess(false);
  };

  return (
    <div className="login-container">
      <div className="login-card">
        <h2>{isLogin ? 'Sign In' : 'Create Account'}</h2>
        
        {registrationSuccess && (
          <div className="success-alert" style={{ marginBottom: '15px' }}>
            ✓ Registration successful! Redirecting to login...
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="login-form">
          {!isLogin && (
            <div className="form-group">
              <label>Full Name</label>
              <input
                type="text"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                required
                placeholder="Enter your full name"
              />
            </div>
          )}
          
          <div className="form-group">
            <label>Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              placeholder="Enter your email"
            />
          </div>
          
          <div className="form-group">
            <label>Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              placeholder="Enter your password (min 6 characters)"
            />
            {isLogin && (
              <small style={{ fontSize: '12px', color: '#6b7280', marginTop: '4px', display: 'block' }}>
                Demo admin: admin@techkraft.com / Admin123!
              </small>
            )}
          </div>

          {error && (
            <div className="error-alert" style={{ marginBottom: '15px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span> {error}</span>
                <button 
                  type="button"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    setError('');
                  }}
                  style={{ 
                    background: 'none', 
                    border: 'none', 
                    color: '#991b1b', 
                    cursor: 'pointer', 
                    fontSize: '18px',
                    fontWeight: 'bold',
                    marginLeft: '10px'
                  }}
                >
                  ✕
                </button>
              </div>
            </div>
          )}

          <button 
            type="submit" 
            className="btn-primary" 
            disabled={loading || registrationSuccess}
            style={{ width: '100%' }}
          >
            {loading ? 'Loading...' : (isLogin ? 'Sign In' : 'Register')}
          </button>
        </form>
        
        <div className="auth-toggle">
          {isLogin ? "Don't have an account? " : "Already have an account? "}
          <button 
            type="button"
            onClick={handleToggleMode} 
            disabled={registrationSuccess}
          >
            {isLogin ? 'Register' : 'Sign In'}
          </button>
        </div>
      </div>
    </div>
  );
}

export default Login;