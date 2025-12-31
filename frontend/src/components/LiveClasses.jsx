import React, { useState } from 'react';
import Navbar from './Navbar';
import Footer from './Footer';
import { useNavigate } from 'react-router-dom';

const LiveClasses = () => {
  const navigate = useNavigate();
  const [selectedCategory, setSelectedCategory] = useState('all');

  const upcomingClasses = [
    {
      id: 1,
      title: 'Ayurvedic Pulse Diagnosis Workshop',
      instructor: 'Dr. Priya Sharma',
      date: '2025-03-15',
      time: '10:00 AM - 12:00 PM IST',
      duration: '2 hours',
      category: 'Ayurveda',
      level: 'Intermediate',
      seats: 15,
      price: '₹499',
      description: 'Learn the ancient art of Nadi Pariksha (pulse diagnosis) to assess doshas and health conditions.',
    },
    {
      id: 2,
      title: 'Advanced Pranayama & Breathwork',
      instructor: 'Swami Ananda',
      date: '2025-03-18',
      time: '6:00 AM - 7:30 AM IST',
      duration: '90 minutes',
      category: 'Yoga',
      level: 'Advanced',
      seats: 20,
      price: '₹399',
      description: 'Master advanced breathing techniques for energy regulation and spiritual awakening.',
    },
    {
      id: 3,
      title: 'Sanskrit Sloka Recitation',
      instructor: 'Pandit Ramesh Kumar',
      date: '2025-03-20',
      time: '5:00 PM - 6:00 PM IST',
      duration: '1 hour',
      category: 'Sanskrit',
      level: 'Beginner',
      seats: 30,
      price: 'Free',
      description: 'Learn proper pronunciation and recitation of popular Sanskrit slokas from Bhagavad Gita.',
    },
    {
      id: 4,
      title: 'Guided Meditation for Stress Relief',
      instructor: 'Sita Devi',
      date: '2025-03-22',
      time: '7:00 PM - 8:00 PM IST',
      duration: '1 hour',
      category: 'Meditation',
      level: 'Beginner',
      seats: 50,
      price: 'Free',
      description: 'Group meditation session focused on releasing stress and finding inner peace.',
    },
    {
      id: 5,
      title: 'Ayurvedic Cooking Masterclass',
      instructor: 'Chef Maya Patel',
      date: '2025-03-25',
      time: '3:00 PM - 5:00 PM IST',
      duration: '2 hours',
      category: 'Ayurveda',
      level: 'Beginner',
      seats: 25,
      price: '₹599',
      description: 'Hands-on cooking session to prepare dosha-balancing meals using Ayurvedic principles.',
    },
    {
      id: 6,
      title: 'Yoga Philosophy Discussion',
      instructor: 'Guru Sita Devi',
      date: '2025-03-28',
      time: '4:00 PM - 5:30 PM IST',
      duration: '90 minutes',
      category: 'Yoga',
      level: 'Intermediate',
      seats: 40,
      price: '₹299',
      description: 'Deep dive into Patanjali\'s Yoga Sutras and their application in modern life.',
    },
  ];

  const categories = ['all', 'Ayurveda', 'Yoga', 'Sanskrit', 'Meditation'];

  const filteredClasses = selectedCategory === 'all' 
    ? upcomingClasses 
    : upcomingClasses.filter(c => c.category === selectedCategory);

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-green-600 to-teal-600 text-white py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4">Live Classes</h1>
          <p className="text-xl text-green-100 max-w-3xl">
            Join live, interactive sessions with expert instructors. Ask questions, practice together, and learn in real-time.
          </p>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        {/* Benefits */}
        <div className="grid md:grid-cols-4 gap-6 mb-12">
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <div className="text-4xl mb-3">🎙️</div>
            <h3 className="font-semibold text-gray-900 mb-2">Live Interaction</h3>
            <p className="text-sm text-gray-600">Ask questions and get instant feedback</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <div className="text-4xl mb-3">📹</div>
            <h3 className="font-semibold text-gray-900 mb-2">Recorded Sessions</h3>
            <p className="text-sm text-gray-600">Access recordings after the class</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <div className="text-4xl mb-3">🎯</div>
            <h3 className="font-semibold text-gray-900 mb-2">Practical Focus</h3>
            <p className="text-sm text-gray-600">Hands-on learning and practice</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow text-center">
            <div className="text-4xl mb-3">👥</div>
            <h3 className="font-semibold text-gray-900 mb-2">Small Groups</h3>
            <p className="text-sm text-gray-600">Limited seats for personal attention</p>
          </div>
        </div>

        {/* Category Filter */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-6 py-2 rounded-full font-medium transition-colors ${
                  selectedCategory === category
                    ? 'bg-green-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {category === 'all' ? 'All Classes' : category}
              </button>
            ))}
          </div>
        </div>

        {/* Upcoming Classes */}
        <div>
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Upcoming Sessions</h2>
          <div className="grid md:grid-cols-2 gap-6">
            {filteredClasses.map((classItem) => (
              <div key={classItem.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow overflow-hidden">
                <div className="p-6">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <span className="px-3 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                        {classItem.category}
                      </span>
                      <span className="ml-2 px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                        {classItem.level}
                      </span>
                    </div>
                    <div className="text-right">
                      <div className="text-lg font-bold text-green-600">{classItem.price}</div>
                    </div>
                  </div>

                  <h3 className="text-xl font-bold text-gray-900 mb-2">{classItem.title}</h3>
                  <p className="text-gray-600 text-sm mb-4">{classItem.description}</p>

                  <div className="space-y-2 text-sm text-gray-700 mb-4">
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">👨‍🏫</span>
                      <span>{classItem.instructor}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">📅</span>
                      <span>{new Date(classItem.date).toLocaleDateString('en-US', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">⏰</span>
                      <span>{classItem.time} ({classItem.duration})</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">🪧</span>
                      <span>{classItem.seats} seats available</span>
                    </div>
                  </div>

                  <button
                    onClick={() => navigate('/signup')}
                    className="w-full bg-green-600 text-white py-3 rounded-lg hover:bg-green-700 transition-colors font-semibold"
                  >
                    Register Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 bg-gradient-to-r from-teal-600 to-green-600 rounded-lg p-8 text-white text-center">
          <h2 className="text-3xl font-bold mb-4">Want to Host a Live Class?</h2>
          <p className="text-lg text-teal-100 mb-6">
            Share your expertise and teach live classes to our community.
          </p>
          <button
            onClick={() => navigate('/for-business')}
            className="bg-white text-green-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors"
          >
            Apply as Instructor
          </button>
        </div>
      </div>

      <Footer />
    </div>
  );
};

export default LiveClasses;