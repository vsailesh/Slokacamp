# Complete React Native Video Player with DRM Support
# Includes screen capture detection and playback session management

import React, { useState, useEffect, useRef } from 'react';
import {
  View,
  Text,
  StyleSheet,
  Alert,
  TouchableOpacity,
  Dimensions,
  StatusBar,
  ActivityIndicator,
  PanResponder,
} from 'react-native';
import Video from 'react-native-video';
import Orientation from 'react-native-orientation-locker';
import AsyncStorage from '@react-native-async-storage/async-storage';
import ScreenCaptureDetector from '../services/ScreenCaptureDetector';
import PlaybackService from '../services/PlaybackService';
import { useNavigation, useRoute } from '@react-navigation/native';

const VideoPlayerScreen = () => {
  const navigation = useNavigation();
  const route = useRoute();
  const { videoId, lessonId, startPosition = 0 } = route.params;
  
  const videoRef = useRef(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(startPosition);
  const [duration, setDuration] = useState(0);
  const [showControls, setShowControls] = useState(true);
  const [isFullscreen, setIsFullscreen] = useState(false);
  const [videoUrls, setVideoUrls] = useState(null);
  const [sessionToken, setSessionToken] = useState(null);
  const [screenCaptureDetected, setScreenCaptureDetected] = useState(false);
  const [isBuffering, setIsBuffering] = useState(false);
  const [error, setError] = useState(null);
  
  // Heartbeat management
  const heartbeatInterval = useRef(null);
  const lastHeartbeat = useRef(0);
  
  // Screen dimensions
  const [screenData, setScreenData] = useState(Dimensions.get('window'));
  
  // Control timeout
  const controlsTimeout = useRef(null);

  useEffect(() => {
    initializePlayer();
    setupScreenCaptureDetection();
    
    // Lock orientation to landscape for video player
    Orientation.lockToLandscape();
    StatusBar.setHidden(true);
    
    return () => {
      cleanup();
    };
  }, []);

  const initializePlayer = async () => {
    try {
      const deviceId = await AsyncStorage.getItem('device_id');
      const accessToken = await AsyncStorage.getItem('access_token');
      
      if (!deviceId || !accessToken) {
        throw new Error('Authentication required');
      }

      // Start playback session
      const sessionResponse = await PlaybackService.startPlayback({
        video_id: videoId,
        device_id: deviceId,
        lesson_id: lessonId,
        start_position: startPosition,
      });

      if (sessionResponse.success) {
        setVideoUrls(sessionResponse.data.video_urls || sessionResponse.data.drm_token);
        setSessionToken(sessionResponse.data.session_token);
        
        // Start heartbeat
        startHeartbeat(sessionResponse.data.session_token);
        
        setIsLoading(false);
      } else {
        throw new Error(sessionResponse.message || 'Failed to start playback session');
      }
    } catch (error) {
      console.error('Player initialization failed:', error);
      setError(error.message);
      setIsLoading(false);
      
      Alert.alert(
        'Playback Error',
        error.message,
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    }
  };

  const setupScreenCaptureDetection = () => {
    ScreenCaptureDetector.addCallback(handleScreenCaptureChange);
    ScreenCaptureDetector.startMonitoring();
  };

  const handleScreenCaptureChange = (isCapturing) => {
    setScreenCaptureDetected(isCapturing);
    
    if (isCapturing) {
      // Pause video when screen recording detected
      setIsPlaying(false);
      
      Alert.alert(
        'Screen Recording Detected',
        'For content protection, video playback has been paused.',
        [{ text: 'OK' }]
      );
    }
  };

  const startHeartbeat = (token) => {
    heartbeatInterval.current = setInterval(() => {
      sendHeartbeat(token);
    }, 30000); // Every 30 seconds
  };

  const sendHeartbeat = async (token) => {
    try {
      await PlaybackService.sendHeartbeat({
        session_token: token,
        current_position: Math.floor(currentTime),
        screen_recording_detected: screenCaptureDetected,
        buffer_events: 0, // Could track buffer events
      });
      
      lastHeartbeat.current = Date.now();
    } catch (error) {
      console.error('Heartbeat failed:', error);
      
      // If heartbeat fails multiple times, show warning
      if (Date.now() - lastHeartbeat.current > 120000) { // 2 minutes
        Alert.alert(
          'Connection Issue',
          'Your session may have expired. Please restart the video.',
          [{ text: 'OK', onPress: () => navigation.goBack() }]
        );
      }
    }
  };

  const cleanup = async () => {
    // Clear intervals
    if (heartbeatInterval.current) {
      clearInterval(heartbeatInterval.current);
    }
    
    if (controlsTimeout.current) {
      clearTimeout(controlsTimeout.current);
    }
    
    // End playback session
    if (sessionToken) {
      try {
        await PlaybackService.endPlayback({
          session_token: sessionToken,
          end_position: Math.floor(currentTime),
          completion_percentage: duration > 0 ? (currentTime / duration) * 100 : 0,
        });
      } catch (error) {
        console.error('Failed to end playback session:', error);
      }
    }
    
    // Stop screen capture detection
    ScreenCaptureDetector.removeCallback(handleScreenCaptureChange);
    
    // Restore orientation and status bar
    Orientation.unlockAllOrientations();
    StatusBar.setHidden(false);
  };

  const handlePlayPause = () => {
    if (screenCaptureDetected) {
      Alert.alert(
        'Playback Blocked',
        'Please stop screen recording to continue watching.',
        [{ text: 'OK' }]
      );
      return;
    }
    
    setIsPlaying(!isPlaying);
    showControlsTemporarily();
  };

  const handleSeek = (position) => {
    setCurrentTime(position);
    videoRef.current?.seek(position);
    showControlsTemporarily();
  };

  const showControlsTemporarily = () => {
    setShowControls(true);
    
    if (controlsTimeout.current) {
      clearTimeout(controlsTimeout.current);
    }
    
    controlsTimeout.current = setTimeout(() => {
      if (isPlaying) {
        setShowControls(false);
      }
    }, 3000);
  };

  const handleProgress = (data) => {
    setCurrentTime(data.currentTime);
  };

  const handleLoad = (data) => {
    setDuration(data.duration);
  };

  const handleBuffer = ({ isBuffering: buffering }) => {
    setIsBuffering(buffering);
  };

  const handleVideoError = (error) => {
    console.error('Video playback error:', error);
    setError('Video playback failed. Please try again.');
    
    Alert.alert(
      'Playback Error',
      'Failed to play video. Please check your connection and try again.',
      [{ text: 'OK', onPress: () => navigation.goBack() }]
    );
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const handleBack = async () => {
    Alert.alert(
      'Exit Video',
      'Are you sure you want to exit? Your progress will be saved.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Exit', onPress: () => navigation.goBack() },
      ]
    );
  };

  // Pan responder for showing/hiding controls
  const panResponder = PanResponder.create({
    onStartShouldSetPanResponder: () => true,
    onPanResponderGrant: () => {
      showControlsTemporarily();
    },
  });

  if (isLoading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
        <Text style={styles.loadingText}>Loading video...</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>⚠️</Text>
        <Text style={styles.errorMessage}>{error}</Text>
        <TouchableOpacity style={styles.retryButton} onPress={initializePlayer}>
          <Text style={styles.retryButtonText}>Retry</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={styles.container} {...panResponder.panHandlers}>
      {/* Video Player */}
      {videoUrls && (
        <Video
          ref={videoRef}
          source={{ 
            uri: videoUrls.hls || videoUrls.dash || videoUrls.mp4,
            headers: videoUrls.headers || {},
          }}
          style={styles.video}
          paused={!isPlaying || screenCaptureDetected}
          onLoad={handleLoad}
          onProgress={handleProgress}
          onBuffer={handleBuffer}
          onError={handleVideoError}
          resizeMode="contain"
          progressUpdateInterval={1000}
          currentTime={currentTime}
        />
      )}
      
      {/* Screen Capture Warning Overlay */}
      {screenCaptureDetected && (
        <View style={styles.captureWarningOverlay}>
          <View style={styles.captureWarning}>
            <Text style={styles.captureWarningIcon}>🚫</Text>
            <Text style={styles.captureWarningTitle}>Screen Recording Detected</Text>
            <Text style={styles.captureWarningText}>
              For content protection, playback is paused while screen recording is active.
            </Text>
          </View>
        </View>
      )}
      
      {/* Buffering Indicator */}
      {isBuffering && (
        <View style={styles.bufferingOverlay}>
          <ActivityIndicator size="large" color="#ffffff" />
          <Text style={styles.bufferingText}>Buffering...</Text>
        </View>
      )}
      
      {/* Controls */}
      {showControls && (
        <View style={styles.controlsContainer}>
          {/* Top Bar */}
          <View style={styles.topControls}>
            <TouchableOpacity style={styles.backButton} onPress={handleBack}>
              <Text style={styles.backButtonText}>← Back</Text>
            </TouchableOpacity>
            
            <Text style={styles.videoTitle}>Sanskrit Lesson</Text>
          </View>
          
          {/* Center Controls */}
          <View style={styles.centerControls}>
            <TouchableOpacity 
              style={styles.playPauseButton} 
              onPress={handlePlayPause}
              disabled={screenCaptureDetected}
            >
              <Text style={styles.playPauseIcon}>
                {isPlaying ? '⏸️' : '▶️'}
              </Text>
            </TouchableOpacity>
          </View>
          
          {/* Bottom Controls */}
          <View style={styles.bottomControls}>
            <Text style={styles.timeText}>
              {formatTime(currentTime)} / {formatTime(duration)}
            </Text>
            
            {/* Progress Bar */}
            <View style={styles.progressContainer}>
              <View style={styles.progressBackground}>
                <View 
                  style={[
                    styles.progressFill,
                    { width: `${duration > 0 ? (currentTime / duration) * 100 : 0}%` }
                  ]} 
                />
              </View>
            </View>
            
            {/* Quality/Speed Controls */}
            <View style={styles.rightControls}>
              <Text style={styles.qualityText}>HD</Text>
            </View>
          </View>
        </View>
      )}
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#000000',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000000',
  },
  loadingText: {
    color: '#ffffff',
    marginTop: 16,
    fontSize: 16,
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#000000',
    paddingHorizontal: 32,
  },
  errorText: {
    fontSize: 64,
    marginBottom: 16,
  },
  errorMessage: {
    color: '#ffffff',
    fontSize: 18,
    textAlign: 'center',
    marginBottom: 24,
  },
  retryButton: {
    backgroundColor: '#ff6b35',
    paddingHorizontal: 24,
    paddingVertical: 12,
    borderRadius: 8,
  },
  retryButtonText: {
    color: '#ffffff',
    fontSize: 16,
    fontWeight: '600',
  },
  video: {
    position: 'absolute',
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
  },
  captureWarningOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.9)',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 999,
  },
  captureWarning: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    padding: 32,
    borderRadius: 16,
    alignItems: 'center',
    maxWidth: '80%',
  },
  captureWarningIcon: {
    fontSize: 48,
    marginBottom: 16,
  },
  captureWarningTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#ff3333',
    marginBottom: 12,
    textAlign: 'center',
  },
  captureWarningText: {
    fontSize: 16,
    color: '#333333',
    textAlign: 'center',
    lineHeight: 24,
  },
  bufferingOverlay: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
  },
  bufferingText: {
    color: '#ffffff',
    marginTop: 16,
    fontSize: 16,
  },
  controlsContainer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.3)',
  },
  topControls: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingTop: 40,
    paddingBottom: 16,
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
  },
  videoTitle: {
    flex: 1,
    color: '#ffffff',
    fontSize: 18,
    fontWeight: '600',
    textAlign: 'center',
    marginRight: 40, // Offset for back button
  },
  centerControls: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  playPauseButton: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: 'rgba(255, 255, 255, 0.2)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  playPauseIcon: {
    fontSize: 32,
  },
  bottomControls: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingHorizontal: 16,
    paddingBottom: 40,
    paddingTop: 16,
  },
  timeText: {
    color: '#ffffff',
    fontSize: 14,
    minWidth: 80,
  },
  progressContainer: {
    flex: 1,
    marginHorizontal: 16,
  },
  progressBackground: {
    height: 4,
    backgroundColor: 'rgba(255, 255, 255, 0.3)',
    borderRadius: 2,
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#ff6b35',
    borderRadius: 2,
  },
  rightControls: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  qualityText: {
    color: '#ffffff',
    fontSize: 14,
    fontWeight: '600',
  },
});

export default VideoPlayerScreen;