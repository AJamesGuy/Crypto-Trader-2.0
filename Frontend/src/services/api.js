import axios from 'axios';

const API_BASE = import.meta.env.VITE_API_URL || 'http://127.0.0.1:5000';

// Create axios instance with base configuration
const axiosInstance = axios.create({
  baseURL: API_BASE,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests automatically
axiosInstance.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle errors globally
axiosInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      // Clear token and redirect to login if unauthorized
      localStorage.removeItem('token');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  signup: async (username, email, password, confirmPassword) => {
    try {
      const response = await axiosInstance.post('/auth/signup', {
        username,
        email,
        password,
        password_confirm: confirmPassword,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Signup failed' };
    }
  },

  login: async (username, password) => {
    try {
      const response = await axiosInstance.post('/auth/login', {
        username,
        password,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Login failed' };
    }
  },

  getProfile: async (userId) => {
    try {
      const response = await axiosInstance.get(`/auth/${userId}/profile`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch profile' };
    }
  },
};

// Dashboard APIs
export const dashboardAPI = {
  getCryptos: async () => {
    try {
      const response = await axiosInstance.get('/dash/cryptos');
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch cryptocurrencies' };
    }
  },

  getMarketData: async () => {
    try {
      const response = await axiosInstance.get('/dash/market-data');
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch market data' };
    }
  },

  searchCryptos: async (query, limit = 50) => {
    try {
      const response = await axiosInstance.get('/dash/search', {
        params: { query, limit },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Search failed' };
    }
  },

  getCryptoMarketData: async (cryptoId) => {
    try {
      const response = await axiosInstance.get(`/dash/market-data/${cryptoId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch crypto market data' };
    }
  },

  getCashBalance: async (userId) => {
    try {
      const response = await axiosInstance.get(`/dash/${userId}/cash-balance`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch cash balance' };
    }
  },

  getCandleData: async (cryptoId, timeframe = '24h') => {
    try {
      const response = await axiosInstance.get(`/dash/market-data/${cryptoId}/candles`, {
        params: { timeframe },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch candle data' };
    }
  },
};

// Trade APIs
export const tradeAPI = {
  placeOrder: async (userId, data) => {
    try {
      const response = await axiosInstance.post(`/trade/${userId}/order`, {
        crypto_id: data.crypto_id,
        order_type: data.order_type,
        quantity: data.quantity,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to place order' };
    }
  },

  getOrders: async (userId, page = 1, perPage = 10, status = '') => {
    try {
      const params = { page, per_page: perPage };
      if (status) {
        params.status = status;
      }
      const response = await axiosInstance.get(`/trade/${userId}/orders`, { params });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch orders' };
    }
  },

  getOrder: async (userId, orderId) => {
    try {
      const response = await axiosInstance.get(`/trade/${userId}/order/${orderId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch order' };
    }
  },

  executeOrder: async (userId, orderId) => {
    try {
      const response = await axiosInstance.post(`/trade/${userId}/order/${orderId}/execute`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to execute order' };
    }
  },

  cancelOrder: async (userId, orderId) => {
    try {
      const response = await axiosInstance.post(`/trade/${userId}/order/${orderId}/cancel`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to cancel order' };
    }
  },
};

// Portfolio APIs
export const portfolioAPI = {
  getPortfolio: async (userId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch portfolio' };
    }
  },

  getHoldings: async (userId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}/holdings`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch holdings' };
    }
  },

  getPerformance: async (userId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}/performance`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch performance data' };
    }
  },

  getBreakdown: async (userId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}/breakdown`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch breakdown' };
    }
  },

  getAsset: async (userId, assetId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}/asset/${assetId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch asset' };
    }
  },

  getAssets: async (userId) => {
    try {
      const response = await axiosInstance.get(`/portfolio/${userId}/assets`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch assets' };
    }
  },
};

// Settings APIs
export const settingsAPI = {
  updateProfile: async (userId, data) => {
    try {
      const response = await axiosInstance.put(`/settings/${userId}/update-profile`, {
        username: data.username,
        email: data.email,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to update profile' };
    }
  },

  changePassword: async (userId, data) => {
    try {
      const response = await axiosInstance.post(`/settings/${userId}/change-password`, {
        current_password: data.currentPassword,
        new_password: data.newPassword,
        confirm_password: data.confirmPassword,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to change password' };
    }
  },

  resetBalance: async (userId) => {
    try {
      const response = await axiosInstance.post(`/settings/${userId}/reset-balance`, {
        confirm: true,
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to reset balance' };
    }
  },

  deleteAccount: async (userId, data) => {
    try {
      const response = await axiosInstance.delete(`/settings/${userId}/delete-account`, {
        data: {
          password: data.password,
          confirm: data.confirm,
        },
      });
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to delete account' };
    }
  },

  getSettings: async (userId) => {
    try {
      const response = await axiosInstance.get(`/settings/${userId}`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch settings' };
    }
  },

  getSecurity: async (userId) => {
    try {
      const response = await axiosInstance.get(`/settings/${userId}/security`);
      return response.data;
    } catch (error) {
      throw error.response?.data || { message: 'Failed to fetch security settings' };
    }
  },
};
