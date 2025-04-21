import React from 'react';
import PropTypes from 'prop-types';
import './SearchHistory.css';

const SearchHistory = ({ searches = [], onSearch, showTitle = true }) => {
    // Ensure searches is an array and not empty
    if (!Array.isArray(searches) || searches.length === 0) {
        return (
            <div className="search-history">
                {showTitle && <h2 className="search-history-title">搜索历史</h2>}
                <div className="no-history">暂无搜索历史</div>
            </div>
        );
    }
    
    // Limit to the most recent 20 searches and ensure each item has the required properties
    const recentSearches = searches
        .slice(0, 20)
        .filter(search => search && typeof search === 'object' && search.query);

    if (recentSearches.length === 0) {
        return (
            <div className="search-history">
                {showTitle && <h2 className="search-history-title">搜索历史</h2>}
                <div className="no-history">暂无有效的搜索历史</div>
            </div>
        );
    }

    return (
        <div className="search-history">
            {showTitle && <h2 className="search-history-title">搜索历史</h2>}
            <div className="search-history-items">
                {recentSearches.map((search, index) => (
                    <div 
                        key={index} 
                        className="search-history-item"
                        onClick={() => onSearch(search)}
                    >
                        <div className="search-item-details">
                            <span className="search-query">{search.query}</span>
                            {search.bondName && (
                                <span className="search-bond-name">{search.bondName}</span>
                            )}
                        </div>
                        <span className="search-timestamp">
                            {search.timestamp ? new Date(search.timestamp).toLocaleString() : '未知时间'}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

SearchHistory.propTypes = {
    searches: PropTypes.arrayOf(
        PropTypes.shape({
            query: PropTypes.string.isRequired,
            bondName: PropTypes.string,
            timestamp: PropTypes.string.isRequired,
            resultCount: PropTypes.number
        })
    ),
    onSearch: PropTypes.func.isRequired,
    showTitle: PropTypes.bool
};

export default SearchHistory; 