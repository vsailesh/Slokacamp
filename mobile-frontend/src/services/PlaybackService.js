# Playback Service for React Native
# Handles video playback sessions, heartbeats, and DRM integration

import AsyncStorage from '@react-native-async-storage/async-storage';
import AuthService from './AuthService';

class PlaybackService {
  constructor() {
    this.activeSessions = new Map();
    this.heartbeatIntervals = new Map();
  }

  async startPlayback(playbackData) {
    try {
      const response = await AuthService.makeRequest('/playback/start/', {
        method: 'POST',
        body: JSON.stringify(playbackData),
      });

      if (response.success) {
        const sessionToken = response.data.session_token;
        
        // Store active session
        this.activeSessions.set(sessionToken, {
          ...response.data,
          startTime: Date.now(),
          lastHeartbeat: Date.now(),
        });

        // Start automatic heartbeat
        this.startHeartbeat(sessionToken);
      }

      return response;
    } catch (error) {
      console.error('Failed to start playback:', error);
      return {
        success: false,
        error: 'Network error',
        message: 'Failed to start video playback. Please check your connection.',
      };
    }
  }

  async sendHeartbeat(heartbeatData) {
    try {
      const response = await AuthService.makeRequest('/playback/heartbeat/', {
        method: 'POST',
        body: JSON.stringify(heartbeatData),
      });

      if (response.success) {
        // Update session data
        const sessionToken = heartbeatData.session_token;
        const session = this.activeSessions.get(sessionToken);
        if (session) {
          session.lastHeartbeat = Date.now();
          session.currentPosition = heartbeatData.current_position;
        }

        // Handle pause instruction from server
        if (response.data.should_pause) {
          return {
            ...response,
            shouldPause: true,
          };
        }
      }

      return response;
    } catch (error) {
      console.error('Heartbeat failed:', error);
      return {
        success: false,
        error: 'Network error',
        message: 'Failed to maintain session connection.',
      };
    }
  }

  async endPlayback(endData) {
    try {
      const response = await AuthService.makeRequest('/playback/end/', {
        method: 'POST',
        body: JSON.stringify(endData),
      });

      // Clean up session
      const sessionToken = endData.session_token;
      this.stopHeartbeat(sessionToken);
      this.activeSessions.delete(sessionToken);

      return response;
    } catch (error) {
      console.error('Failed to end playback:', error);
      
      // Clean up locally even if API call fails
      const sessionToken = endData.session_token;
      this.stopHeartbeat(sessionToken);
      this.activeSessions.delete(sessionToken);
      
      return {
        success: false,
        error: 'Network error',
        message: 'Session ended locally, but server may not have been notified.',
      };
    }
  }

  startHeartbeat(sessionToken) {
    // Clear existing heartbeat if any
    this.stopHeartbeat(sessionToken);

    const interval = setInterval(async () => {
      const session = this.activeSessions.get(sessionToken);
      if (!session) {
        this.stopHeartbeat(sessionToken);
        return;
      }

      try {
        const heartbeatData = {
          session_token: sessionToken,
          current_position: session.currentPosition || 0,
          screen_recording_detected: session.screenRecordingDetected || false,
          buffer_events: session.bufferEvents || 0,
        };

        const response = await this.sendHeartbeat(heartbeatData);
        
        if (!response.success) {
          console.warn('Heartbeat failed:', response.message);
          
          // If heartbeat fails multiple times, consider session dead
          const timeSinceLastSuccess = Date.now() - session.lastHeartbeat;
          if (timeSinceLastSuccess > 180000) { // 3 minutes
            console.error('Session appears to be dead, cleaning up');
            this.stopHeartbeat(sessionToken);
            this.activeSessions.delete(sessionToken);
          }
        }
      } catch (error) {
        console.error('Heartbeat error:', error);
      }
    }, 30000); // Every 30 seconds

    this.heartbeatIntervals.set(sessionToken, interval);
  }

  stopHeartbeat(sessionToken) {
    const interval = this.heartbeatIntervals.get(sessionToken);
    if (interval) {
      clearInterval(interval);
      this.heartbeatIntervals.delete(sessionToken);
    }
  }

  updateSessionPosition(sessionToken, currentPosition) {
    const session = this.activeSessions.get(sessionToken);
    if (session) {
      session.currentPosition = currentPosition;
    }
  }

  updateScreenRecordingStatus(sessionToken, isRecording) {
    const session = this.activeSessions.get(sessionToken);
    if (session) {
      session.screenRecordingDetected = isRecording;
    }
  }

  updateBufferEvents(sessionToken, bufferCount) {
    const session = this.activeSessions.get(sessionToken);
    if (session) {
      session.bufferEvents = (session.bufferEvents || 0) + bufferCount;
    }
  }

  getActiveSession(sessionToken) {
    return this.activeSessions.get(sessionToken);
  }

  getAllActiveSessions() {
    return Array.from(this.activeSessions.values());
  }

  hasActiveSession() {
    return this.activeSessions.size > 0;
  }

  // Clean up all sessions (called when app is backgrounded/closed)
  async cleanupAllSessions() {
    const promises = [];
    
    for (const [sessionToken, session] of this.activeSessions) {
      const endData = {
        session_token: sessionToken,
        end_position: session.currentPosition || 0,
        completion_percentage: 0, // Will be calculated on server
      };
      
      promises.push(this.endPlayback(endData));
    }

    // Wait for all cleanup calls to complete (or fail)
    await Promise.allSettled(promises);
    
    // Clear all local data
    this.activeSessions.clear();
    for (const interval of this.heartbeatIntervals.values()) {
      clearInterval(interval);
    }
    this.heartbeatIntervals.clear();
  }

  // Get video streaming URLs with proper authentication
  async getVideoUrls(videoId, lessonId = null) {
    try {
      const queryParams = new URLSearchParams({ video_id: videoId });
      if (lessonId) {
        queryParams.append('lesson_id', lessonId);
      }

      const response = await AuthService.makeRequest(
        `/videos/stream/?${queryParams.toString()}`
      );

      return response;
    } catch (error) {
      console.error('Failed to get video URLs:', error);
      return {
        success: false,
        error: 'Network error',
        message: 'Failed to get video streaming information.',
      };
    }
  }

  // Check if user can access video (subscription, enrollment)
  async canAccessVideo(videoId, lessonId = null) {
    try {
      const queryParams = new URLSearchParams({ video_id: videoId });
      if (lessonId) {
        queryParams.append('lesson_id', lessonId);
      }

      const response = await AuthService.makeRequest(
        `/videos/access-check/?${queryParams.toString()}`
      );

      return response;
    } catch (error) {
      console.error('Failed to check video access:', error);
      return {
        success: false,
        error: 'Network error',
        message: 'Failed to verify video access.',
      };
    }
  }

  // Quality and analytics
  async reportQualityMetrics(sessionToken, qualityData) {
    try {
      const response = await AuthService.makeRequest('/playback/quality/', {
        method: 'POST',
        body: JSON.stringify({
          session_token: sessionToken,
          ...qualityData,
        }),
      });

      return response;
    } catch (error) {
      console.error('Failed to report quality metrics:', error);
      return { success: false };
    }
  }

  // Error reporting
  async reportPlaybackError(sessionToken, errorData) {
    try {
      const response = await AuthService.makeRequest('/playback/error/', {
        method: 'POST',
        body: JSON.stringify({
          session_token: sessionToken,
          ...errorData,
        }),
      });

      return response;
    } catch (error) {
      console.error('Failed to report playback error:', error);
      return { success: false };
    }
  }
}

// Singleton instance
const playbackService = new PlaybackService();
export default playbackService;