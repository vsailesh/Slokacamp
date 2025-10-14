import React from 'react';
import { Button } from './ui/button';
import { Clock, Users, BookOpen } from 'lucide-react';
import { Link } from 'react-router-dom';

const CourseCard = ({ course, showCategory = false }) => {
  const getLevelColor = (level) => {
    switch (level.toLowerCase()) {
      case 'basic':
      case 'beginner':
        return 'bg-green-100 text-green-800';
      case 'intermediate':
        return 'bg-yellow-100 text-yellow-800';
      case 'advanced':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const getCategoryIcon = (category) => {
    switch (category) {
      case 'slokas':
        return '🕉';
      case 'ayurveda':
        return '🌿';
      case 'career':
        return '🎯';
      case 'skill':
        return '⚡';
      default:
        return '📚';
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-100 overflow-hidden">
      {/* Course Header */}
      <div className="p-6 pb-4">
        {showCategory && (
          <div className="flex items-center mb-3">
            <span className="text-lg mr-2">{getCategoryIcon(course.category)}</span>
            <span className="text-sm font-medium text-gray-600 capitalize">{course.category}</span>
          </div>
        )}
        
        <h3 className="text-xl font-bold text-gray-900 mb-2 line-clamp-2 hover:text-orange-600 transition-colors">
          <Link to={`/course/${course.id}`}>{course.title}</Link>
        </h3>
        
        <div className="flex items-center gap-2 mb-3">
          <span className={`px-2 py-1 rounded-full text-xs font-medium ${getLevelColor(course.level)}`}>
            {course.level} Level
          </span>
          {course.duration && (
            <div className="flex items-center text-gray-500 text-sm">
              <Clock className="w-4 h-4 mr-1" />
              {course.duration}
            </div>
          )}
        </div>
        
        <p className="text-gray-600 text-sm leading-relaxed mb-4 line-clamp-3">
          {course.description}
        </p>
      </div>

      {/* Course Footer */}
      <div className="px-6 pb-6">
        <div className="flex items-center justify-between mb-4">
          {course.learners && (
            <div className="flex items-center text-gray-500 text-sm">
              <Users className="w-4 h-4 mr-1" />
              {course.learners} learners
            </div>
          )}
          {course.instructor && (
            <div className="text-sm text-gray-600">
              by {course.instructor}
            </div>
          )}
        </div>
        
        <div className="flex gap-2">
          <Button 
            className="flex-1 bg-orange-600 hover:bg-orange-700 text-white transition-colors"
            asChild
          >
            <Link to={`/course/${course.id}`}>
              <BookOpen className="w-4 h-4 mr-2" />
              View Details
            </Link>
          </Button>
          
          {course.category === 'slokas' && (
            <Button 
              variant="outline" 
              className="border-orange-600 text-orange-600 hover:bg-orange-50"
              asChild
            >
              <Link to={`/practice/${course.id}`}>Practice</Link>
            </Button>
          )}
        </div>
      </div>
      
      {/* Progress Bar (if enrolled) */}
      {course.progress && (
        <div className="px-6 pb-4">
          <div className="flex justify-between text-sm text-gray-600 mb-1">
            <span>Progress</span>
            <span>{course.progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-gradient-to-r from-orange-500 to-red-500 h-2 rounded-full transition-all duration-300" 
              style={{ width: `${course.progress}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CourseCard;