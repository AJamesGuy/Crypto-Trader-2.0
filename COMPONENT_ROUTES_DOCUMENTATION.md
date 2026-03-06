# Components & Routes Documentation

## Overview
This document maps frontend components to their backend routes and data structures, detailing what data each component expects and where it comes from.

---

## Frontend Components

### 1. **CoinCard**
**Location:** `Frontend/src/components/CoinCard/CoinCard.jsx`

**Purpose:** Displays detailed cryptocurrency card with price, market cap, 24h volume, and changes.

**Props:**
- `crypto` (object): Cryptocurrency data object
- `onSelect` (function): Callback when card is clicked

**Data Structure Expected:**
```javascript
{
  id: number,
  name: string,
  symbol: string,
  image: string,
  price: number (required for price display),
  change_24h: number (required for change percentage),
  market_cap_rank: number,
  market_cap: number (required for stats),
  volume: number (required for stats),
  description?: string
}
```

**Required Backend Route:** `/dash/market-data/{crypto_id}`
- Returns the full market data object with all fields needed

**Current Issue:** When selecting from "Top Cryptocurrencies", receives partial crypto object instead of full market data

---

### 2. **CandlestickChart**
**Location:** `Frontend/src/components/CandlestickChart/CandlestickChart.jsx`

**Purpose:** Displays candlestick chart for cryptocurrency price over time.

**Props:**
- `data` (array): Array of candle data objects
- `cryptoName` (string): Name of cryptocurrency
- `timeframe` (string): Time period (default: '24h')

**Data Structure Expected:**
```javascript
[
  {
    time: string (timestamp),
    open: number,
    high: number,
    low: number,
    close: number,
    volume: number
  }
]
```

**Required Backend Route:** `/dash/market-data/{crypto_id}/candles?timeframe=24h`
- Returns array of OHLCV (Open, High, Low, Close, Volume) candle data

---

### 3. **SearchBar**
**Location:** `Frontend/src/components/SearchBar/SearchBar.jsx`

**Purpose:** Allows users to search for cryptocurrencies by name or symbol.

**Props:**
- `onSearch` (function): Callback when search result is selected
- `token` (string): Auth token

**Data Structure Expected (search results):**
```javascript
{
  id: number,
  name: string,
  symbol: string,
  image: string
}
```

**Required Backend Route:** `/dash/search?query={query}&limit=50`
- Returns array of matching cryptocurrencies

---

### 4. **Dashboard**
**Location:** `Frontend/src/pages/Dashboard.jsx`

**Purpose:** Main dashboard page coordinating all components and state management.

**State Variables:**
- `selectedCrypto`: Currently selected cryptocurrency (for CoinCard display)
- `candleData`: Chart data for selected cryptocurrency
- `cryptos`: All available cryptocurrencies
- `marketData`: Latest market data for all cryptocurrencies
- `cashBalance`: User's cash balance

**Key Functions:**
- `handleSearch(crypto)`: Handles search result selection
  - Calls `getCryptoMarketData(crypto.id)` → `/dash/market-data/{crypto_id}`
  - Sets `selectedCrypto` to market data object
  - Fetches candle data

- `handleCryptoSelect(crypto)`: Handles "Top Cryptocurrencies" selection
  - **ISSUE:** Only calls `fetchCandleData` without fetching full market data
  - Sets `selectedCrypto` to partial crypto object (missing price, change_24h, etc.)

---

## Backend Routes (Flask)

### Dashboard Routes (`app/blueprints/dashboard/routes.py`)

#### 1. **GET `/dash/cryptos`**
**Purpose:** Get all available cryptocurrencies

**Query Parameters:** None

**Response:**
```javascript
[
  {
    id: number,
    name: string,
    symbol: string,
    image: string,
    circulating_supply: number,
    total_supply: number,
    ath: number,
    ath_date: string,
    is_active: boolean
  }
]
```

**Used By:** Initial cryptocurrency list load

---

#### 2. **GET `/dash/market-data`**
**Purpose:** Get latest market data for all cryptocurrencies (ranked by market cap)

**Query Parameters:** None

**Response:**
```javascript
[
  {
    id: number,
    crypto_id: number,
    price: number,
    change_24h: number,
    market_cap: number,
    volume: number,
    timestamp: string,
    symbol: string,
    name: string,
    image: string,
    market_cap_rank: number
  }
]
```

**Used By:** 
- Dashboard sidebar "Top Cryptocurrencies" list
- Initial market data display

---

#### 3. **GET `/dash/market-data/{crypto_id}`**
**Purpose:** Get full market data for a specific cryptocurrency

**Query Parameters:** None

**Response:**
```javascript
{
  id: number,
  crypto_id: number,
  price: number,
  change_24h: number,
  market_cap: number,
  volume: number,
  timestamp: string,
  symbol: string,
  name: string,
  image: string,
  circulating_supply: number,
  total_supply: number,
  ath: number,
  ath_date: string
}
```

