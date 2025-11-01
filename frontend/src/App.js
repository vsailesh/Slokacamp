import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { AuthProvider } from './contexts/AuthContext';
import Navbar from './components/Navbar';
import Homepage from './components/Homepage';
import Footer from './components/Footer';
import Dashboard from './components/Dashboard';
import CourseCatalog from './components/CourseCatalog';
import CourseDetail from './components/CourseDetail';
import LessonPlayer from './components/LessonPlayer';
import Signin from './components/Signin';
import Signup from './components/Signup';
import AdminDashboard from './components/AdminDashboard';
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <AuthProvider>
          <Routes>
            {/* Public routes with Navbar */}
            <Route path="/" element={
              <>
                <Navbar />
                <Homepage />
                <Footer />
              </>
            } />
            <Route path="/courses" element={
              <>
                <Navbar />
                <CourseCatalog />
                <Footer />
              </>
            } />
            <Route path="/course/:courseId" element={
              <>
                <Navbar />
                <CourseDetail />
                <Footer />
              </>
            } />
            
            {/* Auth routes without Navbar */}
            <Route path="/signin" element={<Signin />} />
            <Route path="/signup" element={<Signup />} />
            
            {/* Protected routes with Navbar */}
            <Route path="/dashboard" element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            } />
            <Route path="/lesson/:lessonId" element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <LessonPlayer />
                  <Footer />
                </>
              </ProtectedRoute>
            } />
            <Route path="/learn/:courseId" element={
              <ProtectedRoute>
                <>
                  <Navbar />
                  <LessonPlayer />
                  <Footer />
                </>
              </ProtectedRoute>
            } />
            
            {/* Admin only route */}
            <Route path="/admin" element={
              <ProtectedRoute adminOnly={true}>
                <AdminDashboard />
              </ProtectedRoute>
            } />
            
            {/* Placeholder routes */}
            <Route path="/career-tracks" element={
              <>
                <Navbar />
                <div className="py-20 text-center">Career Tracks page coming soon...</div>
                <Footer />
              </>
            } />
            <Route path="/live-classes" element={
              <>
                <Navbar />
                <div className="py-20 text-center">Live Classes page coming soon...</div>
                <Footer />
              </>
            } />
            <Route path="/for-business" element={
              <>
                <Navbar />
                <div className="py-20 text-center">Business page coming soon...</div>
                <Footer />
              </>
            } />
          </Routes>
        </AuthProvider>
      </BrowserRouter>
    </div>
  );
}

export default App;