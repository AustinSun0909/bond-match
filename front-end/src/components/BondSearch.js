import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchHistory from './SearchHistory.jsx';
import { logout } from '../services/auth';
import './BondSearch.css';

const BondSearch = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  // Load search history from localStorage on component mount
  useEffect(() => {
    const savedHistory = localStorage.getItem('bondSearchHistory');
    if (savedHistory) {
      setSearchHistory(JSON.parse(savedHistory));
    }
  }, []);

  // Save search history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('bondSearchHistory', JSON.stringify(searchHistory));
  }, [searchHistory]);

  const handleSearch = async (query = searchQuery) => {
    setLoading(true);
    setError(null);

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Mock results for development
      const mockResults = Array(5).fill().map((_, i) => ({
        id: i + 1,
        name: `Bond ${i + 1}`,
        issuer: `Issuer ${i + 1}`,
        yield: `${(Math.random() * 5 + 2).toFixed(2)}%`,
        maturity: new Date(Date.now() + Math.random() * 365 * 24 * 60 * 60 * 1000).toLocaleDateString()
      }));

      setSearchResults(mockResults);

      // Add to search history
      const newSearch = {
        query,
        timestamp: new Date().toISOString(),
        resultCount: mockResults.length
      };

      setSearchHistory(prev => {
        const newHistory = [newSearch, ...prev];
        // Keep only the last 50 searches
        return newHistory.slice(0, 50);
      });
    } catch (err) {
      setError('Failed to fetch search results');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      handleSearch();
    }
  };

  const handleHistorySearch = (search) => {
    setSearchQuery(search.query);
    handleSearch(search.query);
  };

  return (
    <div className="bond-search">
      <div className="header-actions">
        <button onClick={handleLogout} className="logout-button">
          Logout
        </button>
      </div>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search bonds..."
            className="search-input"
          />
          <button
            type="submit"
            disabled={loading || !searchQuery.trim()}
            className="search-button"
          >
            {loading ? 'Searching...' : 'Search'}
          </button>
        </div>
      </form>

      {error && <div className="error-message">{error}</div>}

      {searchResults.length > 0 && (
        <div className="search-results">
          <h2>Search Results</h2>
          <table className="results-table">
            <thead>
              <tr>
                <th>Name</th>
                <th>Issuer</th>
                <th>Yield</th>
                <th>Maturity</th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map((bond) => (
                <tr key={bond.id}>
                  <td>{bond.name}</td>
                  <td>{bond.issuer}</td>
                  <td>{bond.yield}</td>
                  <td>{bond.maturity}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <SearchHistory
        searches={searchHistory}
        onSearch={handleHistorySearch}
      />
    </div>
  );
};

export default BondSearch; 