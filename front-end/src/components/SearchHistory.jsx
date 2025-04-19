import React from 'react';
import PropTypes from 'prop-types';

const SearchHistory = ({ history = [], onSearch }) => {
    if (!history || history.length === 0) return null;

    return (
        <div className="mt-6">
            <h2 className="text-xl font-semibold mb-2">搜索历史</h2>
            <div className="flex flex-wrap gap-2">
                {history.map((code, index) => (
                    <button
                        key={index}
                        onClick={() => onSearch(code)}
                        className="bg-gray-100 hover:bg-gray-200 px-3 py-1 rounded text-sm"
                    >
                        {code}
                    </button>
                ))}
            </div>
        </div>
    );
};

SearchHistory.propTypes = {
    history: PropTypes.arrayOf(PropTypes.string),
    onSearch: PropTypes.func.isRequired
};

export default SearchHistory; 