/**
 * Format currency values
 */
export const formatCurrency = (value) => {
  if (!value) return '$0.00'
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(value)
}

/**
 * Format large numbers with abbreviations (K, M, B)
 */
export const formatLargeNumber = (value) => {
  if (!value) return '0'
  if (value >= 1e9) return (value / 1e9).toFixed(2) + 'B'
  if (value >= 1e6) return (value / 1e6).toFixed(2) + 'M'
  if (value >= 1e3) return (value / 1e3).toFixed(2) + 'K'
  return value.toFixed(2)
}

/**
 * Format percentage
 */
export const formatPercentage = (value) => {
  if (!value) return '0%'
  return (value > 0 ? '+' : '') + value.toFixed(2) + '%'
}

/**
 * Format crypto amounts
 */
export const formatCryptoAmount = (value, decimals = 8) => {
  if (!value) return '0'
  return parseFloat(value).toFixed(decimals)
}

/**
 * Format date
 */
export const formatDate = (date) => {
  if (!date) return ''
  return new Intl.DateTimeFormat('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  }).format(new Date(date))
}

/**
 * Get color class based on value (positive/negative)
 */
export const getColorClass = (value) => {
  if (!value) return ''
  return value >= 0 ? 'positive' : 'negative'
}

/**
 * Format order status for display
 */
export const formatOrderStatus = (status) => {
  const statusMap = {
    pending: 'Pending',
    executed: 'Executed',
    cancelled: 'Cancelled',
    failed: 'Failed'
  }
  return statusMap[status] || status
}
