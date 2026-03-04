import React from 'react'
import './TradeChart.css'

const TradeChart = ({ data }) => {
  if (!data) return <p>No chart data available</p>

  const maxValue = Math.max(...(data.assets?.map(a => a.value) || [1]))

  return (
    <div className="trade-chart">
      <h3 className="chart-title">Portfolio Performance</h3>
      <div className="chart-container">
        {data.assets && data.assets.map((asset, index) => (
          <div key={index} className="chart-bar-group">
            <div className="chart-bar-wrapper">
              <div
                className="chart-bar"
                style={{
                  height: `${(asset.value / maxValue) * 100}%`
                }}
              >
                <span className="bar-value">${asset.value?.toFixed(0)}</span>
              </div>
            </div>
            <div className="chart-label">
              <span className="symbol">{asset.symbol}</span>
              <span className="percentage">{asset.percentage?.toFixed(1)}%</span>
            </div>
          </div>
        ))}
      </div>
      <div className="chart-stats">
        <div className="stat">
          <span className="label">Total Portfolio Value</span>
          <span className="value">${data.total_value?.toFixed(2)}</span>
        </div>
        <div className="stat">
          <span className="label">Total Gain/Loss</span>
          <span className={`value ${data.total_gain >= 0 ? 'positive' : 'negative'}`}>
            ${data.total_gain?.toFixed(2)} ({data.gain_percentage?.toFixed(2)}%)
          </span>
        </div>
      </div>
    </div>
  )
}

export default TradeChart