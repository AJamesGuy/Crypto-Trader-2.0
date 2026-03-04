import { useState } from 'react'
import { dashboardAPI } from '../../services/api'
import './SearchBar.css'

const SearchBar = ({ onSearch, token }) => {
  const [query, setQuery] = useState('')
  const [results, setResults] = useState([])
  const [loading, setLoading] = useState(false)
  const [showResults, setShowResults] = useState(false)

  const handleSearch = async (e) => {
    const searchTerm = e.target.value
    setQuery(searchTerm)

    if (searchTerm.trim() === '') {
      setResults([])
      setShowResults(false)
      return
    }

    setLoading(true)
    try {
      const data = await dashboardAPI.searchCryptos(searchTerm, 10)
      setResults(data || [])
      setShowResults(true)
    } catch (err) {
      console.error('Search error:', err)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  const handleSelectResult = (crypto) => {
    if (onSearch) {
      onSearch(crypto)
    }
    setQuery('')
    setResults([])
    setShowResults(false)
  }

  return (
    <div className="search-container">
      <input
        type="text"
        className="search-input"
        placeholder="Search cryptocurrencies..."
        value={query}
        onChange={handleSearch}
      />
      {loading && <p className="search-loading">Searching...</p>}
      {showResults && results.length > 0 && (
        <div className="search-results">
          {results.map((crypto) => (
            <div
              key={crypto.id}
              className="search-result-item"
              onClick={() => handleSelectResult(crypto)}
            >
              <img src={crypto.image} alt={crypto.symbol} className="result-icon" />
              <div className="result-info">
                <span className="result-name">{crypto.name}</span>
                <span className="result-symbol">{crypto.symbol?.toUpperCase()}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

export default SearchBar