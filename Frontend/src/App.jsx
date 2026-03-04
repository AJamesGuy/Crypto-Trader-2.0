import { BrowserRouter, Routes, Route, Navigate, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './context/AuthContext';
import NavBar from './components/NavBar/NavBar';
import DashNavBar from './components/DashNavBar/DashNavBar';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Dashboard from './pages/Dashboard';
import Trade from './pages/Trade';
import Portfolio from './pages/Portfolio';
import Settings from './pages/Settings';

const NavBarWrapper = () => {
  const location = useLocation();
  const { user } = useAuth();
  
  // Show DashNavBar for protected routes, NavBar for auth routes
  if (user && ['/dashboard', '/trade', '/portfolio', '/settings'].includes(location.pathname)) { // includes method checks if the current path is one of the protected routes
    return <DashNavBar />;
  }
  return <NavBar />;
};

const Protected = ({ children }) => { // This component checks if the user is authenticated before rendering the protected route
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" replace />;
};

function App() {
  return (
    <AuthProvider> 
      <BrowserRouter> 
          <NavBarWrapper /> 
            <Routes>
              <Route path="/login" element={<Login />} />
              <Route path="/signup" element={<Signup />} />
              <Route path="/dashboard" element={<Protected><Dashboard /></Protected>} />
              <Route path="/trade" element={<Protected><Trade /></Protected>} />
              <Route path="/portfolio" element={<Protected><Portfolio /></Protected>} />
              <Route path="/settings" element={<Protected><Settings /></Protected>} />
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="*" element={<Navigate to="/dashboard" replace />} />
            </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}

export default App;