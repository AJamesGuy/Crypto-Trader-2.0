import React, { useMemo } from 'react'
import {
  ComposedChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer
} from 'recharts'
import './CandlestickChart.css'

const CandlestickChart = ({ data, cryptoName = 'Cryptocurrency', timeframe = '24h' }) => {
  // Format candle data for display
  const formattedData = useMemo(() => {
    if (!data || !Array.isArray(data)) {
      console.warn('CandlestickChart: No data or data is not an array', data)
      return []
    }
    
    console.log('Processing candlestick data:', data)
    
    return data.map((candle, index) => {
      try {
        const open = parseFloat(candle.open)
        const close = parseFloat(candle.close)
        const high = parseFloat(candle.high)
        const low = parseFloat(candle.low)
        
        // Validate that all values are numbers
        if (isNaN(open) || isNaN(close) || isNaN(high) || isNaN(low)) {
          console.warn(`Skipping candle ${index} with invalid values:`, candle)
          return null
        }
        
        return {
          time: candle.time || `${index}`,
          open: open,
          close: close,
          high: high,
          low: low,
          volume: candle.volume || 0,
          isUp: close >= open,
          changePercent: (((close - open) / open) * 100).toFixed(2)
        }
      } catch (e) {
        console.error(`Error processing candle ${index}:`, e, candle)
        return null
      }
    }).filter(c => c !== null)
  }, [data])

  if (!formattedData.length) {
    return (
      <div className="flex items-center justify-center h-96 bg-gray-900 rounded-lg border border-gray-800">
        <div className="text-center">
          <p className="text-gray-400 mb-2">No chart data available</p>
          <p className="text-gray-600 text-sm">
            Make sure the cryptocurrency has historical data in the system
          </p>
        </div>
      </div>
    )
  }

  const minPrice = Math.min(...formattedData.map(d => d.low)) * 0.95
  const maxPrice = Math.max(...formattedData.map(d => d.high)) * 1.05

  const CustomCandlestick = (props) => {
    const { x, y, width, height, payload } = props
    
    if (!payload) return null

    const xCenter = x + width / 2
    const yScale = (price) => {
      return y + height - ((price - minPrice) / (maxPrice - minPrice)) * height
    }

    const wickX = xCenter
    const bodyWidth = Math.max(width * 0.6, 4)
    const wickColor = payload.isUp ? '#10b981' : '#ef4444'
    const bodyColor = payload.isUp ? '#10b981' : '#ef4444'

    const wickTop = yScale(payload.high)
    const wickBottom = yScale(payload.low)

    const bodyTop = yScale(Math.max(payload.open, payload.close))
    const bodyBottom = yScale(Math.min(payload.open, payload.close))
    const bodyHeight = Math.max(bodyBottom - bodyTop, 1)

    return (
      <g>
        <line
          x1={wickX}
          y1={wickTop}
          x2={wickX}
          y2={wickBottom}
          stroke={wickColor}
          strokeWidth={1}
        />
        <rect
          x={xCenter - bodyWidth / 2}
          y={bodyTop}
          width={bodyWidth}
          height={bodyHeight}
          fill={bodyColor}
          stroke={bodyColor}
          strokeWidth={1}
        />
      </g>
    )
  }

  const CustomTooltip = ({ active, payload }) => {
    if (active && payload && payload[0]) {
      const data = payload[0].payload
      return (
        <div className="bg-gray-800 border border-gray-700 rounded p-3 shadow-lg">
          <p className="text-gray-300 text-sm mb-2">
            <span className="font-semibold">{data.time}</span>
          </p>
          <p className="text-gray-400 text-xs">
            <span className="text-gray-500">Open:</span> <span className="text-white">${data.open.toFixed(2)}</span>
          </p>
          <p className="text-gray-400 text-xs">
            <span className="text-gray-500">High:</span> <span className="text-white">${data.high.toFixed(2)}</span>
          </p>
          <p className="text-gray-400 text-xs">
            <span className="text-gray-500">Low:</span> <span className="text-white">${data.low.toFixed(2)}</span>
          </p>
          <p className={`text-xs font-semibold mt-1 ${data.isUp ? 'text-green-400' : 'text-red-400'}`}>
            Close: ${data.close.toFixed(2)} ({data.changePercent}%)
          </p>
        </div>
      )
    }
    return null
  }

  return (
    <div className="candlestick-container">
      <div className="bg-gray-900 rounded-lg border border-gray-800 p-6 shadow-xl">
        {/* Header */}
        <div className="flex justify-between items-center mb-6">
          <div>
            <h2 className="text-2xl font-bold text-white">{cryptoName} Price Chart</h2>
            <p className="text-gray-400 text-sm mt-1">Timeframe: {timeframe}</p>
          </div>
          <div className="flex gap-3">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 rounded-sm"></div>
              <span className="text-gray-400 text-sm">Up</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 rounded-sm"></div>
              <span className="text-gray-400 text-sm">Down</span>
            </div>
          </div>
        </div>
        <div className="grid grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 rounded p-3 border border-gray-700">
            <p className="text-gray-400 text-xs mb-1">High</p>
            <p className="text-white text-lg font-semibold">
              ${Math.max(...formattedData.map(d => d.high)).toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-800 rounded p-3 border border-gray-700">
            <p className="text-gray-400 text-xs mb-1">Low</p>
            <p className="text-white text-lg font-semibold">
              ${Math.min(...formattedData.map(d => d.low)).toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-800 rounded p-3 border border-gray-700">
            <p className="text-gray-400 text-xs mb-1">Open</p>
            <p className="text-white text-lg font-semibold">
              ${formattedData[0]?.open.toFixed(2)}
            </p>
          </div>
          <div className="bg-gray-800 rounded p-3 border border-gray-700">
            <p className="text-gray-400 text-xs mb-1">Close</p>
            <p className={`text-lg font-semibold ${
              formattedData[formattedData.length - 1]?.isUp
                ? 'text-green-400'
                : 'text-red-400'
            }`}>
              ${formattedData[formattedData.length - 1]?.close.toFixed(2)}
            </p>
          </div>
        </div>

        {/* Chart */}
        <div className="bg-gray-800 rounded border border-gray-700 p-4">
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={formattedData} margin={{ top: 20, right: 30, left: 0, bottom: 60 }}>
              <defs>
                <linearGradient id="colorUp" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                </linearGradient>
                <linearGradient id="colorDown" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#ef4444" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="#ef4444" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid
                strokeDasharray="3 3"
                stroke="#374151"
                vertical={true}
                horizontal={true}
              />
              <XAxis
                dataKey="time"
                stroke="#9ca3af"
                tick={{ fontSize: 12, fill: '#9ca3af' }}
                angle={-45}
                textAnchor="end"
                height={80}
              />
              <YAxis
                stroke="#9ca3af"
                tick={{ fontSize: 12, fill: '#9ca3af' }}
                domain={[minPrice, maxPrice]}
                width={80}
              />
              <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.1)' }} />
              <Bar
                dataKey="close"
                shape={<CustomCandlestick />}
                isAnimationActive={false}
              />
            </ComposedChart>
          </ResponsiveContainer>
        </div>

        {/* Footer Info */}
        <div className="mt-4 flex justify-between text-xs text-gray-500">
          <span>Total Candles: {formattedData.length}</span>
          <span>
            Up Trend: {formattedData.filter(d => d.isUp).length} | Down Trend: {formattedData.filter(d => !d.isUp).length}
          </span>
        </div>
      </div>
    </div>
  )
}

export default CandlestickChart
