import { useState, useEffect } from 'react'
import './OrderForm.css'

const OrderForm = ({ cryptoDetail, onSubmit, loading }) => {
  const [orderType, setOrderType] = useState('buy')
  const [quantity, setQuantity] = useState('')
  const [price, setPrice] = useState(cryptoDetail?.price?.toString() || '')

  useEffect(() => {
    if (cryptoDetail?.price) {
      setPrice(cryptoDetail.price.toString())
    }
  }, [cryptoDetail?.price])

  const handleSubmit = (e) => {
    e.preventDefault()
    
    if (!quantity) {
      alert('Please enter quantity')
      return
    }

    onSubmit({
      crypto_id: cryptoDetail?.crypto_id,
      order_type: orderType,
      quantity: parseFloat(quantity)
    })

    setQuantity('')
  }

  const totalValue = (parseFloat(quantity) || 0) * (parseFloat(price) || 0)

  return (
    <form onSubmit={handleSubmit} className="order-form">
      <div className="form-group">
        <label htmlFor="orderType">Order Type:</label>
        <select
          id="orderType"
          value={orderType}
          onChange={(e) => setOrderType(e.target.value)}
          className={`order-type-select ${orderType}`}
        >
          <option value="buy">Buy</option>
          <option value="sell">Sell</option>
        </select>
      </div>

      <div className="form-group">
        <label htmlFor="quantity">Quantity:</label>
        <input
          type="number"
          id="quantity"
          value={quantity}
          onChange={(e) => setQuantity(e.target.value)}
          placeholder="Enter quantity"
          step="0.00000001"
          min="0"
          required
        />
      </div>

      <div className="form-group">
        <label htmlFor="price">Price per unit:</label>
        <p>{cryptoDetail?.price}</p>
      </div>

      <div className="order-summary">
        <div className="summary-row">
          <span>Total Value:</span>
          <span className="total-value">${totalValue.toFixed(2)}</span>
        </div>
      </div>

      <button 
        type="submit" 
        disabled={loading || !quantity}
        className={`submit-btn ${orderType}`}
      >
        {loading ? 'Placing Order...' : `Place ${orderType.toUpperCase()} Order`}
      </button>
    </form>
  )
}

export default OrderForm