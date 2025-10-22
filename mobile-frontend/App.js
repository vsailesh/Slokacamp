# React Native E-Learning App for Ayurveda
# Main App Component with Authentication and Navigation

import React, { useEffect, useState } from 'react';
import {
  NavigationContainer,
  createBottomTabNavigator,
  createStackNavigator,
} from '@react-navigation/native';
import {
  View,
  Text,
  StyleSheet,
  StatusBar,
  Alert,
  Platform,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { Provider } from 'react-redux';
import { store } from './src/store/store';

// Screens
import LoginScreen from './src/screens/LoginScreen';
import RegisterScreen from './src/screens/RegisterScreen';
import DashboardScreen from './src/screens/DashboardScreen';
import CoursesScreen from './src/screens/CoursesScreen';
import CourseDetailScreen from './src/screens/CourseDetailScreen';
import VideoPlayerScreen from './src/screens/VideoPlayerScreen';
import ProfileScreen from './src/screens/ProfileScreen';
import SubscriptionScreen from './src/screens/SubscriptionScreen';

// Components
import LoadingSpinner from './src/components/LoadingSpinner';
import DeviceManager from './src/services/DeviceManager';
import ScreenCaptureDetector from './src/services/ScreenCaptureDetector';

// Services
import AuthService from './src/services/AuthService';

// Navigation
const Stack = createStackNavigator();
const Tab = createBottomTabNavigator();

// Bottom Tab Navigator
function TabNavigator() {
  return (
    <Tab.Navigator
      screenOptions={{
        tabBarStyle: {
          backgroundColor: '#ffffff',
          borderTopColor: '#e0e0e0',
          paddingBottom: Platform.OS === 'ios' ? 20 : 10,
          height: Platform.OS === 'ios' ? 90 : 70,
        },
        tabBarActiveTintColor: '#ff6b35',
        tabBarInactiveTintColor: '#666666',
        headerShown: false,
      }}
    >
      <Tab.Screen 
        name="Dashboard" 
        component={DashboardScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>🏠</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Courses" 
        component={CoursesScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>📚</Text>
          ),
        }}
      />
      <Tab.Screen 
        name="Profile" 
        component={ProfileScreen}
        options={{
          tabBarIcon: ({ color, size }) => (
            <Text style={{ color, fontSize: size }}>👤</Text>
          ),
        }}
      />
    </Tab.Navigator>
  );
}

// Auth Stack Navigator
function AuthStack() {
  return (
    <Stack.Navigator 
      screenOptions={{ 
        headerShown: false,
        cardStyle: { backgroundColor: '#ffffff' }
      }}
    >
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Register" component={RegisterScreen} />
    </Stack.Navigator>
  );
}

// Main App Stack Navigator
function AppStack() {
  return (
    <Stack.Navigator 
      screenOptions={{ 
        headerShown: false,
        cardStyle: { backgroundColor: '#ffffff' }
      }}
    >
      <Stack.Screen name="MainTabs" component={TabNavigator} />
      <Stack.Screen name="CourseDetail" component={CourseDetailScreen} />
      <Stack.Screen 
        name="VideoPlayer" 
        component={VideoPlayerScreen}
        options={{ 
          presentation: 'fullScreenModal',
          gestureEnabled: false // Prevent swipe to dismiss during video playback
        }}
      />
      <Stack.Screen name="Subscription" component={SubscriptionScreen} />
    </Stack.Navigator>
  );
}

// Main App Component
export default function App() {
  const [isLoading, setIsLoading] = useState(true);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [screenCaptureDetected, setScreenCaptureDetected] = useState(false);

  useEffect(() => {
    initializeApp();
  }, []);

  const initializeApp = async () => {
    try {
      // Initialize device management
      await DeviceManager.initialize();
      
      // Check authentication status
      const token = await AsyncStorage.getItem('access_token');
      const refreshToken = await AsyncStorage.getItem('refresh_token');
      
      if (token && refreshToken) {
        // Validate token
        const isValid = await AuthService.validateToken(token);
        if (isValid) {
          setIsAuthenticated(true);
        } else {
          // Try to refresh token
          const refreshed = await AuthService.refreshToken(refreshToken);
          setIsAuthenticated(refreshed);
        }
      }
      
      // Initialize screen capture detection
      ScreenCaptureDetector.startMonitoring((detected) => {
        setScreenCaptureDetected(detected);
        if (detected) {
          Alert.alert(
            'Screen Recording Detected',
            'For security reasons, video playback will be paused while screen recording is active.',
            [{ text: 'OK' }]
          );
        }
      });
      
    } catch (error) {
      console.error('App initialization error:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Show loading screen while initializing
  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <LoadingSpinner size="large" color="#ff6b35" />
        <Text style={styles.loadingText}>Initializing SlokaCamp...</Text>
      </View>
    );
  }

  // Show screen capture warning overlay
  const ScreenCaptureOverlay = () => {
    if (!screenCaptureDetected) return null;
    
    return (
      <View style={styles.screenCaptureOverlay}>
        <View style={styles.screenCaptureModal}>
          <Text style={styles.screenCaptureTitle}>🚫 Screen Recording Detected</Text>
          <Text style={styles.screenCaptureMessage}>
            For content protection, video playback is disabled while screen recording is active.
            Please stop screen recording to continue.
          </Text>
        </View>
      </View>
    );
  };

  return (
    <Provider store={store}>
      <NavigationContainer>
        <StatusBar 
          barStyle="dark-content" 
          backgroundColor="#ffffff" 
          translucent={false} 
        />
        
        {isAuthenticated ? <AppStack /> : <AuthStack />}
        
        {/* Screen Capture Detection Overlay */}
        <ScreenCaptureOverlay />
        
      </NavigationContainer>
    </Provider>
  );
}

const styles = StyleSheet.create({
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#ffffff',
  },
  loadingText: {
    marginTop: 16,
    fontSize: 16,
    color: '#666666',
    fontFamily: 'System',
  },
  screenCaptureOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.8)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 9999,
  },
  screenCaptureModal: {
    backgroundColor: '#ffffff',
    marginHorizontal: 32,
    padding: 24,
    borderRadius: 16,
    alignItems: 'center',
  },
  screenCaptureTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ff3333',
    marginBottom: 16,
    textAlign: 'center',
  },
  screenCaptureMessage: {
    fontSize: 16,
    color: '#333333',
    textAlign: 'center',
    lineHeight: 24,
  },
});