import axios from 'axios';
import { API_URL } from '@env';

const api = axios.create({
  baseURL: 'https://ayurlearn.preview.emergentagent.com/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

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
