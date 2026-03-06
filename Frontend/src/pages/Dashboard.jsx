import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { dashboardAPI } from '../services/api'
import SearchBar from '../components/SearchBar/SearchBar'
import CoinCard from '../components/CoinCard/CoinCard'
import CandlestickChart from '../components/CandlestickChart/CandlestickChart'
import "../styles/Dashboard.css"

const Dashboard = () => {
  const { user, token } = useAuth()
  const [cryptos, setCryptos] = useState([])
  const [marketData, setMarketData] = useState([])
  const [cashBalance, setCashBalance] = useState(0)
  const [cryptosLoading, setCryptosLoading] = useState(true)
  const [marketLoading, setMarketLoading] = useState(true)
  const [balanceLoading, setBalanceLoading] = useState(true)
  const [selectedCrypto, setSelectedCrypto] = useState(null)

  useEffect(() => {
    if (!user?.id || !token) return

    // Fetch all cryptos
    const fetchCryptos = async () => {
      try {
        const data = await dashboardAPI.getCryptos()
        setCryptos(data || [])
        // Set Bitcoin as default
        const btc = data?.find(c => c.symbol === 'BTC')
        if (btc && !selectedCrypto) {
          setSelectedCrypto(btc)
        }
      } catch (err) {
        console.error('Error fetching cryptos:', err)
      } finally {
        setCryptosLoading(false)
      }
    }

    // Fetch market data
    const fetchMarketData = async () => {
      try {
        const data = await dashboardAPI.getMarketData()
        setMarketData(data || [])
      } catch (err) {
        console.error('Error fetching market data:', err)
      } finally {
        setMarketLoading(false)
      }
    }

    // Fetch cash balance
    const fetchCashBalance = async () => {
      try {
        const data = await dashboardAPI.getCashBalance(user.id)
        setCashBalance(data.cash_balance || 0)
      } catch (err) {
        console.error('Error fetching cash balance:', err)
      } finally {
        setBalanceLoading(false)
      }
    }

    fetchCryptos()
    fetchMarketData()
    fetchCashBalance()

    // Set intervals for auto-refresh
    const cryptoInterval = setInterval(fetchCryptos, 300000) // 5 minutes
    const marketInterval = setInterval(fetchMarketData, 60000) // 1 minute
    const balanceInterval = setInterval(fetchCashBalance, 60000) // 1 minute

    return () => {
      clearInterval(cryptoInterval)
      clearInterval(marketInterval)
      clearInterval(balanceInterval)
    }
  }, [user?.id, token])



  const handleCryptoSelect = (crypto) => {
    setSelectedCrypto(crypto)
  }

  const handleSearch = async (crypto) => {
    try {
      const marketData = await dashboardAPI.getCryptoMarketData(crypto.id)
      setSelectedCrypto(marketData)
    } catch (err) {
      console.error('Error fetching market data for crypto:', err)
      setSelectedCrypto(crypto)
    }
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <div className="header-left">
          <h1>Dashboard</h1>
          <p className="welcome-text">Welcome, {user?.username || 'Guest'}!</p>
        </div>
        <div className="header-right">
          <div className="balance-card">
            <span className="balance-label">Cash Balance</span>
            {balanceLoading ? (
              <span className="balance-amount">--</span>
            ) : (
              <span className="balance-amount">${cashBalance.toFixed(2)}</span>
            )}
          </div>
          <SearchBar onSearch={handleSearch} token={token} />
        </div>
      </div>

      {/* Main Content */}
      <div className="dashboard-main">
        {/* Chart Section */}
        <div className="chart-section">
          {selectedCrypto && (
            <CandlestickChart 
              cryptoId={selectedCrypto.id}
              timeframe="24h"
              width={800}
              height={400}
            />
          )}
        </div>

        {/* Sidebar */}
        <div className="dashboard-sidebar">
          {/* Selected Crypto Card */}
          {selectedCrypto && (
            <div className="selected-crypto-card">
              <h3>Selected Cryptocurrency</h3>
              <CoinCard crypto={selectedCrypto} onSelect={() => {}} />
            </div>
          )}

          {/* Top Cryptos */}
          <div className="top-cryptos-card">
            <h3>Top Cryptocurrencies</h3>
            {cryptosLoading || marketLoading ? (
              <p className="loading-text">Loading...</p>
            ) : (
              <div className="crypto-list">
                {(marketData || cryptos).slice(0, 6).map((crypto) => (
                  <div
                    key={crypto.id}
                    className={`crypto-list-item ${selectedCrypto?.id === crypto.id ? 'active' : ''}`}
                    onClick={() => handleCryptoSelect(crypto)}
                  >
                    <div className="crypto-info">
                      <span className="crypto-symbol">{crypto.symbol}</span>
                      <span className="crypto-price">${crypto.price?.toFixed(2)}</span>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default Dashboard