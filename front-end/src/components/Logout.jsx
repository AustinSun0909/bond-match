import React from 'react';
import { useAuth } from '../context/AuthContext';

const Logout = () => {
  const { logout } = useAuth();

  const handleLogout = () => {
    console.log('Logout button clicked');
    
    try {
      // Call the logout function from AuthContext
      // The auth.js logout function already handles redirection
      logout();
      console.log('Logout successful');
    } catch (error) {
      console.error('Error during logout:', error);
    }
  };

  return (
    <button 
      onClick={handleLogout}
      className="bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
    >
      Logout
    </button>
  );
};

export default Logout; 