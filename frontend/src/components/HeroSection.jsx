import React from 'react';
import { Button } from './ui/button';
import { Play, Users, Award, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

const HeroSection = () => {
  return (
    <section className="bg-gradient-to-br from-orange-50 via-white to-red-50 py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Content */}
          <div className="text-center lg:text-left">
            <h1 className="text-5xl lg:text-6xl font-bold text-gray-900 leading-tight mb-6">
              Master Ancient
              <span className="block text-transparent bg-clip-text bg-gradient-to-r from-orange-600 to-red-600">
                Sanskrit Wisdom
              </span>
              in the Modern Way
            </h1>
            
            <p className="text-xl text-gray-600 mb-8 leading-relaxed">
              Learn Sanskrit slokas with Duolingo-style interactivity and explore Ayurvedic knowledge 
              through comprehensive video courses. Join live classes with expert teachers from India's top institutions.
            </p>

            {/* Stats */}
            <div className="flex flex-wrap justify-center lg:justify-start gap-8 mb-8 text-center">
              <div>
                <div className="text-2xl font-bold text-gray-900">2.5M+</div>
                <div className="text-sm text-gray-600">Learners Worldwide</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">450+</div>
                <div className="text-sm text-gray-600">Courses Available</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-gray-900">150+</div>
                <div className="text-sm text-gray-600">Countries</div>
              </div>
            </div>

            {/* CTA Buttons */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center lg:justify-start mb-8">
              <Button 
                size="lg" 
                className="bg-orange-600 hover:bg-orange-700 text-white px-8 py-4 text-lg font-semibold transition-all duration-300 transform hover:scale-105"
                asChild
              >
                <Link to="/signup">
                  Start Learning for Free
                </Link>
              </Button>
              
              <Button 
                variant="outline" 
                size="lg" 
                className="border-2 border-gray-300 hover:border-orange-600 text-gray-700 hover:text-orange-600 px-8 py-4 text-lg font-semibold transition-all duration-300 hover:shadow-lg"
                asChild
              >
                <Link to="/demo" className="flex items-center">
                  <Play className="w-5 h-5 mr-2" />
                  Watch Demo
                </Link>
              </Button>
            </div>

            {/* Trust Indicators */}
            <div className="flex flex-wrap items-center justify-center lg:justify-start gap-6 text-sm text-gray-500">
              <div className="flex items-center">
                <Users className="w-4 h-4 mr-2" />
                Trusted by 2.5M+ learners
              </div>
              <div className="flex items-center">
                <Award className="w-4 h-4 mr-2" />
                Industry-recognized certificates
              </div>
              <div className="flex items-center">
                <BookOpen className="w-4 h-4 mr-2" />
                Learn from Sanskrit scholars
              </div>
            </div>
          </div>

          {/* Right Visual */}
          <div className="relative">
            {/* Main Visual Container */}
            <div className="relative bg-white rounded-2xl shadow-2xl p-8 transform rotate-2 hover:rotate-0 transition-transform duration-500">
              <div className="absolute -top-4 -left-4 w-12 h-12 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center">
                <span className="text-white text-xl">🕉</span>
              </div>
              
              {/* Mock Learning Interface */}
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Today's Sanskrit Lesson</h3>
                  <div className="flex items-center text-orange-600">
                    <span className="text-sm font-medium">Streak: 7 days 🔥</span>
                  </div>
                </div>
                
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-center text-2xl font-sanskrit text-gray-800 mb-2">
                    सर्वे भवन्तु सुखिनः
                  </p>
                  <p className="text-center text-gray-600 text-sm">
                    "May all beings be happy"
                  </p>
                </div>
                
                <div className="grid grid-cols-2 gap-3">
                  <button className="bg-orange-100 hover:bg-orange-200 text-orange-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    Play Audio 🔊
                  </button>
                  <button className="bg-green-100 hover:bg-green-200 text-green-800 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
                    Practice 📝
                  </button>
                </div>
                
                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="flex justify-between text-sm text-gray-600 mb-1">
                    <span>Progress</span>
                    <span>75%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                  </div>
                </div>
              </div>
            </div>
            
            {/* Floating Elements */}
            <div className="absolute -top-6 right-4 bg-green-500 text-white px-3 py-1 rounded-full text-sm font-medium animate-bounce">
              +10 XP
            </div>
            
            <div className="absolute -bottom-4 -left-2 bg-white rounded-lg shadow-lg p-3 transform -rotate-6">
              <div className="flex items-center space-x-2">
                <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center text-white text-xs font-bold">
                  A
                </div>
                <div className="text-xs">
                  <div className="font-medium text-gray-900">Ayurveda Course</div>
                  <div className="text-gray-600">Lesson 3 of 12</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default HeroSection;