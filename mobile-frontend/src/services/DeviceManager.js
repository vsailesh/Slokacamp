// Device Manager for single-device playback enforcement
// Handles device registration, authentication, and policy enforcement

import AsyncStorage from '@react-native-async-storage/async-storage';
import DeviceInfo from 'react-native-device-info';
import { Platform, Alert } from 'react-native';
import PushNotification from 'react-native-push-notification';
import messaging from '@react-native-firebase/messaging';

class DeviceManager {
  constructor() {
    this.deviceId = null;
    this.deviceInfo = {};
    this.pushToken = null;
  }

  async initialize() {
    try {
      // Get or create device ID
      this.deviceId = await this.getOrCreateDeviceId();
      
      // Collect device information
      this.deviceInfo = await this.collectDeviceInfo();
      
      // Request push notification permissions and get token
      await this.setupPushNotifications();
      
      console.log('Device Manager initialized:', {
        deviceId: this.deviceId,
        deviceInfo: this.deviceInfo,
      });
      
    } catch (error) {
      console.error('Device Manager initialization failed:', error);
      throw error;
    }
  }

  async getOrCreateDeviceId() {
    try {
      // Try to get existing device ID from storage
      let deviceId = await AsyncStorage.getItem('device_id');
      
      if (!deviceId) {
        // Generate new device ID using device unique identifier
        const uniqueId = await DeviceInfo.getUniqueId();
        const timestamp = Date.now();
        deviceId = `${uniqueId}-${timestamp}`;
        
        // Save device ID to storage
        await AsyncStorage.setItem('device_id', deviceId);
      }
      
      return deviceId;
    } catch (error) {
      console.error('Error getting device ID:', error);
      // Fallback to timestamp-based ID
      return `fallback-${Date.now()}`;
    }
  }

  async collectDeviceInfo() {
    try {
      const [deviceName, systemName, systemVersion, model, brand] = await Promise.all([
        DeviceInfo.getDeviceName(),
        DeviceInfo.getSystemName(),
        DeviceInfo.getSystemVersion(),
        DeviceInfo.getModel(),
        DeviceInfo.getBrand(),
      ]);

      return {
        deviceName: deviceName || 'Unknown Device',
        platform: Platform.OS,
        osVersion: `${systemName} ${systemVersion}`,
        deviceModel: model,
        brand,
        appVersion: DeviceInfo.getVersion(),
        buildNumber: DeviceInfo.getBuildNumber(),
      };
    } catch (error) {
      console.error('Error collecting device info:', error);
      return {
        deviceName: 'Unknown Device',
        platform: Platform.OS,
        osVersion: 'Unknown',
        deviceModel: 'Unknown',
        brand: 'Unknown',
        appVersion: '1.0.0',
        buildNumber: '1',
      };
    }
  }

  async setupPushNotifications() {
    try {
      // Request permission (iOS)
      if (Platform.OS === 'ios') {
        const authStatus = await messaging().requestPermission();
        const enabled =
          authStatus === messaging.AuthorizationStatus.AUTHORIZED ||
          authStatus === messaging.AuthorizationStatus.PROVISIONAL;

        if (!enabled) {
          console.log('Push notification permission denied');
          return;
        }
      }

      // Get FCM token
      const token = await messaging().getToken();
      this.pushToken = token;
      
      // Save token to storage
      await AsyncStorage.setItem('push_token', token);
      
      // Listen for token refresh
      messaging().onTokenRefresh((newToken) => {
        this.pushToken = newToken;
        AsyncStorage.setItem('push_token', newToken);
        // Update token on server
        this.updatePushTokenOnServer(newToken);
      });
      
      console.log('Push notification token:', token);
      
    } catch (error) {
      console.error('Push notification setup failed:', error);
    }
  }

  async updatePushTokenOnServer(token) {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      if (!accessToken) return;

      const response = await fetch(`${API_BASE_URL}/devices/${this.deviceId}/`, {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          push_token: token,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to update push token on server');
      }
    } catch (error) {
      console.error('Error updating push token on server:', error);
    }
  }

  async registerDevice(userId) {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      
      const deviceData = {
        device_id: this.deviceId,
        device_name: this.deviceInfo.deviceName,
        platform: this.deviceInfo.platform,
        os_version: this.deviceInfo.osVersion,
        app_version: this.deviceInfo.appVersion,
        device_model: this.deviceInfo.deviceModel,
        push_token: this.pushToken || '',
        device_fingerprint: {
          brand: this.deviceInfo.brand,
          model: this.deviceInfo.deviceModel,
          build_number: this.deviceInfo.buildNumber,
        },
      };

      const response = await fetch(`${API_BASE_URL}/devices/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deviceData),
      });

      const result = await response.json();

      if (!response.ok) {
        if (response.status === 409) {
          // Device already exists, handle device policy
          return this.handleDeviceConflict(result);
        }
        throw new Error(result.message || 'Device registration failed');
      }

      // Save device registration info
      await AsyncStorage.setItem('device_registered', 'true');
      await AsyncStorage.setItem('device_server_id', result.id);
      
      return result;
    } catch (error) {
      console.error('Device registration failed:', error);
      throw error;
    }
  }

  async handleDeviceConflict(conflictData) {
    return new Promise((resolve, reject) => {
      Alert.alert(
        'Device Limit Reached',
        'You can only use SlokaCamp on one device at a time. Would you like to transfer your access to this device?',
        [
          {
            text: 'Cancel',
            style: 'cancel',
            onPress: () => reject(new Error('User cancelled device transfer')),
          },
          {
            text: 'Transfer Access',
            onPress: async () => {
              try {
                const result = await this.transferDeviceAccess();
                resolve(result);
              } catch (error) {
                reject(error);
              }
            },
          },
        ],
        { cancelable: false }
      );
    });
  }

  async transferDeviceAccess() {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      
      const response = await fetch(`${API_BASE_URL}/devices/transfer/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          new_device_id: this.deviceId,
          device_name: this.deviceInfo.deviceName,
          platform: this.deviceInfo.platform,
          reason: 'manual_transfer',
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || 'Device transfer failed');
      }

      // Update local storage
      await AsyncStorage.setItem('device_registered', 'true');
      await AsyncStorage.setItem('device_server_id', result.device.id);
      
      return result;
    } catch (error) {
      console.error('Device transfer failed:', error);
      throw error;
    }
  }

  async checkDeviceStatus() {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      const deviceServerId = await AsyncStorage.getItem('device_server_id');
      
      if (!deviceServerId) {
        return { is_active: false };
      }

      const response = await fetch(`${API_BASE_URL}/devices/${deviceServerId}/`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });

      if (response.ok) {
        return await response.json();
      } else {
        return { is_active: false };
      }
    } catch (error) {
      console.error('Error checking device status:', error);
      return { is_active: false };
    }
  }

  async updateLastSeen() {
    try {
      const accessToken = await AsyncStorage.getItem('access_token');
      const deviceServerId = await AsyncStorage.getItem('device_server_id');
      
      if (!deviceServerId) return;

      await fetch(`${API_BASE_URL}/devices/${deviceServerId}/heartbeat/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
        },
      });
    } catch (error) {
      console.error('Error updating device heartbeat:', error);
    }
  }

  getDeviceId() {
    return this.deviceId;
  }

  getDeviceInfo() {
    return this.deviceInfo;
  }

  getPushToken() {
    return this.pushToken;
  }
}

// Singleton instance
const deviceManager = new DeviceManager();
export default deviceManager;

// Configuration
const API_BASE_URL = __DEV__ 
  ? 'http://localhost:8000/api'
  : 'https://api.slokacamp.com/api';