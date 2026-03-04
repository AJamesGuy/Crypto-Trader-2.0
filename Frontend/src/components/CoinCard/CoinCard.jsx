import React from 'react'
import './CoinCard.css'

const CoinCard = ({ crypto, onSelect }) => {
  if (!crypto) return null

  const priceChange = crypto.change_24h || 0
  const changePercentage = crypto.change_24h || 0
  const isPositive = priceChange >= 0

  return (
    <div 
      className="coin-card"
      onClick={() => onSelect && onSelect(crypto)}
      style={{ cursor: onSelect ? 'pointer' : 'default' }}
    >
      <div className="coin-header">
        <img src={crypto.image} alt={crypto.symbol} className="coin-icon" />
        <div className="coin-info">
          <h3 className="coin-name">{crypto.name}</h3>
          <span className="coin-symbol">{crypto.symbol?.toUpperCase()}</span>
        </div>
        {crypto.market_cap_rank && (
          <span className="coin-rank">#{crypto.market_cap_rank}</span>
        )}
      </div>
      
      <div className="coin-price">
        <span className="price">${crypto.price?.toFixed(2)}</span>
        <span className={`change ${isPositive ? 'positive' : 'negative'}`}>
          {isPositive ? '+' : ''}{changePercentage?.toFixed(2)}%
        </span>
      </div>

      {crypto.description && (
        <p className="coin-description">{crypto.description}</p>
      )}

      {crypto.market_cap && (
        <div className="coin-stats">
          <div className="stat">
            <span className="label">Market Cap</span>
            <span className="value">${(crypto.market_cap / 1e9).toFixed(2)}B</span>
          </div>
          <div className="stat">
            <span className="label">24h Volume</span>
            <span className="value">${(crypto.volume / 1e9).toFixed(2)}B</span>
          </div>
        </div>
      )}
    </div>
  )
}

export default CoinCard