# Authentication Service for React Native
# Handles all authentication-related API calls and token management

import AsyncStorage from '@react-native-async-storage/async-storage';
import DeviceManager from './DeviceManager';

const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api'
  : 'https://api.slokacamp.com/api';

class AuthService {
  constructor() {
    this.baseURL = API_BASE_URL;
  }

  async makeRequest(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    const defaultHeaders = {
      'Content-Type': 'application/json',
    };

    // Add authentication header if token exists
    const accessToken = await AsyncStorage.getItem('access_token');
    if (accessToken && !options.skipAuth) {
      defaultHeaders.Authorization = `Bearer ${accessToken}`;
    }

    const config = {
      method: 'GET',
      headers: {
        ...defaultHeaders,
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      const data = await response.json();

      if (response.ok) {
        return {
          success: true,
          data,
          status: response.status,
        };
      } else {
        // Handle token refresh for 401 errors
        if (response.status === 401 && !options.skipRefresh) {
          const refreshed = await this.refreshToken();
          if (refreshed) {
            // Retry the original request
            return this.makeRequest(endpoint, { ...options, skipRefresh: true });
          }
        }

        return {
          success: false,
          error: data.error || 'Request failed',
          message: data.message || data.detail || 'An error occurred',
          status: response.status,
          data,
        };
      }
    } catch (error) {
      console.error('Request failed:', error);
      return {
        success: false,
        error: 'Network error',
        message: 'Please check your internet connection and try again.',
      };
    }
  }

  async login(credentials) {
    return this.makeRequest('/auth/login/', {
      method: 'POST',
      body: JSON.stringify(credentials),
      skipAuth: true,
    });
  }

  async register(userData) {
    return this.makeRequest('/auth/register/', {
      method: 'POST',
      body: JSON.stringify(userData),
      skipAuth: true,
    });
  }

  async socialAuth(socialData) {
    return this.makeRequest('/auth/social/', {
      method: 'POST',
      body: JSON.stringify(socialData),
      skipAuth: true,
    });
  }

  async refreshToken() {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      if (!refreshToken) {
        await this.logout();
        return false;
      }

      const response = await this.makeRequest('/auth/refresh/', {
        method: 'POST',
        body: JSON.stringify({ refresh: refreshToken }),
        skipAuth: true,
        skipRefresh: true,
      });

      if (response.success) {
        await AsyncStorage.setItem('access_token', response.data.access);
        return true;
      } else {
        await this.logout();
        return false;
      }
    } catch (error) {
      console.error('Token refresh failed:', error);
      await this.logout();
      return false;
    }
  }

  async validateToken(token) {
    try {
      const response = await this.makeRequest('/auth/validate/', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
        skipRefresh: true,
      });

      return response.success;
    } catch (error) {
      return false;
    }
  }

  async logout() {
    try {
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      
      if (refreshToken) {
        await this.makeRequest('/auth/logout/', {
          method: 'POST',
          body: JSON.stringify({ refresh: refreshToken }),
        });
      }
    } catch (error) {
      console.error('Logout request failed:', error);
    } finally {
      // Clear local storage regardless of API call success
      await AsyncStorage.multiRemove([
        'access_token',
        'refresh_token',
        'user_data',
        'device_id',
      ]);
    }
  }

  async getCurrentUser() {
    try {
      const userData = await AsyncStorage.getItem('user_data');
      return userData ? JSON.parse(userData) : null;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  async updateProfile(profileData) {
    return this.makeRequest('/auth/profile/', {
      method: 'PATCH',
      body: JSON.stringify(profileData),
    });
  }

  async changePassword(passwordData) {
    return this.makeRequest('/auth/change-password/', {
      method: 'POST',
      body: JSON.stringify(passwordData),
    });
  }

  async requestPasswordReset(email) {
    return this.makeRequest('/auth/password-reset/', {
      method: 'POST',
      body: JSON.stringify({ email }),
      skipAuth: true,
    });
  }

  async confirmPasswordReset(resetData) {
    return this.makeRequest('/auth/password-reset-confirm/', {
      method: 'POST',
      body: JSON.stringify(resetData),
      skipAuth: true,
    });
  }

  async verifyEmail(token) {
    return this.makeRequest('/auth/verify-email/', {
      method: 'POST',
      body: JSON.stringify({ token }),
      skipAuth: true,
    });
  }

  async resendVerificationEmail(email) {
    return this.makeRequest('/auth/resend-verification/', {
      method: 'POST',
      body: JSON.stringify({ email }),
      skipAuth: true,
    });
  }

  // Device management
  async registerDevice(deviceData) {
    return this.makeRequest('/devices/', {
      method: 'POST',
      body: JSON.stringify(deviceData),
    });
  }

  async getDevices() {
    return this.makeRequest('/devices/');
  }

  async deactivateDevice(deviceId) {
    return this.makeRequest(`/devices/${deviceId}/`, {
      method: 'DELETE',
    });
  }

  async transferDevice(transferData) {
    return this.makeRequest('/devices/transfer/', {
      method: 'POST',
      body: JSON.stringify(transferData),
    });
  }

  // Helper methods
  async isAuthenticated() {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      
      if (!accessToken || !refreshToken) {
        return false;
      }

      // Validate current token
      const isValid = await this.validateToken(accessToken);
      if (isValid) {
        return true;
      }

      // Try to refresh token
      return await this.refreshToken();
    } catch (error) {
      console.error('Authentication check failed:', error);
      return false;
    }
  }

  async getAuthHeaders() {
    const accessToken = await AsyncStorage.getItem('access_token');
    return accessToken 
      ? { Authorization: `Bearer ${accessToken}` }
      : {};
  }

  // Token management
  async getAccessToken() {
    return AsyncStorage.getItem('access_token');
  }

  async setTokens(accessToken, refreshToken) {
    await AsyncStorage.multiSet([
      ['access_token', accessToken],
      ['refresh_token', refreshToken],
    ]);
  }

  async clearTokens() {
    await AsyncStorage.multiRemove([
      'access_token',
      'refresh_token',
    ]);
  }

  // Subscription helpers
  async getUserSubscription() {
    return this.makeRequest('/subscriptions/current/');
  }

  async isSubscriptionActive() {
    try {
      const response = await this.getUserSubscription();
      return response.success && response.data && response.data.is_active;
    } catch (error) {
      return false;
    }
  }
}

// Singleton instance
const authService = new AuthService();
export default authService;