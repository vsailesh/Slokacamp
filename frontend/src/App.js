import React from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Navbar from './components/Navbar';
import Homepage from './components/Homepage';
import Footer from './components/Footer';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Navbar />
        <Routes>
          <Route path="/" element={<Homepage />} />
          <Route path="/courses" element={<div className="py-20 text-center">Courses page coming soon...</div>} />
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