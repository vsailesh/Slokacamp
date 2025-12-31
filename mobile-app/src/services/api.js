import axios from 'axios';
import { API_URL } from '@env';

// Ensure API_URL doesn't have trailing /api, we'll add it here
const baseURL = API_URL 
  ? (API_URL.endsWith('/api') ? API_URL : `${API_URL}/api`)
  : 'https://ayurlearn.preview.emergentagent.com/api';

const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for debugging (development only)
api.interceptors.request.use(
  (config) => {
    if (__DEV__) {
      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.baseURL}${config.url}`);
    }
    return config;
  },
  (error) => {
    if (__DEV__) {
      console.error('[API Request Error]', error);
    }
    return Promise.reject(error);
  }
);

// Add response interceptor for debugging (development only)
api.interceptors.response.use(
  (response) => {
    if (__DEV__) {
      console.log(`[API Response] ${response.config.method?.toUpperCase()} ${response.config.url} - Status: ${response.status}`);
    }
    return response;
  },
  (error) => {
    if (__DEV__) {
      console.error(`[API Error] ${error.config?.method?.toUpperCase()} ${error.config?.url}`, error.response?.data || error.message);
    }
    return Promise.reject(error);
  }
);

export const setAuthToken = (token) => {
  if (token) {
    api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
  } else {
    delete api.defaults.headers.common['Authorization'];
  }
};

export const authAPI = {
  signup: (data) => api.post('/auth/signup/', data),
  signin: (data) => api.post('/auth/signin/', data),
  getCurrentUser: () => api.get('/auth/me/'),
};

export const coursesAPI = {
  getAllCourses: (params) => api.get('/courses/', { params }),
  getCourse: (id) => api.get(`/courses/${id}/`),
  getMyEnrollments: () => api.get('/courses/my-enrollments/'),
  enrollCourse: (courseId) => api.post('/courses/enroll/', { course_id: courseId }),
  updateLessonProgress: (data) => api.post('/courses/lesson-progress/', data),
};

export default api;
