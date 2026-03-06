import React, { useState, useEffect } from 'react';
import { CartesianGrid, XAxis, YAxis, Bar, ErrorBar, ComposedChart, Line, Cell, Tooltip } from 'recharts';
import { dashboardAPI } from '../../services/api'; // Adjust the import path based on your project structure (from api.js)

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    const entry = payload[0].payload;
    // Reconstruct original values for tooltip
    const originalOpen = entry.up ? entry.low : entry.high;
    const originalClose = entry.up ? entry.high : entry.low;
    const originalLow = Math.min(entry.low, entry.high) - (entry.errorLowUp || entry.errorLowDown || 0) * 2;
    const originalHigh = Math.max(entry.low, entry.high) + (entry.errorHighUp || entry.errorHighDown || 0) * 2;
    const date = new Date(entry.date).toLocaleString();

    return (
      <div style={{ backgroundColor: 'white', border: '1px solid #ccc', padding: '10px' }}>
        <p><strong>Date:</strong> {date}</p>
        <p><strong>Open:</strong> ${originalOpen.toFixed(2)}</p>
        <p><strong>Close:</strong> ${originalClose.toFixed(2)}</p>
        <p><strong>Low:</strong> ${originalLow.toFixed(2)}</p>
        <p><strong>High:</strong> ${originalHigh.toFixed(2)}</p>
      </div>
    );
  }
  return null;
};

const CandlestickChart = ({ 
  cryptoId, 
  timeframe = '24h',
  width = 800,
  height = 400,
  bullishColor = '#00906F',
  bearishColor = '#B23507',
  dynamicPadding = true
}) => {
  const [rawData, setRawData] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!cryptoId) {
      console.warn('CandlestickChart: cryptoId prop is missing');
      setError('Invalid cryptocurrency ID');
      return;
    }

    setLoading(true);
    setError(null);
    
    console.log('Fetching candle data for cryptoId:', cryptoId, 'timeframe:', timeframe);
    
    dashboardAPI.getCandleData(cryptoId, timeframe)
      .then((candles) => {
        console.log('Candle data received:', candles);
        if (!candles || candles.length === 0) {
          setError('No candle data available for this cryptocurrency');
          setRawData([]);
          return;
        }
        
        const processedData = candles.map((candle) => ({
          date: new Date(candle.time).getTime(),
          open: candle.open,
          high: candle.high,
          low: candle.low,
          close: candle.close,
        }));
        setRawData(processedData);
      })
      .catch((error) => {
        console.error('Error fetching candle data:', error);
        console.error('Error details:', error.response?.data || error.message);
        setError(`Failed to load chart data: ${error.response?.data?.message || error.message || 'Unknown error'}`);
        setRawData([]);
      })
      .finally(() => setLoading(false));
  }, [cryptoId, timeframe]);

  // Format date based on timeframe for better UX
  const formatDateByTimeframe = (tick) => {
    const date = new Date(tick);
    if (timeframe === '24h') {
      return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    } else if (timeframe === '7d') {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    } else {
      return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
    }
  };

  if (loading) {
    return (
      <div style={{ 
        width, 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px'
      }}>
        <p style={{ color: '#666', fontSize: '16px' }}>Loading chart data...</p>
      </div>
    );
  }

  if (error || !rawData.length) {
    return (
      <div style={{ 
        width, 
        height, 
        display: 'flex', 
        alignItems: 'center', 
        justifyContent: 'center',
        backgroundColor: '#f5f5f5',
        borderRadius: '8px',
        border: '1px solid #e0e0e0'
      }}>
        <p style={{ color: '#d32f2f', fontSize: '16px', textAlign: 'center', padding: '20px' }}>
          {error || 'Unable to load chart data'}
        </p>
      </div>
    );
  }

  const transformedData = rawData.map((point) => ({
    date: point.date,
    low: Math.min(point.close, point.open),
    high: Math.max(point.close, point.open),
    height: Math.abs(point.close - point.open),
    errorLineHigh: (point.high - Math.max(point.close, point.open)) / 2 + Math.max(point.close, point.open),
    errorLineLow: Math.min(point.close, point.open) - (Math.min(point.close, point.open) - point.low) / 2,
    errorLowUp: point.close > point.open ? (Math.min(point.close, point.open) - point.low) / 2 : null,
    errorHighUp: point.close > point.open ? (point.high - Math.max(point.close, point.open)) / 2 : null,
    errorLowDown: point.close <= point.open ? (Math.min(point.close, point.open) - point.low) / 2 : null,
    errorHighDown: point.close <= point.open ? (point.high - Math.max(point.close, point.open)) / 2 : null,
    up: point.close > point.open,
  }));

  // Dynamic padding calculation
  const allValues = rawData.flatMap(d => [d.high, d.low]);
  const minValue = Math.min(...allValues);
  const maxValue = Math.max(...allValues);
  const range = maxValue - minValue;
  const padding = dynamicPadding ? range * 0.1 : 100;
  
  const minLow = minValue - padding;
  const maxHigh = maxValue + padding;

  const formatDollars = (tick) => `$${tick.toFixed(0)}`;

  return (
    <ComposedChart width={width} height={height} data={transformedData}>
      <CartesianGrid horizontal={false} strokeDasharray="1 15" />
      <XAxis dataKey="date" tickFormatter={formatDateByTimeframe} />
      <YAxis domain={[minLow, maxHigh]} tickFormatter={formatDollars} />
      <Tooltip content={<CustomTooltip />} />

      {/* Invisible base bar */}
      <Bar dataKey="low" fillOpacity={0} stackId="stack" />

      {/* Body bar */}
      <Bar dataKey="height" stackId="stack" barSize={10}>
        {transformedData.map((entry, index) => (
          <Cell key={`cell-${index}`} fill={entry.up ? bullishColor : bearishColor} />
        ))}
      </Bar>

      {/* Wicks for down (bearish) */}
      <Line dataKey="errorLineHigh" stroke="none" isAnimationActive={false} dot={false}>
        <ErrorBar dataKey="errorHighDown" width={3} strokeWidth={2} stroke={bearishColor} />
      </Line>
      <Line dataKey="errorLineLow" stroke="none" isAnimationActive={false} dot={false}>
        <ErrorBar dataKey="errorLowDown" width={3} strokeWidth={2} stroke={bearishColor} />
      </Line>

      {/* Wicks for up (bullish) */}
      <Line dataKey="errorLineHigh" stroke="none" isAnimationActive={false} dot={false}>
        <ErrorBar dataKey="errorHighUp" width={3} strokeWidth={2} stroke={bullishColor} />
      </Line>
      <Line dataKey="errorLineLow" stroke="none" isAnimationActive={false} dot={false}>
        <ErrorBar dataKey="errorLowUp" width={3} strokeWidth={2} stroke={bullishColor} />
      </Line>
    </ComposedChart>
  );
};

export default CandlestickChart;