**Used By:** 
- `CoinCard` component (requires full market data)
- `handleSearch` callback

---

#### 4. **GET `/dash/market-data/{crypto_id}/candles?timeframe=24h`**
**Purpose:** Get candlestick/OHLCV data for a cryptocurrency

**Query Parameters:**
- `timeframe` (string): Time period ('24h', '1w', '1m', etc.)

**Response:**
```javascript
[
  {
    time: string (ISO format timestamp),
    open: number,
    high: number,
    low: number,
    close: number,
    volume: number
  }
]
```

**Used By:** `CandlestickChart` component

---

#### 5. **GET `/dash/search?query={query}&limit=50`**
**Purpose:** Search cryptocurrencies by name or symbol

**Query Parameters:**
- `query` (string): Search term
- `limit` (number): Maximum results (default: 50)

**Response:**
```javascript
[
  {
    id: number,
    name: string,
    symbol: string,
    image: string,
    circulating_supply: number,
    total_supply: number,
    ath: number,
    ath_date: string,
    is_active: boolean
  }
]
```

**Used By:** `SearchBar` component

---

#### 6. **GET `/dash/{user_id}/cash-balance`**
**Purpose:** Get user's cash balance

**Query Parameters:** None

**Response:**
```javascript
{
  cash_balance: number
}
```

**Used By:** Dashboard header balance display

---

## Data Flow Diagram

```
Dashboard.jsx
├── State: selectedCrypto (market data form market-data route)
├── State: candleData (from market-data/{id}/candles)
├── State: cryptos (from /dash/cryptos)
├── State: marketData (from /dash/market-data)
│
├── CoinCard
│   └── Displays: selectedCrypto data
│       Required: price, change_24h, market_cap, volume
│       From: /dash/market-data/{crypto_id}
│
├── CandlestickChart
│   └── Displays: candleData (OHLCV)
│       From: /dash/market-data/{crypto_id}/candles
│
├── SearchBar
│   └── Searches via: /dash/search
│       Returns: Limited crypto data (id, name, symbol, image)
│       On select: Calls handleSearch(crypto) 
│           → Fetches /dash/market-data/{crypto_id}
│           → Sets selectedCrypto
│
└── Top Cryptocurrencies List
    └── Source: marketData from /dash/market-data
        On click: Calls handleCryptoSelect(crypto)
            → ISSUE: Doesn't fetch full market data
            → selectedCrypto receives partial data
            → CoinCard fails to display price, changes, etc.
```

---

## Issues & Recommendations

### Issue: CoinCard Data Mismatch
**Problem:** When selecting from "Top Cryptocurrencies", `CoinCard` receives incomplete data.

**Root Cause:** 
- `handleCryptoSelect` sets `selectedCrypto` to the clicked item from the list (which only has basic data)
- `CoinCard` expects full market data with `price`, `change_24h`, `market_cap`, `volume` fields

**Solution:** Update `handleCryptoSelect` to fetch full market data:
```javascript
const handleCryptoSelect = async (crypto) => {
  try {
    const marketData = await dashboardAPI.getCryptoMarketData(crypto.id)
    setSelectedCrypto(marketData)
    fetchCandleData(crypto.id)
  } catch (err) {
    console.error('Error fetching market data:', err)
  }
}
```

This matches the behavior of `handleSearch` which already fetches full market data.

---

## API Service Methods (Frontend)

**Location:** `Frontend/src/services/api.js`

```javascript
dashboardAPI.getCryptos()
  → GET /dash/cryptos

dashboardAPI.getMarketData()
  → GET /dash/market-data

dashboardAPI.getCryptoMarketData(cryptoId)
  → GET /dash/market-data/{cryptoId}

dashboardAPI.getCandleData(cryptoId, timeframe)
  → GET /dash/market-data/{cryptoId}/candles?timeframe={timeframe}

dashboardAPI.searchCryptos(query, limit)
  → GET /dash/search?query={query}&limit={limit}

dashboardAPI.getCashBalance(userId)
  → GET /dash/{userId}/cash-balance
```

---

## Summary Table

| Component | Route | Purpose | Data Fields Required |
|-----------|-------|---------|---------------------|
| CoinCard | `/dash/market-data/{id}` | Display crypto details | price, change_24h, market_cap, volume |
| CandlestickChart | `/dash/market-data/{id}/candles` | Display chart | time, open, high, low, close, volume |
| SearchBar | `/dash/search` | Find crypto | id, name, symbol, image |
| Top Cryptos List | `/dash/market-data` | Show top cryptos | Standard market data |
| Dashboard | `/dash/cryptos` | Initial load | Basic crypto info |
| Cash Balance | `/dash/{user_id}/cash-balance` | Show balance | cash_balance |
