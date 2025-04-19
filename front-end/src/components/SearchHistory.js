import React from 'react';
import './SearchHistory.css';

const SearchHistory = ({ searches, onSearch }) => {
  return (
    <div className="search-history">
      <h3>Recent Searches</h3>
      {searches.length === 0 ? (
        <p className="no-history">No search history yet</p>
      ) : (
        <ul className="history-list">
          {searches.map((search, index) => (
            <li key={index} className="history-item">
              <button
                onClick={() => onSearch(search)}
                className="history-button"
              >
                <div className="search-details">
                  <span className="search-query">{search.query}</span>
                  <span className="search-date">
                    {new Date(search.timestamp).toLocaleString()}
                  </span>
                </div>
                <div className="search-results">
                  Found {search.resultCount} bonds
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default SearchHistory; 