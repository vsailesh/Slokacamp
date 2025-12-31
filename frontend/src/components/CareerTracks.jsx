import React from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { useNavigate } from 'react-router-dom';

const CareerTracks = () => {
  const navigate = useNavigate();

  const careerTracks = [
    {
      id: 1,
      title: 'Ayurvedic Practitioner',
      description: 'Become a certified Ayurvedic practitioner with comprehensive training in diagnosis, treatment, and holistic wellness.',
      duration: '12 months',
      courses: 8,
      level: 'Beginner to Advanced',
      skills: ['Dosha Analysis', 'Herbal Medicine', 'Panchakarma', 'Nutrition', 'Clinical Practice'],
      outcomes: 'Practice as certified Ayurvedic consultant, open wellness clinic, work in spas/resorts',
    },
    {
      id: 2,
      title: 'Yoga Instructor',
      description: 'Master the art of teaching yoga with in-depth study of asanas, philosophy, anatomy, and teaching methodology.',
      duration: '9 months',
      courses: 6,
      level: 'Intermediate',
      skills: ['Asana Practice', 'Pranayama', 'Meditation', 'Yoga Philosophy', 'Teaching Skills'],
      outcomes: 'Teach at studios, conduct workshops, offer private classes, become RYT certified',
    },
    {
      id: 3,
      title: 'Sanskrit Scholar',
      description: 'Deep dive into Sanskrit language, literature, and ancient texts with comprehensive linguistic training.',
      duration: '18 months',
      courses: 10,
      level: 'Beginner to Advanced',
      skills: ['Grammar', 'Literature', 'Vedic Studies', 'Translation', 'Research'],
      outcomes: 'Academic research, translation work, teaching, cultural preservation',
    },
    {
      id: 4,
      title: 'Meditation Teacher',
      description: 'Learn various meditation techniques and how to guide others in their mindfulness journey.',
      duration: '6 months',
      courses: 5,
      level: 'Beginner',
      skills: ['Mindfulness', 'Guided Meditation', 'Breathwork', 'Stress Management', 'Group Facilitation'],
      outcomes: 'Lead meditation sessions, corporate wellness programs, retreat facilitator',
    },
    {
      id: 5,
      title: 'Holistic Wellness Coach',
      description: 'Integrate Ayurveda, yoga, and meditation to guide clients toward complete wellness.',
      duration: '10 months',
      courses: 7,
      level: 'Intermediate',
      skills: ['Lifestyle Counseling', 'Nutrition', 'Mind-Body Connection', 'Client Management'],
      outcomes: 'Private practice, corporate wellness, online coaching, retreat leadership',
    },
    {
      id: 6,
      title: 'Vedic Astrology',
      description: 'Study the ancient science of Jyotish to provide insights and guidance through astrological consultation.',
      duration: '15 months',
      courses: 9,
      level: 'Advanced',
      skills: ['Chart Reading', 'Planetary Analysis', 'Remedial Measures', 'Predictive Techniques'],
      outcomes: 'Astrological consultations, compatibility analysis, timing guidance',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Career Tracks</h1>
          <p className="text-xl text-blue-100 max-w-3xl">
            Structured learning paths designed to help you achieve your career goals in traditional wellness and spiritual practices.
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Overview */}
        <div className="mb-12 bg-white rounded-lg p-8 shadow-md">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">What are Career Tracks?</h2>
          <p className="text-gray-700 mb-4">
            Career Tracks are curated learning paths that combine multiple courses to help you master a specific profession. 
            Each track includes a structured curriculum, hands-on practice, and certification upon completion.
          </p>
          <div className="grid md:grid-cols-3 gap-6 mt-6">
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">6+</div>
              <div className="text-gray-600">Career Paths</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">50+</div>
              <div className="text-gray-600">Courses Included</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-blue-600 mb-2">100%</div>
              <div className="text-gray-600">Certification Rate</div>
            </div>
          </div>
        </div>

        {/* Career Tracks Grid */}
        <div className="grid md:grid-cols-2 gap-8">
          {careerTracks.map((track) => (
            <div key={track.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow overflow-hidden">
              <div className="p-6">
                <div className="flex items-start justify-between mb-4">
                  <h3 className="text-2xl font-bold text-gray-900">{track.title}</h3>
                  <span className="px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {track.level}
                  </span>
                </div>
                
                <p className="text-gray-600 mb-4">{track.description}</p>
                
                <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                  <div>
                    <span className="text-gray-500">Duration:</span>
                    <p className="font-semibold text-gray-900">{track.duration}</p>
                  </div>
                  <div>
                    <span className="text-gray-500">Courses:</span>
                    <p className="font-semibold text-gray-900">{track.courses} courses</p>
                  </div>
                </div>

                <div className="mb-4">
                  <h4 className="font-semibold text-gray-900 mb-2">Skills You'll Learn:</h4>
                  <div className="flex flex-wrap gap-2">
                    {track.skills.map((skill, index) => (
                      <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mb-6">
                  <h4 className="font-semibold text-gray-900 mb-2">Career Outcomes:</h4>
                  <p className="text-sm text-gray-600">{track.outcomes}</p>
                </div>

                <button
                  onClick={() => navigate('/courses')}
                  className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors font-semibold"
                >
                  Explore Track
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* CTA Section */}
        <div className="mt-12 bg-gradient-to-r from-purple-600 to-blue-600 rounded-lg p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Start Your Journey?</h2>
          <p className="text-lg text-purple-100 mb-6 max-w-2xl mx-auto">
            Choose a career track and get personalized guidance throughout your learning journey.
          </p>
          <button
            onClick={() => navigate('/signup')}
            className="bg-white text-purple-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Get Started Free
          </button>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default CareerTracks;