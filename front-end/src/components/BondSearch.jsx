import React, { useState, useEffect } from 'react';
import axios from 'axios';
import SearchHistory from './SearchHistory.jsx';

const BondSearch = () => {
    const [bondCode, setBondCode] = useState('');
    const [searchResults, setSearchResults] = useState(null);
    const [error, setError] = useState(null);
    const [searchHistory, setSearchHistory] = useState([]);

    useEffect(() => {
        // Load search history from localStorage
        const savedHistory = localStorage.getItem('bondSearchHistory');
        if (savedHistory) {
            try {
                const parsedHistory = JSON.parse(savedHistory);
                if (Array.isArray(parsedHistory)) {
                    setSearchHistory(parsedHistory);
                }
            } catch (e) {
                console.error('Failed to parse search history:', e);
                localStorage.removeItem('bondSearchHistory');
            }
        }
    }, []);

    const handleSearch = async (e) => {
        e.preventDefault();
        setError(null);
        setSearchResults(null);

        try {
            const response = await axios.post('/api/bond/match/', {
                bond_code: bondCode
            });

            // Update search history
            const newHistory = [bondCode, ...searchHistory.filter(code => code !== bondCode)].slice(0, 10);
            setSearchHistory(newHistory);
            localStorage.setItem('bondSearchHistory', JSON.stringify(newHistory));

            setSearchResults(response.data);
        } catch (err) {
            setError(err.response?.data?.error || '搜索失败，请稍后重试');
        }
    };

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">债券匹配搜索</h1>
            
            <form onSubmit={handleSearch} className="mb-6">
                <div className="flex gap-4">
                    <input
                        type="text"
                        value={bondCode}
                        onChange={(e) => setBondCode(e.target.value)}
                        placeholder="输入债券代码"
                        className="flex-1 p-2 border rounded"
                        required
                    />
                    <button
                        type="submit"
                        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
                    >
                        搜索
                    </button>
                </div>
            </form>

            {error && (
                <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
                    {error}
                </div>
            )}

            {searchResults && (
                <div className="mb-6">
                    <h2 className="text-xl font-semibold mb-2">搜索结果</h2>
                    
                    {searchResults.message ? (
                        <div className="bg-yellow-100 border border-yellow-400 text-yellow-700 px-4 py-3 rounded">
                            {searchResults.message}
                        </div>
                    ) : (
                        <div className="space-y-6">
                            {searchResults.potential_buyers.map((buyer, index) => (
                                <div key={index} className="border p-4 rounded-lg">
                                    <h3 className="text-lg font-semibold mb-2">{buyer.company_name}</h3>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div>
                                            <p><strong>基金名称:</strong> {buyer.fund_name}</p>
                                            <p><strong>基金经理:</strong> {buyer.fund_manager}</p>
                                            {buyer.primary_manager_contact && (
                                                <div className="mt-2">
                                                    <p><strong>经理联系方式:</strong></p>
                                                    {buyer.primary_manager_contact.phone && (
                                                        <p>电话: {buyer.primary_manager_contact.phone}</p>
                                                    )}
                                                    {buyer.primary_manager_contact.email && (
                                                        <p>邮箱: {buyer.primary_manager_contact.email}</p>
                                                    )}
                                                </div>
                                            )}
                                        </div>
                                        <div>
                                            <p><strong>所有联系人:</strong></p>
                                            <ul className="list-disc pl-5">
                                                {buyer.all_contacts.map((contact, idx) => (
                                                    <li key={idx}>
                                                        {contact.name} ({contact.role})
                                                        {contact.phone && ` - 电话: ${contact.phone}`}
                                                        {contact.email && ` - 邮箱: ${contact.email}`}
                                                    </li>
                                                ))}
                                            </ul>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            <SearchHistory 
                history={searchHistory}
                onSearch={(code) => {
                    setBondCode(code);
                    handleSearch({ preventDefault: () => {} });
                }}
            />
        </div>
    );
};

export default BondSearch; 