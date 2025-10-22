# React Native Login Screen
# Handles email/password and social authentication with device registration

import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TextInput,
  StyleSheet,
  Alert,
  KeyboardAvoidingView,
  Platform,
  ScrollView,
  TouchableOpacity,
  ActivityIndicator,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { GoogleSignin } from '@react-native-google-signin/google-signin';
import { LoginManager, AccessToken } from 'react-native-fbsdk-next';
import { appleAuth } from '@invertase/react-native-apple-authentication';
import DeviceManager from '../services/DeviceManager';
import AuthService from '../services/AuthService';

const LoginScreen = ({ navigation }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  useEffect(() => {
    // Configure Google Sign In
    GoogleSignin.configure({
      webClientId: '1234567890-abcdefghijklmnop.apps.googleusercontent.com', // Replace with actual
      offlineAccess: true,
      hostedDomain: '',
      forceCodeForRefreshToken: true,
    });
  }, []);

  const handleEmailLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }

    if (!isValidEmail(email)) {
      Alert.alert('Error', 'Please enter a valid email address');
      return;
    }

    setIsLoading(true);

    try {
      const deviceId = DeviceManager.getDeviceId();
      const deviceInfo = DeviceManager.getDeviceInfo();
      const pushToken = DeviceManager.getPushToken();

      const loginData = {
        email: email.toLowerCase().trim(),
        password,
        device_id: deviceId,
        device_name: deviceInfo.deviceName,
        platform: deviceInfo.platform,
        push_token: pushToken || '',
      };

      const response = await AuthService.login(loginData);

      if (response.success) {
        // Store tokens
        await AsyncStorage.multiSet([
          ['access_token', response.data.access],
          ['refresh_token', response.data.refresh],
          ['user_data', JSON.stringify(response.data.user)],
          ['device_id', response.data.device_id],
        ]);

        // Navigate to main app
        navigation.replace('MainTabs');
      } else {
        handleLoginError(response.error, response.message);
      }
    } catch (error) {
      console.error('Login error:', error);
      Alert.alert('Login Failed', 'An unexpected error occurred. Please try again.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleGoogleLogin = async () => {
    setIsLoading(true);

    try {
      // Check if device is signed in
      await GoogleSignin.hasPlayServices();
      
      // Sign in
      const userInfo = await GoogleSignin.signIn();
      const tokens = await GoogleSignin.getTokens();

      const deviceId = DeviceManager.getDeviceId();
      const deviceInfo = DeviceManager.getDeviceInfo();
      const pushToken = DeviceManager.getPushToken();

      const socialAuthData = {
        provider: 'google',
        access_token: tokens.accessToken,
        device_id: deviceId,
        device_name: deviceInfo.deviceName,
        platform: deviceInfo.platform,
        push_token: pushToken || '',
      };

      const response = await AuthService.socialAuth(socialAuthData);

      if (response.success) {
        await AsyncStorage.multiSet([
          ['access_token', response.data.access],
          ['refresh_token', response.data.refresh],
          ['user_data', JSON.stringify(response.data.user)],
          ['device_id', response.data.device_id],
        ]);

        navigation.replace('MainTabs');
      } else {
        handleLoginError(response.error, response.message);
      }
    } catch (error) {
      console.error('Google login error:', error);
      if (error.code === statusCodes.SIGN_IN_CANCELLED) {
        // User cancelled the login flow
      } else {
        Alert.alert('Google Sign In Failed', 'Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleFacebookLogin = async () => {
    setIsLoading(true);

    try {
      const result = await LoginManager.logInWithPermissions(['public_profile', 'email']);

      if (result.isCancelled) {
        return;
      }

      const data = await AccessToken.getCurrentAccessToken();

      if (!data) {
        throw new Error('Something went wrong obtaining access token');
      }

      const deviceId = DeviceManager.getDeviceId();
      const deviceInfo = DeviceManager.getDeviceInfo();
      const pushToken = DeviceManager.getPushToken();

      const socialAuthData = {
        provider: 'facebook',
        access_token: data.accessToken,
        device_id: deviceId,
        device_name: deviceInfo.deviceName,
        platform: deviceInfo.platform,
        push_token: pushToken || '',
      };

      const response = await AuthService.socialAuth(socialAuthData);

      if (response.success) {
        await AsyncStorage.multiSet([
          ['access_token', response.data.access],
          ['refresh_token', response.data.refresh],
          ['user_data', JSON.stringify(response.data.user)],
          ['device_id', response.data.device_id],
        ]);

        navigation.replace('MainTabs');
      } else {
        handleLoginError(response.error, response.message);
      }
    } catch (error) {
      console.error('Facebook login error:', error);
      Alert.alert('Facebook Sign In Failed', 'Please try again later.');
    } finally {
      setIsLoading(false);
    }
  };

  const handleAppleLogin = async () => {
    if (!appleAuth.isSupported) {
      Alert.alert('Apple Sign In', 'Apple Sign In is not supported on this device.');
      return;
    }

    setIsLoading(true);

    try {
      const appleAuthRequestResponse = await appleAuth.performRequest({
        requestedOperation: appleAuth.Operation.LOGIN,
        requestedScopes: [appleAuth.Scope.EMAIL, appleAuth.Scope.FULL_NAME],
      });

      const credentialState = await appleAuth.getCredentialStateForUser(
        appleAuthRequestResponse.user
      );

      if (credentialState === appleAuth.State.AUTHORIZED) {
        const deviceId = DeviceManager.getDeviceId();
        const deviceInfo = DeviceManager.getDeviceInfo();
        const pushToken = DeviceManager.getPushToken();

        const socialAuthData = {
          provider: 'apple',
          access_token: appleAuthRequestResponse.identityToken,
          device_id: deviceId,
          device_name: deviceInfo.deviceName,
          platform: deviceInfo.platform,
          push_token: pushToken || '',
        };

        const response = await AuthService.socialAuth(socialAuthData);

        if (response.success) {
          await AsyncStorage.multiSet([
            ['access_token', response.data.access],
            ['refresh_token', response.data.refresh],
            ['user_data', JSON.stringify(response.data.user)],
            ['device_id', response.data.device_id],
          ]);

          navigation.replace('MainTabs');
        } else {
          handleLoginError(response.error, response.message);
        }
      }
    } catch (error) {
      console.error('Apple login error:', error);
      if (error.code === appleAuth.Error.CANCELED) {
        // User cancelled
      } else {
        Alert.alert('Apple Sign In Failed', 'Please try again later.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleLoginError = (error, message) => {
    if (error === 'Device limit reached') {
      Alert.alert(
        'Device Limit Reached',
        'You can only use SlokaCamp on one device at a time. Would you like to transfer your access to this device?',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Transfer Access',
            onPress: () => navigation.navigate('DeviceTransfer', { email }),
          },
        ]
      );
    } else if (error === 'Email not verified') {
      Alert.alert(
        'Email Verification Required',
        'Please verify your email address before logging in.',
        [
          { text: 'OK' },
          {
            text: 'Resend Email',
            onPress: () => resendVerificationEmail(),
          },
        ]
      );
    } else {
      Alert.alert('Login Failed', message || 'Please check your credentials and try again.');
    }
  };

  const resendVerificationEmail = async () => {
    try {
      await AuthService.resendVerificationEmail(email);
      Alert.alert('Email Sent', 'Please check your email for verification instructions.');
    } catch (error) {
      Alert.alert('Error', 'Failed to resend verification email.');
    }
  };

  const isValidEmail = (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  };

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
        <Text style={styles.loadingText}>Signing in...</Text>
      </View>
    );
  }

  return (
    <KeyboardAvoidingView
      style={styles.container}
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Header */}
        <View style={styles.header}>
          <Text style={styles.logo}>🕉 SlokaCamp</Text>
          <Text style={styles.subtitle}>Continue your spiritual learning journey</Text>
        </View>

        {/* Login Form */}
        <View style={styles.form}>
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Email</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your email"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Password</Text>
            <View style={styles.passwordContainer}>
              <TextInput
                style={styles.passwordInput}
                placeholder="Enter your password"
                value={password}
                onChangeText={setPassword}
                secureTextEntry={!showPassword}
                autoCapitalize="none"
                autoCorrect={false}
              />
              <TouchableOpacity
                style={styles.passwordToggle}
                onPress={() => setShowPassword(!showPassword)}
              >
                <Text style={styles.passwordToggleText}>
                  {showPassword ? '👁' : '👁‍🗨'}
                </Text>
              </TouchableOpacity>
            </View>
          </View>

          <TouchableOpacity style={styles.loginButton} onPress={handleEmailLogin}>
            <Text style={styles.loginButtonText}>Sign In</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.forgotPasswordButton}
            onPress={() => navigation.navigate('ForgotPassword')}
          >
            <Text style={styles.forgotPasswordText}>Forgot Password?</Text>
          </TouchableOpacity>
        </View>

        {/* Social Login */}
        <View style={styles.socialLogin}>
          <View style={styles.divider}>
            <View style={styles.dividerLine} />
            <Text style={styles.dividerText}>Or continue with</Text>
            <View style={styles.dividerLine} />
          </View>

          <View style={styles.socialButtons}>
            <TouchableOpacity style={styles.socialButton} onPress={handleGoogleLogin}>
              <Text style={styles.socialButtonText}>📧 Google</Text>
            </TouchableOpacity>

            <TouchableOpacity style={styles.socialButton} onPress={handleFacebookLogin}>
              <Text style={styles.socialButtonText}>📘 Facebook</Text>
            </TouchableOpacity>

            {Platform.OS === 'ios' && (
              <TouchableOpacity style={styles.socialButton} onPress={handleAppleLogin}>
                <Text style={styles.socialButtonText}>🍎 Apple</Text>
              </TouchableOpacity>
            )}
          </View>
        </View>

        {/* Sign Up Link */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>Don't have an account? </Text>
          <TouchableOpacity onPress={() => navigation.navigate('Register')}>
            <Text style={styles.signUpLink}>Sign Up</Text>
          </TouchableOpacity>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#ffffff',
  },
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
  },
  scrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    paddingHorizontal: 24,
  },
  header: {
    alignItems: 'center',
    marginBottom: 48,
  },
  logo: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ff6b35',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 16,
    color: '#666666',
    textAlign: 'center',
  },
  form: {
    marginBottom: 32,
  },
  inputContainer: {
    marginBottom: 24,
  },
  inputLabel: {
    fontSize: 16,
    fontWeight: '600',
    color: '#333333',
    marginBottom: 8,
  },
  input: {
    height: 50,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    paddingHorizontal: 16,
    fontSize: 16,
    backgroundColor: '#f9f9f9',
  },
  passwordContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    height: 50,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    backgroundColor: '#f9f9f9',
  },
  passwordInput: {
    flex: 1,
    paddingHorizontal: 16,
    fontSize: 16,
  },
  passwordToggle: {
    paddingHorizontal: 16,
  },
  passwordToggleText: {
    fontSize: 18,
  },
  loginButton: {
    height: 50,
    backgroundColor: '#ff6b35',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 8,
  },
  loginButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  forgotPasswordButton: {
    alignItems: 'center',
    marginTop: 16,
  },
  forgotPasswordText: {
    color: '#ff6b35',
    fontSize: 16,
    fontWeight: '500',
  },
  socialLogin: {
    marginBottom: 32,
  },
  divider: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 24,
  },
  dividerLine: {
    flex: 1,
    height: 1,
    backgroundColor: '#e0e0e0',
  },
  dividerText: {
    marginHorizontal: 16,
    color: '#666666',
    fontSize: 14,
  },
  socialButtons: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  socialButton: {
    flex: 1,
    height: 50,
    borderWidth: 1,
    borderColor: '#e0e0e0',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    marginHorizontal: 4,
  },
  socialButtonText: {
    fontSize: 16,
    fontWeight: '500',
    color: '#333333',
  },
  footer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
  },
  footerText: {
    fontSize: 16,
    color: '#666666',
  },
  signUpLink: {
    fontSize: 16,
    color: '#ff6b35',
    fontWeight: '600',
  },
});

export default LoginScreen;