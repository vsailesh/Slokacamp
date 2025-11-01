# Course Service for React Native
# Handles all course-related API calls and data management

import AuthService from './AuthService';

class CourseService {
  async getCourses(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/courses/?${queryString}` : '/courses/';
    
    return AuthService.makeRequest(endpoint);
  }

  async getCourse(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/`);
  }

  async enrollInCourse(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/enroll/`, {
      method: 'POST',
    });
  }

  async getUserEnrollments() {
    return AuthService.makeRequest('/courses/enrollments/');
  }

  async getLesson(lessonId) {
    return AuthService.makeRequest(`/courses/lessons/${lessonId}/`);
  }

  async updateLessonProgress(lessonId, progressData) {
    return AuthService.makeRequest(`/courses/lessons/${lessonId}/progress/`, {
      method: 'PATCH',
      body: JSON.stringify(progressData),
    });
  }

  async getDashboard() {
    return AuthService.makeRequest('/dashboard/');
  }

  async searchCourses(query) {
    return this.getCourses({ search: query });
  }

  async getCoursesByCategory(category) {
    return this.getCourses({ category });
  }

  async getCoursesByLevel(level) {
    return this.getCourses({ level });
  }

  async getPopularCourses() {
    return this.getCourses({ ordering: 'popular' });
  }

  async getRecommendedCourses() {
    return AuthService.makeRequest('/courses/recommended/');
  }

  async getFeaturedCourses() {
    return this.getCourses({ is_featured: true });
  }

  async getFreeCourses() {
    return this.getCourses({ is_free: true });
  }

  // Progress tracking
  async getUserProgress(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/progress/`);
  }

  async markLessonComplete(lessonId) {
    return this.updateLessonProgress(lessonId, { 
      status: 'completed',
      completion_percentage: 100 
    });
  }

  async saveLessonPosition(lessonId, position, watchTime) {
    return this.updateLessonProgress(lessonId, {
      last_position: position,
      watch_time: watchTime,
      status: 'in_progress'
    });
  }

  // Reviews and ratings
  async getCourseReviews(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/reviews/`);
  }

  async submitCourseReview(courseId, reviewData) {
    return AuthService.makeRequest(`/courses/${courseId}/reviews/`, {
      method: 'POST',
      body: JSON.stringify(reviewData),
    });
  }

  // Categories and filters
  async getCategories() {
    return AuthService.makeRequest('/courses/categories/');
  }

  async getLevels() {
    return AuthService.makeRequest('/courses/levels/');
  }

  // Certificates
  async getCertificate(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/certificate/`);
  }

  async downloadCertificate(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/certificate/download/`, {
      method: 'POST',
    });
  }

  // Bookmarks and favorites
  async bookmarkCourse(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/bookmark/`, {
      method: 'POST',
    });
  }

  async unbookmarkCourse(courseId) {
    return AuthService.makeRequest(`/courses/${courseId}/bookmark/`, {
      method: 'DELETE',
    });
  }

  async getBookmarkedCourses() {
    return AuthService.makeRequest('/courses/bookmarks/');
  }

  // Live classes
  async getLiveClasses() {
    return AuthService.makeRequest('/live-classes/');
  }

  async joinLiveClass(classId) {
    return AuthService.makeRequest(`/live-classes/${classId}/join/`, {
      method: 'POST',
    });
  }

  async getLiveClassDetails(classId) {
    return AuthService.makeRequest(`/live-classes/${classId}/`);
  }

  // Offline content
  async getOfflineContent() {
    return AuthService.makeRequest('/courses/offline/');
  }

  async downloadForOffline(lessonId) {
    return AuthService.makeRequest(`/courses/lessons/${lessonId}/download/`, {
      method: 'POST',
    });
  }

  // Analytics and insights
  async getLearningAnalytics() {
    return AuthService.makeRequest('/analytics/learning/');
  }

  async getProgressAnalytics() {
    return AuthService.makeRequest('/analytics/progress/');
  }

  async getStreakData() {
    return AuthService.makeRequest('/analytics/streak/');
  }

  // Practice and quizzes
  async getPracticeQuestions(lessonId) {
    return AuthService.makeRequest(`/courses/lessons/${lessonId}/practice/`);
  }

  async submitPracticeAnswer(questionId, answerData) {
    return AuthService.makeRequest(`/practice/questions/${questionId}/answer/`, {
      method: 'POST',
      body: JSON.stringify(answerData),
    });
  }

  async getQuizResults(quizId) {
    return AuthService.makeRequest(`/quizzes/${quizId}/results/`);
  }

  // Sanskrit-specific features
  async getSanskritPronunciation(text) {
    return AuthService.makeRequest('/sanskrit/pronunciation/', {
      method: 'POST',
      body: JSON.stringify({ text }),
    });
  }

  async getTransliteration(sanskritText) {
    return AuthService.makeRequest('/sanskrit/transliterate/', {
      method: 'POST',
      body: JSON.stringify({ text: sanskritText }),
    });
  }

  async getWordMeaning(word) {
    return AuthService.makeRequest(`/sanskrit/dictionary/?word=${encodeURIComponent(word)}`);
  }

  // Study plans
  async getStudyPlan() {
    return AuthService.makeRequest('/study-plan/');
  }

  async createCustomStudyPlan(planData) {
    return AuthService.makeRequest('/study-plan/custom/', {
      method: 'POST',
      body: JSON.stringify(planData),
    });
  }

  async updateStudyPlan(planId, updateData) {
    return AuthService.makeRequest(`/study-plan/${planId}/`, {
      method: 'PATCH',
      body: JSON.stringify(updateData),
    });
  }

  // Helper methods
  async isEnrolledInCourse(courseId) {
    try {
      const response = await this.getCourse(courseId);
      return response.success && response.data.enrollment_status?.is_enrolled;
    } catch (error) {
      return false;
    }
  }

  async getCourseProgress(courseId) {
    try {
      const response = await this.getCourse(courseId);
      return response.success ? response.data.enrollment_status?.progress_percentage || 0 : 0;
    } catch (error) {
      return 0;
    }
  }

  // Cache management
  clearCache() {
    // Implement cache clearing logic if needed
  }

  // Offline support helpers
  async syncOfflineProgress() {
    // Implement offline progress sync
    return { success: true };
  }

  async getOfflineCapabilities() {
    return {
      canDownload: true,
      maxDownloads: 10,
      availableStorage: '2GB',
    };
  }
}

// Singleton instance
const courseService = new CourseService();
export default courseService;