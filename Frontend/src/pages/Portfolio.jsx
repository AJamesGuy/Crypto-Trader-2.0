import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { portfolioAPI } from '../services/api'
import TradeChart from '../components/TradeChart/TradeChart'
import "../styles/Portfolio.css"

const Portfolio = () => {
  const { user, token } = useAuth()
  const [portfolio, setPortfolio] = useState(null)
  const [holdings, setHoldings] = useState([])
  const [performance, setPerformance] = useState(null)
  const [breakdown, setBreakdown] = useState(null)
  const [selectedAsset, setSelectedAsset] = useState(null)
  const [assetDetail, setAssetDetail] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user?.id || !token) return

    const fetchPortfolioData = async () => {
      try {
        setLoading(true)
        const [portfolioData, holdingsData, performanceData, breakdownData] = await Promise.all([
          portfolioAPI.getPortfolio(user.id),
          portfolioAPI.getHoldings(user.id),
          portfolioAPI.getPerformance(user.id),
          portfolioAPI.getBreakdown(user.id)
        ])

        setPortfolio(portfolioData)
        setHoldings(holdingsData || [])
        setPerformance(performanceData)
        setBreakdown(breakdownData)
      } catch (err) {
        console.error('Error fetching portfolio:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchPortfolioData()
    const interval = setInterval(fetchPortfolioData, 60000) // Refresh every minute

    return () => clearInterval(interval)
  }, [user?.id, token])

  const handleAssetSelect = async (assetId) => {
    try {
      const data = await portfolioAPI.getAsset(user.id, assetId)
      setAssetDetail(data)
      setSelectedAsset(assetId)
    } catch (err) {
      console.error('Error fetching asset detail:', err)
    }
  }

  // const enhancedHoldings = holdings.map(holding => ({
  //   ...holding, total_value: holding.current_value,
  // }));

  if (loading) return <p>Loading portfolio...</p>
  if (!portfolio) return <p>No portfolio data available</p>

  return (
    <div className="portfolio-container">
        <div classname="portfolio-container-2">
            <h1>Portfolio</h1>

      <div className="portfolio-overview">
        <div className="overview-card">
          <h2>Total Value</h2>
          <span className="value">${portfolio.total_portfolio_value?.toFixed(2)}</span>
        </div>
        <div className="overview-card">
          <h2>Total Invested</h2>
          <span className="value">${portfolio.total_invested?.toFixed(2)}</span>
        </div>
        <div className="overview-card">
          <h2>Gain/Loss</h2>
          <span className={`value ${portfolio.overall_gain_loss >= 0 ? 'positive' : 'negative'}`}>
            ${portfolio.overall_gain_loss?.toFixed(2)} ({portfolio.overall_gain_loss_percent?.toFixed(2)}%)
          </span>
        </div>
        <div className="overview-card">
          <h2>Cash Balance</h2>
          <span className="value">${portfolio.cash_balance?.toFixed(2)}</span>
        </div>
      </div>

      {performance && <TradeChart data={performance} />}

      {breakdown && (
        <div className="breakdown-section">
          <h2>Asset Allocation</h2>
          <div className="breakdown-grid">
            {breakdown.breakdown.map((asset, index) => (
              <div key={index} className="breakdown-item">
                <div className="breakdown-bar">
                  <div
                    className="breakdown-fill"
                    style={{ width: `${asset.percentage}%` }}
                  />
                </div>
                <div className="breakdown-info">
                  <span className="symbol">{asset.symbol}</span>
                  <span className="percentage">{asset.percentage?.toFixed(2)}%</span>
                  <span className="value">${asset.value?.toFixed(2)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="holdings-section">
        <h2>Holdings</h2>
        {holdings.length === 0 ? (
          <p>No holdings yet</p>
        ) : (
            <div className="holdings-table">
            <table>
              <thead>
                <tr>
                  <th>Cryptocurrency</th>
                  <th>Quantity</th>
                  <th>Avg. Cost</th>
                  <th>Current Price</th>
                  <th>Total Value</th>
                  <th>Gain/Loss</th>
                  <th>% Gain</th>
                </tr>
              </thead>
              <tbody>
                {holdings.map((holding) => (
                  <tr
                    key={holding.id}
                    onClick={() => handleAssetSelect(holding.id)}
                    style={{ cursor: 'pointer' }}
                  >
                    <td className="symbol-cell">
                      {holding.crypto_image && (
                          <img src={holding.crypto_image} alt={holding.symbol} className="icon" />
                      )}
                      <span>{holding.crypto_name} ({holding.symbol?.toUpperCase()})</span>
                    </td>
                    <td>{holding.quantity?.toFixed(8)}</td>
                    <td>${holding.average_cost?.toFixed(2)}</td>
                    <td>${holding.current_price?.toFixed(2)}</td>
                    <td>${holding.current_value?.toFixed(2)}</td>
                    <td className={holding.gain_loss >= 0 ? 'positive' : 'negative'}>
                      ${holding.gain_loss?.toFixed(2)}
                    </td>
                    <td className={holding.gain_percentage >= 0 ? 'positive' : 'negative'}>
                      {holding.gain_percentage?.toFixed(2)}%
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {selectedAsset && assetDetail && (
        <div className="asset-detail-modal">
          <div className="modal-content">
            <button
              className="close-btn"
              onClick={() => {
                setSelectedAsset(null)
                setAssetDetail(null)
              }}
            >
              ×
            </button>
            <h2>{assetDetail.crypto_name}</h2>
            <div className="asset-stats">
              <div className="stat">
                <span className="label">Quantity Held</span>
                <span className="value">{assetDetail.quantity?.toFixed(8)}</span>
              </div>
              <div className="stat">
                <span className="label">Average Cost Per Unit</span>
                <span className="value">${assetDetail.avg_buy_price?.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="label">Current Price</span>
                <span className="value">${assetDetail.current_price?.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="label">Total Cost Basis</span>
                <span className="value">${assetDetail.invested_value?.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="label">Current Value</span>
                <span className="value">${assetDetail.current_value?.toFixed(2)}</span>
              </div>
              <div className="stat">
                <span className="label">Unrealized Gain/Loss</span>
                <span className={`value ${assetDetail.gain_loss >= 0 ? 'positive' : 'negative'}`}>
                  ${assetDetail.gain_loss?.toFixed(2)} ({assetDetail.gain_loss_percent?.toFixed(2)}%)
                </span>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  )
}

export default Portfolio