import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from './components/Navbar';
import Homepage from './components/Homepage';
import Footer from './components/Footer';
import Dashboard from './components/Dashboard';
import CourseCatalog from './components/CourseCatalog';
import CourseDetail from './components/CourseDetail';
import LessonPlayer from './components/LessonPlayer';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/courses" element={<CourseCatalog />} />
          <Route path="/course/:courseId" element={<CourseDetail />} />
          <Route path="/lesson/:lessonId" element={<LessonPlayer />} />
          <Route path="/learn/:courseId" element={<LessonPlayer />} />
          <Route path="/career-tracks" element={<div className="py-20 text-center">Career Tracks page coming soon...</div>} />
          <Route path="/live-classes" element={<div className="py-20 text-center">Live Classes page coming soon...</div>} />
          <Route path="/for-business" element={<div className="py-20 text-center">Business page coming soon...</div>} />
          <Route path="/login" element={<div className="py-20 text-center">Login page coming soon...</div>} />
          <Route path="/signup" element={<div className="py-20 text-center">Signup page coming soon...</div>} />
        </Routes>
        <Footer />
      </BrowserRouter>
    </div>
  );
}

export default App;