// Screen Capture Detection Service
// Monitors for screen recording and mirroring to protect DRM content

import { Platform, NativeModules, NativeEventEmitter } from 'react-native';

class ScreenCaptureDetector {
  constructor() {
    this.isMonitoring = false;
    this.callbacks = [];
    this.screenCaptureDetected = false;
    
    // Native module for screen capture detection
    this.nativeModule = NativeModules.ScreenCaptureDetector;
    
    if (this.nativeModule) {
      this.eventEmitter = new NativeEventEmitter(this.nativeModule);
      this.setupEventListeners();
    }
  }

  setupEventListeners() {
    if (!this.eventEmitter) return;
    
    // iOS: Listen for screen capture changes
    if (Platform.OS === 'ios') {
      this.eventEmitter.addListener('ScreenCaptureChanged', (event) => {
        this.handleScreenCaptureChange(event.isCaptured);
      });
      
      // iOS: Listen for screen mirroring changes
      this.eventEmitter.addListener('ScreenMirroringChanged', (event) => {
        this.handleScreenCaptureChange(event.isMirrored);
      });
    }
    
    // Android: Listen for screen recording detection
    if (Platform.OS === 'android') {
      this.eventEmitter.addListener('ScreenRecordingChanged', (event) => {
        this.handleScreenCaptureChange(event.isRecording);
      });
    }
  }

  handleScreenCaptureChange(isCapturing) {
    this.screenCaptureDetected = isCapturing;
    
    // Notify all registered callbacks
    this.callbacks.forEach(callback => {
      try {
        callback(isCapturing);
      } catch (error) {
        console.error('Error in screen capture callback:', error);
      }
    });
  }

  startMonitoring(callback) {
    if (callback && typeof callback === 'function') {
      this.callbacks.push(callback);
    }
    
    if (this.isMonitoring) {
      return;
    }
    
    this.isMonitoring = true;
    
    if (this.nativeModule) {
      // Start native monitoring
      this.nativeModule.startMonitoring();
    } else {
      // Fallback: Use JavaScript-based detection (less reliable)
      this.startJavaScriptBasedDetection();
    }
    
    console.log('Screen capture detection started');
  }

  stopMonitoring() {
    if (!this.isMonitoring) {
      return;
    }
    
    this.isMonitoring = false;
    this.callbacks = [];
    
    if (this.nativeModule) {
      this.nativeModule.stopMonitoring();
    }
    
    console.log('Screen capture detection stopped');
  }

  startJavaScriptBasedDetection() {
    // Fallback detection method (limited effectiveness)
    // This is a basic implementation and may not catch all screen recording
    
    if (Platform.OS === 'ios') {
      // iOS: Check for UIScreen capture status periodically
      this.fallbackInterval = setInterval(() => {
        // This would require native implementation to be effective
        // JavaScript alone cannot reliably detect screen recording on iOS
        console.log('Fallback screen capture check (iOS)');
      }, 1000);
    } else if (Platform.OS === 'android') {
      // Android: Check for screen recording indicators
      this.fallbackInterval = setInterval(() => {
        // This would require native implementation to be effective
        // JavaScript alone cannot reliably detect screen recording on Android
        console.log('Fallback screen capture check (Android)');
      }, 1000);
    }
  }

  isScreenCaptureDetected() {
    return this.screenCaptureDetected;
  }

  // Method to be called by video player components
  shouldBlockPlayback() {
    return this.screenCaptureDetected;
  }

  addCallback(callback) {
    if (callback && typeof callback === 'function') {
      this.callbacks.push(callback);
    }
  }

  removeCallback(callback) {
    const index = this.callbacks.indexOf(callback);
    if (index > -1) {
      this.callbacks.splice(index, 1);
    }
  }
}

// Singleton instance
const screenCaptureDetector = new ScreenCaptureDetector();
export default screenCaptureDetector;

