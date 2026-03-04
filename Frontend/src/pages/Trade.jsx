import { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import { dashboardAPI, tradeAPI } from '../services/api'
import OrderForm from '../components/OrderForm/OrderForm'
import CoinCard from '../components/CoinCard/CoinCard'
import CandlestickChart from '../components/CandlestickChart/CandlestickChart'
import "../styles/Trade.css"

const Trade = () => {
  const { user, token } = useAuth()
  const [cryptos, setCryptos] = useState([])
  const [selectedCrypto, setSelectedCrypto] = useState(null)
  const [orders, setOrders] = useState([])
  const [loading, setLoading] = useState(false)
  const [message, setMessage] = useState('')
  const [page, setPage] = useState(1)
  const [totalOrders, setTotalOrders] = useState(0)
  const [candleData, setCandleData] = useState([])
  const [candleLoading, setCandleLoading] = useState(false)
//   const [formData, setFormData] = useState({});

  useEffect(() => {
    if (!user?.id || !token) return

    // Fetch all cryptos for dropdown
    const fetchCryptos = async () => {
      try {
        const data = await dashboardAPI.getCryptos()
        setCryptos(data || [])
        // Set Bitcoin as default
        const btc = data?.find(c => c.symbol === 'BTC')
        if (btc && !selectedCrypto) {
          handleCryptoSelect(btc.id)
        }
      } catch (err) {
        console.error('Error fetching cryptos:', err)
      }
    }

    // Fetch orders
    const fetchOrders = async () => {
      try {
        const data = await tradeAPI.getOrders(user.id, page, 10)
        setOrders(data.orders || [])
        setTotalOrders(data.total || 0)
      } catch (err) {
        console.error('Error fetching orders:', err)
      }
    }

    fetchCryptos()
    fetchOrders()
  }, [user?.id, token, page])

  const handleCryptoSelect = async (cryptoId) => {
    try {
      const data = await dashboardAPI.getCryptoMarketData(cryptoId)
      setSelectedCrypto(data)
      setMessage('')
      
      // Fetch candlestick data
      setCandleLoading(true)
      try {
        const candleData = await dashboardAPI.getCandleData(cryptoId, '24h')
        setCandleData(candleData || [])
      } catch (err) {
        console.error('Error fetching candle data:', err)
        setCandleData([])
      } finally {
        setCandleLoading(false)
      }
    } catch (err) {
      setMessage('Error fetching crypto details')
      setCandleData([])
    }
  }

  const handlePlaceOrder = async (formData) => {
    setLoading(true)
    setMessage('')

    try {
      await tradeAPI.placeOrder(user.id, formData)
      setMessage('Order placed successfully!')
      setSelectedCrypto(null)

      // Refresh orders list
      const data = await tradeAPI.getOrders(user.id, 1, 10)
      setOrders(data.orders || [])
      setPage(1)
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to place order'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleExecuteOrder = async (orderId) => {
    setLoading(true)
    try {
      await tradeAPI.executeOrder(user.id, orderId)
      setMessage('Order executed successfully!')
      
      // Refresh orders
      const data = await tradeAPI.getOrders(user.id, page, 10)
      setOrders(data.orders || [])
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to execute order'}`)
    } finally {
      setLoading(false)
    }
  }

  const handleCancelOrder = async (orderId) => {
    if (!window.confirm('Are you sure you want to cancel this order?')) {
      return
    }

    setLoading(true)
    try {
      await tradeAPI.cancelOrder(user.id, orderId)
      setMessage('Order cancelled successfully!')
      
      // Refresh orders
      const data = await tradeAPI.getOrders(user.id, page, 10)
      setOrders(data.orders || [])
    } catch (err) {
      setMessage(`Error: ${err.message || 'Failed to cancel order'}`)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="trade-container">
      <div className="trade-header">
        <h1>Trade</h1>
        <p className="subtitle">Select a cryptocurrency and place your order</p>
      </div>

      <div className="trade-main">
        <div className="trade-chart-section">
          {selectedCrypto ? (
            !candleLoading && candleData.length > 0 ? (
              <CandlestickChart 
                data={candleData} 
                cryptoName={selectedCrypto.name || selectedCrypto.symbol}
                timeframe="24h"
              />
            ) : (
              <div className="chart-loading">Loading chart data...</div>
            )
          ) : null}
        </div>

        <div className="trade-panel">
          <div className="crypto-selector-section">
            <label htmlFor="crypto-select">Select Cryptocurrency</label>
            <select 
              id="crypto-select"
              onChange={(e) => handleCryptoSelect(e.target.value)}
              value={selectedCrypto?.id || ''}
            >
              <option value="">Choose a cryptocurrency...</option>
              {cryptos.map((crypto) => (
                <option key={crypto.id} value={crypto.id}>
                  {crypto.name} ({crypto.symbol?.toUpperCase()})
                </option>
              ))}
            </select>
          </div>

          {message && (
            <div className={`message-box ${message.includes('Error') ? 'error' : 'success'}`}>
              {message}
            </div>
          )}

          {selectedCrypto && (
            <div className="trading-section">
              <div className="crypto-detail-card">
                <CoinCard crypto={selectedCrypto} />
              </div>
              <div className="order-form-card">
                <OrderForm
                  cryptoDetail={selectedCrypto}
                  onSubmit={handlePlaceOrder} 
                  loading={loading}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="orders-panel">
        <h2>Order History</h2>
        {orders.length === 0 ? (
          <p className="no-orders">No orders yet</p>
        ) : (
          <div className="orders-table-wrapper">
            <table className="orders-table">
              <thead>
                <tr>
                  <th>Crypto</th>
                  <th>Type</th>
                  <th>Quantity</th>
                  <th>Price</th>
                  <th>Total</th>
                  <th>Status</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {orders.map((order) => (
                  <tr key={order.id}>
                    <td>{order.symbol}</td>
                    <td className={`type-${order.type}`}>{order.type.toUpperCase()}</td>
                    <td>{order.quantity}</td>
                    <td>${order.price?.toFixed(2)}</td>
                    <td>${(order.quantity * order.price)?.toFixed(2)}</td>
                    <td className={`status-${order.status}`}>{order.status}</td>
                    <td className="actions">
                      {order.status === 'pending' && (
                        <div className="action-buttons">
                          <button
                            className="btn-execute"
                            onClick={() => handleExecuteOrder(order.id)}
                            disabled={loading}
                          >
                            Execute
                          </button>
                          <button
                            className="btn-cancel"
                            onClick={() => handleCancelOrder(order.id)}
                            disabled={loading}
                          >
                            Cancel
                          </button>
                        </div>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            <div className="pagination">
              <button
                onClick={() => setPage(Math.max(1, page - 1))}
                disabled={page === 1}
              >
                ← Previous
              </button>
              <span className="page-info">Page {page} of {Math.ceil(totalOrders / 10)}</span>
              <button
                onClick={() => setPage(page + 1)}
                disabled={page * 10 >= totalOrders}
              >
                Next →
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default Trade