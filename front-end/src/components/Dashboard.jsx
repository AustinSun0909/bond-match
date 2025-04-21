import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { getCurrentUser } from '../services/auth';
import { searchBonds, getSearchHistory, matchBond } from '../services/bondService';
import SearchHistory from './SearchHistory.jsx';
import ContactList from './ContactList.jsx';
import './Dashboard.css';

const Dashboard = () => {
  const { isLoggedIn, logout } = useAuth();
  const navigate = useNavigate();
  const [currentUser, setCurrentUser] = useState(null);
  
  // Bond search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [searchHistory, setSearchHistory] = useState([]);
  const [matchResults, setMatchResults] = useState(null);
  const [matchLoading, setMatchLoading] = useState(false);
  const [matchError, setMatchError] = useState(null);
  const [activeTab, setActiveTab] = useState('search'); // 'search' or 'history'
  const [tabTransitioning, setTabTransitioning] = useState(false);

  // Verify authentication and get user on component mount
  useEffect(() => {
    // Check if user is logged in
    if (!isLoggedIn) {
      console.log('Dashboard: Not logged in, redirecting to login');
      navigate('/login');
      return;
    }

    // Get current user info
    const userInfo = getCurrentUser();
    console.log('Dashboard: Current user from token:', userInfo);
    
    if (userInfo) {
      setCurrentUser(userInfo);
    } else {
      console.warn('Dashboard: No user info found in token');
      // If we can't get user info but have a token, still allow access
      // but consider logging the user out if this is unexpected
      setCurrentUser({ username: localStorage.getItem('lastUsername') || 'User' });
    }
  }, [isLoggedIn, navigate]);
  
  const handleLogout = () => {
    console.log('Dashboard: Logout button clicked');
    logout();
  };
  
  // Helper functions for search history
  const saveSearchHistoryToLocalStorage = (history) => {
    try {
      localStorage.setItem('bondSearchHistory', JSON.stringify(history));
    } catch (error) {
      console.error('Error saving search history to localStorage:', error);
    }
  };

  const loadSearchHistoryFromLocalStorage = () => {
    try {
      const savedHistory = localStorage.getItem('bondSearchHistory');
      return savedHistory ? JSON.parse(savedHistory) : [];
    } catch (error) {
      console.error('Error loading search history from localStorage:', error);
      return [];
    }
  };
  
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

  // Load search history on component mount
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

  const handleTabChange = (tab) => {
    if (tab === activeTab) return;
    
    setTabTransitioning(true);
    setActiveTab(tab);
    
    // Reset transition flag after animation completes
    setTimeout(() => {
      setTabTransitioning(false);
    }, 300);
  };

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
    // Switch to search tab to show results
    setActiveTab('search');

    try {
      const results = await searchBonds(query.trim());
      console.log('Search results in Dashboard:', results);
      
      // Process results to use proper bond names
      const processedResults = results.map(bond => ({
        ...bond,
        // We don't need the fallback anymore as the backend should provide proper names
        bond_name: bond.bond_name
      }));
      
      setSearchResults(processedResults);

      // Get bond name from the first result if available
      let bondName = '';
      if (processedResults.length > 0) {
        bondName = processedResults[0].bond_name || '';
      }

      // Add to search history locally (will also be saved on backend)
      const newSearch = {
        query,
        bondName,
        timestamp: new Date().toISOString(),
        resultCount: processedResults.length
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
            resultCount: processedResults.length,
            bondName
          };
        } else {
          // Add new search
          newHistory = [newSearch, ...prev];
        }
        
        // Keep only the last 20 searches in state
        const updatedHistory = newHistory.slice(0, 20);
        
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
    
    // Set the search query and perform the search
    setSearchQuery(search.query);
    handleSearch(search.query);
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
    <div className="app-layout">
      {/* Fixed header */}
      <header className="app-header">
        <h1 className="app-title">债券匹配系统</h1>
        <div className="user-info">
          <span className="welcome-text">欢迎, {currentUser?.username || 'Guest'}</span>
          <button onClick={handleLogout} className="logout-button">
            登出
          </button>
        </div>
      </header>
      
      <div className="app-content">
        {/* Fixed sidebar */}
        <aside className="app-sidebar">
          <nav className="sidebar-nav">
            <button 
              onClick={() => handleTabChange('search')} 
              className={`nav-button ${activeTab === 'search' ? 'active' : ''}`}
            >
              债券搜索
            </button>
            <button 
              onClick={() => handleTabChange('history')} 
              className={`nav-button ${activeTab === 'history' ? 'active' : ''}`}
            >
              搜索历史
            </button>
          </nav>
        </aside>
        
        {/* Main content area */}
        <main className="main-content">
          <div className={`tab-content ${tabTransitioning ? 'transitioning' : ''}`}>
            {activeTab === 'search' ? (
              <div className="content-section">
                <h2 className="section-title">债券搜索</h2>
                
                <div className="search-container">
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
                </div>
                
                <div className="results-container">
                  {loading && (
                    <div className="loading-indicator">
                      <p>正在搜索，请稍候...</p>
                    </div>
                  )}

                  {searchResults.length > 0 ? (
                    <div className="search-results">
                      <h3>搜索结果 ({searchResults.length})</h3>
                      <div className="results-table-wrapper">
                        <table className="results-table">
                          <thead>
                            <tr>
                              <th>债券代码</th>
                              <th>债券名称</th>
                              <th>发行人</th>
                              <th>票面利率(%)</th>
                              <th>剩余期限</th>
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
                                <td>{bond.remaining_term || '-'}</td>
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
                    </div>
                  ) : searchQuery && !loading ? (
                    <div className="no-results">
                      <p>未找到匹配的债券</p>
                    </div>
                  ) : !loading && (
                    <div className="empty-state">
                      <p>请输入债券代码、名称或发行人进行搜索</p>
                    </div>
                  )}

                  {matchError && <div className="error-message">{matchError}</div>}

                  {matchResults && (
                    <div className="match-results">
                      <h3>债券信息</h3>
                      <div className="bond-info">
                        <p><strong>债券代码:</strong> {matchResults.bond_info.bond_code || '未知'}</p>
                        <p><strong>债券名称:</strong> {matchResults.bond_info.bond_name || '未知'}</p>
                        <p><strong>发行人:</strong> {matchResults.bond_info.issuer || '未知'}</p>
                        <p><strong>发行日期:</strong> {matchResults.bond_info.issue_date || '未知'}</p>
                        <p><strong>期限:</strong> {matchResults.bond_info.term || '未知'}</p>
                        <p><strong>票面利率(%):</strong> {matchResults.bond_info.coupon_rate || '未知'}</p>
                        <p><strong>剩余期限:</strong> {matchResults.bond_info.remaining_term || '未知'}</p>
                      </div>

                      <h3>潜在买家</h3>
                      {matchResults.potential_buyers && matchResults.potential_buyers.length > 0 ? (
                        <div className="potential-buyers">
                          {matchResults.potential_buyers.map((buyer, index) => (
                            <div key={index} className="buyer-card">
                              <div className="buyer-header">
                                <h4>{buyer.company_name}</h4>
                                <span className="company-type-badge">{buyer.company_type}</span>
                              </div>
                              
                              {buyer.primary_contact && (
                                <div className="primary-contact">
                                  <h5 className="contact-heading">主要联系人</h5>
                                  <div className="primary-contact-card">
                                    <div className="contact-name-container">
                                      <div className="contact-name">
                                        {buyer.primary_contact.name}
                                        {buyer.primary_contact.is_leader && <span className="leader-badge">领导</span>}
                                      </div>
                                      <div className="contact-role">
                                        {buyer.primary_contact.role}
                                        {buyer.entity_type === 'fund' && buyer.fund_name && (
                                          <span className="fund-name">（{buyer.fund_name}）</span>
                                        )}
                                      </div>
                                    </div>
                                    <div className="contact-details">
                                      <p><strong>工作电话:</strong> {buyer.primary_contact.phone || '-'}</p>
                                      <p><strong>手机:</strong> {buyer.primary_contact.mobile || '-'}</p>
                                      <p><strong>邮箱:</strong> {buyer.primary_contact.email || '-'}</p>
                                      <p><strong>微信:</strong> {buyer.primary_contact.wechat || '-'}</p>
                                      <p><strong>QQ:</strong> {buyer.primary_contact.qq || '-'}</p>
                                      <p><strong>QT:</strong> {buyer.primary_contact.qt || '-'}</p>
                                    </div>
                                  </div>
                                </div>
                              )}
                              
                              {buyer.all_contacts && buyer.all_contacts.length > 0 && (
                                <ContactList contacts={buyer.all_contacts} />
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
                </div>
              </div>
            ) : (
              <div className="content-section">
                <h2 className="section-title">搜索历史</h2>
                <div className="history-container">
                  <SearchHistory
                    searches={searchHistory}
                    onSearch={handleHistorySearch}
                    showTitle={false}
                  />
                </div>
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  );
};

export default Dashboard; 