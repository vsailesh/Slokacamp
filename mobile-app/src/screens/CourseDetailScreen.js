import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  ActivityIndicator,
  Alert,
} from 'react-native';
import { coursesAPI } from '../services/api';
import { useAuth } from '../context/AuthContext';

export default function CourseDetailScreen({ route, navigation }) {
  const { courseId } = route.params;
  const { user } = useAuth();
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [enrolling, setEnrolling] = useState(false);

  useEffect(() => {
    loadCourse();
  }, []);

  const loadCourse = async () => {
    try {
      const response = await coursesAPI.getCourse(courseId);
      setCourse(response.data);
    } catch (error) {
      if (__DEV__) {
        console.error('Error loading course:', error);
      }
      Alert.alert('Error', 'Failed to load course details');
    } finally {
      setLoading(false);
    }
  };

  const handleEnroll = async () => {
    setEnrolling(true);
    try {
      await coursesAPI.enrollCourse(courseId);
      Alert.alert('Success', 'Enrolled successfully!', [
        { text: 'OK', onPress: () => navigation.navigate('Dashboard') },
      ]);
    } catch (error) {
      const message = error.response?.data?.detail || 'Enrollment failed';
      Alert.alert('Error', message);
    } finally {
      setEnrolling(false);
    }
  };

  if (loading) {
    return (
      <View style={styles.loadingContainer}>
        <ActivityIndicator size="large" color="#ff6b35" />
      </View>
    );
  }

  if (!course) {
    return (
      <View style={styles.errorContainer}>
        <Text style={styles.errorText}>Course not found</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <ScrollView style={styles.content}>
        {/* Course Header */}
        <View style={styles.header}>
          <Text style={styles.category}>{course.category}</Text>
          <Text style={styles.title}>{course.title}</Text>
          <Text style={styles.description}>{course.short_description}</Text>
          
          <View style={styles.statsRow}>
            <View style={styles.stat}>
              <Text style={styles.statValue}>⭐ {course.rating}</Text>
              <Text style={styles.statLabel}>Rating</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{course.total_students}</Text>
              <Text style={styles.statLabel}>Students</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{course.lessons_count || 0}</Text>
              <Text style={styles.statLabel}>Lessons</Text>
            </View>
            <View style={styles.stat}>
              <Text style={styles.statValue}>{course.duration_hours}h</Text>
              <Text style={styles.statLabel}>Duration</Text>
            </View>
          </View>
        </View>

        {/* Instructor */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Instructor</Text>
          <View style={styles.instructorCard}>
            <Text style={styles.instructorName}>👨‍🏫 {course.instructor_name}</Text>
            <Text style={styles.instructorBio}>{course.instructor_bio}</Text>
          </View>
        </View>

        {/* Full Description */}
        <View style={styles.section}>
          <Text style={styles.sectionTitle}>About This Course</Text>
          <Text style={styles.fullDescription}>{course.description}</Text>
        </View>

        {/* Lessons */}
        {course.lessons && course.lessons.length > 0 && (
          <View style={styles.section}>
            <Text style={styles.sectionTitle}>Course Content</Text>
            {course.lessons.slice(0, 5).map((lesson, index) => (
              <View key={lesson.id} style={styles.lessonItem}>
                <Text style={styles.lessonNumber}>{index + 1}</Text>
                <View style={styles.lessonInfo}>
                  <Text style={styles.lessonTitle}>{lesson.title}</Text>
                  <Text style={styles.lessonDuration}>
                    {lesson.lesson_type} • {lesson.duration_minutes} min
                  </Text>
                </View>
              </View>
            ))}
            {course.lessons.length > 5 && (
              <Text style={styles.moreLessons}>
                + {course.lessons.length - 5} more lessons
              </Text>
            )}
          </View>
        )}

        <View style={{ height: 100 }} />
      </ScrollView>

      {/* Enroll Button */}
      <View style={styles.footer}>
        <TouchableOpacity
          style={[styles.enrollButton, enrolling && styles.enrollButtonDisabled]}
          onPress={handleEnroll}
          disabled={enrolling}
        >
          {enrolling ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.enrollButtonText}>Enroll Now</Text>
          )}
        </TouchableOpacity>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#f8f9fa',
  },
  loadingContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
  },
  errorText: {
    fontSize: 16,
    color: '#666',
  },
  content: {
    flex: 1,
  },
  header: {
    backgroundColor: '#fff',
    padding: 20,
  },
  category: {
    fontSize: 12,
    color: '#ff6b35',
    fontWeight: '600',
    marginBottom: 8,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#666',
    marginBottom: 20,
  },
  statsRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  stat: {
    alignItems: 'center',
  },
  statValue: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
  },
  statLabel: {
    fontSize: 12,
    color: '#666',
    marginTop: 4,
  },
  section: {
    backgroundColor: '#fff',
    padding: 20,
    marginTop: 10,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1a1a1a',
    marginBottom: 15,
  },
  instructorCard: {
    padding: 15,
    backgroundColor: '#f8f9fa',
    borderRadius: 10,
  },
  instructorName: {
    fontSize: 16,
    fontWeight: '600',
    color: '#1a1a1a',
    marginBottom: 8,
  },
  instructorBio: {
    fontSize: 14,
    color: '#666',
  },
  fullDescription: {
    fontSize: 14,
    color: '#666',
    lineHeight: 22,
  },
  lessonItem: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#f0f0f0',
  },
  lessonNumber: {
    width: 30,
    height: 30,
    borderRadius: 15,
    backgroundColor: '#f0f0f0',
    textAlign: 'center',
    lineHeight: 30,
    fontSize: 14,
    fontWeight: '600',
    color: '#666',
    marginRight: 12,
  },
  lessonInfo: {
    flex: 1,
  },
  lessonTitle: {
    fontSize: 14,
    fontWeight: '500',
    color: '#1a1a1a',
    marginBottom: 4,
  },
  lessonDuration: {
    fontSize: 12,
    color: '#666',
  },
  moreLessons: {
    fontSize: 14,
    color: '#ff6b35',
    textAlign: 'center',
    marginTop: 15,
  },
  footer: {
    backgroundColor: '#fff',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#e0e0e0',
  },
  enrollButton: {
    backgroundColor: '#ff6b35',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
  },
  enrollButtonDisabled: {
    backgroundColor: '#ffb399',
  },
  enrollButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});