// Native Module Implementation Guide:
/*

iOS Implementation (ScreenCaptureDetector.swift):

```swift
import UIKit
import React

@objc(ScreenCaptureDetector)
class ScreenCaptureDetector: RCTEventEmitter {
  private var isMonitoring = false
  
  override init() {
    super.init()
  }
  
  @objc
  func startMonitoring() {
    guard !isMonitoring else { return }
    
    isMonitoring = true
    
    // Monitor screen capture
    NotificationCenter.default.addObserver(
      self,
      selector: #selector(screenCaptureChanged),
      name: UIScreen.capturedDidChangeNotification,
      object: nil
    )
    
    // Monitor screen mirroring
    NotificationCenter.default.addObserver(
      self,
      selector: #selector(screenMirroringChanged),
      name: UIScreen.mirroredScreenDidChangeNotification,
      object: nil
    )
  }
  
  @objc
  func stopMonitoring() {
    guard isMonitoring else { return }
    
    isMonitoring = false
    NotificationCenter.default.removeObserver(self)
  }
  
  @objc
  private func screenCaptureChanged() {
    sendEvent(withName: "ScreenCaptureChanged", body: ["isCaptured": UIScreen.main.isCaptured])
  }
  
  @objc
  private func screenMirroringChanged() {
    sendEvent(withName: "ScreenMirroringChanged", body: ["isMirrored": UIScreen.main.mirrored != nil])
  }
  
  override func supportedEvents() -> [String]! {
    return ["ScreenCaptureChanged", "ScreenMirroringChanged"]
  }
  
  @objc
  override static func requiresMainQueueSetup() -> Bool {
    return true
  }
}
```

Android Implementation (ScreenCaptureDetectorModule.java):

```java
package com.slokacamp;

import android.app.Activity;
import android.content.Context;
import android.hardware.display.DisplayManager;
import android.hardware.display.VirtualDisplay;
import android.media.projection.MediaProjectionManager;
import android.os.Handler;
import android.os.Looper;

import com.facebook.react.bridge.ReactApplicationContext;
import com.facebook.react.bridge.ReactContextBaseJavaModule;
import com.facebook.react.bridge.ReactMethod;
import com.facebook.react.bridge.WritableMap;
import com.facebook.react.bridge.Arguments;
import com.facebook.react.modules.core.DeviceEventManagerModule;

public class ScreenCaptureDetectorModule extends ReactContextBaseJavaModule {
    private ReactApplicationContext reactContext;
    private boolean isMonitoring = false;
    private Handler handler;
    private Runnable screenRecordingChecker;
    
    public ScreenCaptureDetectorModule(ReactApplicationContext reactContext) {
        super(reactContext);
        this.reactContext = reactContext;
        this.handler = new Handler(Looper.getMainLooper());
    }
    
    @Override
    public String getName() {
        return "ScreenCaptureDetector";
    }
    
    @ReactMethod
    public void startMonitoring() {
        if (isMonitoring) return;
        
        isMonitoring = true;
        
        screenRecordingChecker = new Runnable() {
            @Override
            public void run() {
                boolean isRecording = isScreenRecording();
                
                WritableMap params = Arguments.createMap();
                params.putBoolean("isRecording", isRecording);
                
                reactContext
                    .getJSModule(DeviceEventManagerModule.RCTDeviceEventEmitter.class)
                    .emit("ScreenRecordingChanged", params);
                
                if (isMonitoring) {
                    handler.postDelayed(this, 1000); // Check every second
                }
            }
        };
        
        handler.post(screenRecordingChecker);
    }
    
    @ReactMethod
    public void stopMonitoring() {
        isMonitoring = false;
        if (screenRecordingChecker != null) {
            handler.removeCallbacks(screenRecordingChecker);
        }
    }
    
    private boolean isScreenRecording() {
        try {
            MediaProjectionManager mediaProjectionManager = 
                (MediaProjectionManager) reactContext.getSystemService(Context.MEDIA_PROJECTION_SERVICE);
            
            // This is a simplified check - in practice, you'd need more sophisticated detection
            // Check for active virtual displays or media projection sessions
            
            return false; // Implement actual detection logic
        } catch (Exception e) {
            return false;
        }
    }
}
```

*/