import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import SearchHistory from './SearchHistory.jsx';
import { useAuth } from '../context/AuthContext';
import { searchBonds, getSearchHistory, matchBond } from '../services/bondService';
import './BondSearch.css';

const BondSearch = () => {
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

  const handleLogout = () => {
    console.log('BondSearch: Logout button clicked');
    // Let the auth.js logout function handle the redirection
    logout();
  };

  // Load search history from API
  useEffect(() => {
    const fetchSearchHistory = async () => {
      try {
        const history = await getSearchHistory();
        setSearchHistory(history);
      } catch (err) {
        console.error('Error fetching search history:', err);
      }
    };

    fetchSearchHistory();
  }, []);

  const handleSearch = async (query = searchQuery) => {
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

      // Add to search history locally (will also be saved on backend)
      const newSearch = {
        query,
        timestamp: new Date().toISOString(),
        resultCount: results.length
      };

      setSearchHistory(prev => {
        const newHistory = [newSearch, ...prev];
        // Keep only the last 50 searches
        return newHistory.slice(0, 50);
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
    <div className="bond-search">
      <div className="header-actions">
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

      <SearchHistory
        searches={searchHistory}
        onSearch={handleHistorySearch}
      />
    </div>
  );
};

export default BondSearch; 