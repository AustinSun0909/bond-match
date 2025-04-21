import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchHistory from './SearchHistory.jsx';
import { useAuth } from '../context/AuthContext';
import { searchBonds, getSearchHistory, matchBond } from '../services/bondService';
import './BondSearch.css';

const BondSearch = ({ showHistory = false }) => {
  const navigate = useNavigate();
  const { logout } = useAuth();
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [matchResults, setMatchResults] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState(null);
  const searchHistoryRef = useRef(null);

  const handleLogout = () => {
    console.log('BondSearch: Logout button clicked');
    // Let the auth.js logout function handle the redirection
    logout();
  };

  const handleReturn = () => {
    navigate('/dashboard');
  };

  // Define handleSearch function first
  const handleSearch = async (query = searchQuery) => {
    if (!query) {
      setError('请输入搜索内容');
      return;
    }
    
    if (!query.trim() || query.trim().length < 2) {
      setError('请输入至少2个字符进行搜索');
      return;
    }

    setLoading(true);
    setError(null);
    // Clear any previous match results when performing a new search
    setMatchResults(null);

    try {
      const results = await searchBonds(query.trim());
      setSearchResults(results);

      // Get bond name from the first result if available
      let bondName = '';
      if (results.length > 0) {
        bondName = results[0].bond_name || '';
      }

      // Add to search history locally (will also be saved on backend)
      const newSearch = {
        query,
        bondName,
        timestamp: new Date().toISOString(),
        resultCount: results.length
      };

      // Update state
      setSearchHistory(prev => {
        // Check if the same query already exists
        const existingIndex = prev.findIndex(item => item.query === query);
        
        let newHistory;
        if (existingIndex !== -1) {
          // Update existing search with new timestamp and details
          newHistory = [...prev];
          newHistory[existingIndex] = {
            ...newHistory[existingIndex],
            timestamp: new Date().toISOString(),
            resultCount: results.length,
            bondName
          };
        } else {
          // Add new search
          newHistory = [newSearch, ...prev];
        }
        
        // Keep only the last 50 searches in state
        const updatedHistory = newHistory.slice(0, 50);
        
        // Also save to localStorage
        saveSearchHistoryToLocalStorage(updatedHistory);
        
        return updatedHistory;
      });
    } catch (err) {
      setError(err.message || '搜索失败，请稍后再试');
      console.error('Search error:', err);
    } finally {
      setLoading(false);
    }
  };

  // Helper function to save search history to localStorage
  const saveSearchHistoryToLocalStorage = (history) => {
    try {
      localStorage.setItem('bondSearchHistory', JSON.stringify(history));
    } catch (error) {
      console.error('Error saving search history to localStorage:', error);
    }
  };

  // Helper function to load search history from localStorage
  const loadSearchHistoryFromLocalStorage = () => {
    try {
      const savedHistory = localStorage.getItem('bondSearchHistory');
      return savedHistory ? JSON.parse(savedHistory) : [];
    } catch (error) {
      console.error('Error loading search history from localStorage:', error);
      return [];
    }
  };

  // Load search history from API and localStorage
  useEffect(() => {
    const fetchSearchHistory = async () => {
      try {
        // First, load from localStorage
        const localHistory = loadSearchHistoryFromLocalStorage();
        
        // Then try to get from API
        let apiHistory = [];
        try {
          apiHistory = await getSearchHistory();
          apiHistory = Array.isArray(apiHistory) ? apiHistory : [];
        } catch (err) {
          console.error('Error fetching search history from API:', err);
        }
        
        // Merge histories (prioritize newer searches)
        const mergedHistory = mergeSearchHistories(localHistory, apiHistory);
        
        // Update state and localStorage
        setSearchHistory(mergedHistory);
        saveSearchHistoryToLocalStorage(mergedHistory);
      } catch (err) {
        console.error('Error managing search history:', err);
        setSearchHistory([]);
      }
    };

    fetchSearchHistory();
  }, []);

  // Helper function to merge search histories from different sources
  const mergeSearchHistories = (localHistory, apiHistory) => {
    // Create a map using just the query as a key (to ensure uniqueness)
    const historyMap = new Map();
    
    // Add all items to the map (newer timestamp will overwrite older for the same query)
    [...localHistory, ...apiHistory].forEach(item => {
      if (item && item.query && item.timestamp) {
        const existingItem = historyMap.get(item.query);
        
        // Only replace if this item is newer or if no existing item
        if (!existingItem || new Date(item.timestamp) > new Date(existingItem.timestamp)) {
          historyMap.set(item.query, item);
        }
      }
    });
    
    // Convert back to array and sort by timestamp (newest first)
    const mergedHistory = Array.from(historyMap.values()).sort((a, b) => {
      return new Date(b.timestamp) - new Date(a.timestamp);
    });
    
    // Limit to 20 entries
    return mergedHistory.slice(0, 20);
  };

  // Scroll to search history if showHistory is true
  useEffect(() => {
    if (showHistory && searchHistoryRef.current) {
      searchHistoryRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [showHistory, searchHistory]);

  // Check for pending searches (from search history navigation)
  useEffect(() => {
    const pendingSearch = sessionStorage.getItem('pendingSearch');
    if (pendingSearch) {
      // Clear the pending search from session storage
      sessionStorage.removeItem('pendingSearch');
      // Set the search query and perform the search
      setSearchQuery(pendingSearch);
      handleSearch(pendingSearch);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);  // We intentionally only want this to run once on mount

  const handleSubmit = (e) => {
    e.preventDefault();
    if (searchQuery.trim()) {
      handleSearch();
    }
  };

  const handleHistorySearch = (search) => {
    if (!search || typeof search !== 'object' || !search.query) {
      console.error('Invalid search item:', search);
      return;
    }
    
    // If we're on the search-history page, navigate to the search page
    if (showHistory) {
      navigate('/bonds/search');
      // We'll store the search query to be executed after navigation
      sessionStorage.setItem('pendingSearch', search.query);
    } else {
      // We're already on the search page, so just perform the search
      setSearchQuery(search.query);
      handleSearch(search.query);
    }
  };

  const handleMatchBond = async (bondCode) => {
    setMatchLoading(true);
    setMatchError(null);
    
    try {
      const results = await matchBond(bondCode);
      setMatchResults(results);
    } catch (err) {
      setMatchError(err.message || '匹配失败，请稍后再试');
      console.error('Match error:', err);
    } finally {
      setMatchLoading(false);
    }
  };

  return (
    <div className="bond-search">
      <div className="header-actions">
        <button onClick={handleReturn} className="return-button">
          返回主页
        </button>
        <button onClick={handleLogout} className="logout-button">
          退出登录
        </button>
      </div>
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-group">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="搜索债券代码、名称或发行人..."
            className="search-input"
          />
          <button
            type="submit"
            disabled={loading || !searchQuery.trim()}
            className="search-button"
          >
            {loading ? '搜索中...' : '搜索'}
          </button>
        </div>
      </form>

      {error && <div className="error-message">{error}</div>}

      {searchResults.length > 0 ? (
        <div className="search-results">
          <h2>搜索结果 ({searchResults.length})</h2>
          <table className="results-table">
            <thead>
              <tr>
                <th>债券代码</th>
                <th>债券名称</th>
                <th>发行人</th>
                <th>票面利率</th>
                <th>到期日</th>
                <th>操作</th>
              </tr>
            </thead>
            <tbody>
              {searchResults.map((bond) => (
                <tr key={bond.id}>
                  <td>{bond.bond_code}</td>
                  <td>{bond.bond_name}</td>
                  <td>{bond.issuer}</td>
                  <td>{bond.coupon_rate}</td>
                  <td>{bond.maturity_date}</td>
                  <td>
                    <button 
                      onClick={() => handleMatchBond(bond.bond_code)}
                      className="match-button"
                      disabled={matchLoading}
                    >
                      {matchLoading ? '匹配中...' : '匹配潜在买家'}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      ) : searchQuery && !loading ? (
        <div className="no-results">
          <p>未找到匹配的债券</p>
        </div>
      ) : null}

      {matchError && <div className="error-message">{matchError}</div>}

      {matchResults && (
        <div className="match-results">
          <h2>债券信息</h2>
          <div className="bond-info">
            <p><strong>债券代码:</strong> {matchResults.bond_info.bond_code || '未知'}</p>
            <p><strong>债券名称:</strong> {matchResults.bond_info.bond_name || '未知'}</p>
            <p><strong>发行人:</strong> {matchResults.bond_info.issuer || '未知'}</p>
            <p><strong>发行日期:</strong> {matchResults.bond_info.issue_date || '未知'}</p>
            <p><strong>期限:</strong> {matchResults.bond_info.term || '未知'}</p>
            <p><strong>票面利率:</strong> {matchResults.bond_info.coupon_rate || '未知'}</p>
          </div>

          <h2>潜在买家</h2>
          {matchResults.potential_buyers && matchResults.potential_buyers.length > 0 ? (
            <div className="potential-buyers">
              {matchResults.potential_buyers.map((buyer, index) => (
                <div key={index} className="buyer-card">
                  <h3>{buyer.company_name}</h3>
                  <p><strong>基金名称:</strong> {buyer.fund_name}</p>
                  <p><strong>基金经理:</strong> {buyer.fund_manager}</p>
                  
                  {buyer.primary_manager_contact && (
                    <div className="primary-contact">
                      <h4>主要联系人</h4>
                      <p><strong>电话:</strong> {buyer.primary_manager_contact.phone || '未提供'}</p>
                      <p><strong>邮箱:</strong> {buyer.primary_manager_contact.email || '未提供'}</p>
                    </div>
                  )}
                  
                  {buyer.all_contacts && buyer.all_contacts.length > 0 && (
                    <div className="all-contacts">
                      <h4>所有联系人</h4>
                      <table className="contacts-table">
                        <thead>
                          <tr>
                            <th>姓名</th>
                            <th>角色</th>
                            <th>电话</th>
                            <th>邮箱</th>
                          </tr>
                        </thead>
                        <tbody>
                          {buyer.all_contacts.map((contact, idx) => (
                            <tr key={idx}>
                              <td>{contact.name}</td>
                              <td>{contact.role}</td>
                              <td>{contact.phone}</td>
                              <td>{contact.email}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="no-buyers">
              <p>数据库中未找到曾持有该债券主体所发行债券之基金、理财等潜在买家。</p>
            </div>
          )}
        </div>
      )}

      <div ref={searchHistoryRef}>
        <SearchHistory
          searches={searchHistory}
          onSearch={handleHistorySearch}
        />
      </div>
    </div>
  );
};

export default BondSearch; 