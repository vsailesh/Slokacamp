import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from './ui/button';
import { Menu, X } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const Navbar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, logout, isAdmin } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  const categories = [
    'Sanskrit Slokas',
    'Ayurveda', 
    'Meditation',
    'Yoga Philosophy',
    'Vedic Astrology',
    'Live Classes'
  ];

  return (
    <>
      {/* Promotional Banner */}
      <div className="bg-gradient-to-r from-orange-500 to-red-500 text-white py-2 px-4 text-center text-sm">
        <span className="font-medium">🎉 Welcome 2.5M+ learners! Save 50% on SlokaCamp Premium!</span>
        <Button variant="ghost" size="sm" className="ml-2 text-white hover:text-orange-100">
          Learn More
        </Button>
      </div>

      {/* Main Navigation */}
      <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
        {/* Desktop Categories Bar */}
        <div className="hidden md:block bg-gray-50 border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex items-center justify-center space-x-8 py-2">
              {categories.map((category) => (
                <Link
                  key={category}
                  to={`/${category.toLowerCase().replace(' ', '-')}`}
                  className="text-sm text-gray-600 hover:text-orange-600 transition-colors duration-200"
                >
                  {category}
                </Link>
              ))}
            </div>
          </div>
        </div>

        {/* Main Navbar */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            {/* Logo */}
            <Link to="/" className="flex items-center space-x-2">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🕉</span>
              </div>
              <span className="text-2xl font-bold text-gray-900">SlokaCamp</span>
            </Link>

            {/* Desktop Navigation */}
            <div className="hidden md:flex items-center space-x-6">
              <Link to="/courses" className="text-gray-700 hover:text-orange-600 font-medium">
                All Courses
              </Link>
              <Link to="/career-tracks" className="text-gray-700 hover:text-orange-600 font-medium">
                Career Tracks
              </Link>
              <Link to="/live-classes" className="text-gray-700 hover:text-orange-600 font-medium">
                Live Classes
              </Link>
              <Link to="/discussions" className="text-gray-700 hover:text-orange-600 font-medium">
                Discussions
              </Link>
              <Link to="/for-business" className="text-gray-700 hover:text-orange-600 font-medium">
                For Business
              </Link>
            </div>

            {/* Auth Buttons */}
            <div className="hidden md:flex items-center space-x-3">
              {user ? (
                <>
                  <span className="text-sm text-gray-600">Welcome, {user.full_name}</span>
                  {isAdmin() && (
                    <Button variant="outline" asChild>
                      <Link to="/admin">Admin</Link>
                    </Button>
                  )}
                  <Button variant="ghost" asChild>
                    <Link to="/dashboard">Dashboard</Link>
                  </Button>
                  <Button 
                    variant="outline" 
                    onClick={handleLogout}
                    className="text-red-600 hover:text-red-700 hover:bg-red-50"
                  >
                    Sign Out
                  </Button>
                </>
              ) : (
                <>
                  <Button variant="ghost" asChild>
                    <Link to="/signin">Sign In</Link>
                  </Button>
                  <Button className="bg-orange-600 hover:bg-orange-700 text-white" asChild>
                    <Link to="/signup">Start Learning</Link>
                  </Button>
                </>
              )}
            </div>

            {/* Mobile menu button */}
            <Button
              variant="ghost"
              className="md:hidden"
              onClick={() => setIsMenuOpen(!isMenuOpen)}
            >
              {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
            </Button>
          </div>

          {/* Mobile Menu */}
          {isMenuOpen && (
            <div className="md:hidden py-4 border-t border-gray-200">
              <div className="flex flex-col space-y-4">
                <Link to="/courses" className="text-gray-700 hover:text-orange-600 font-medium">
                  All Courses
                </Link>
                <Link to="/career-tracks" className="text-gray-700 hover:text-orange-600 font-medium">
                  Career Tracks
                </Link>
                <Link to="/live-classes" className="text-gray-700 hover:text-orange-600 font-medium">
                  Live Classes
                </Link>
                <Link to="/discussions" className="text-gray-700 hover:text-orange-600 font-medium">
                  Discussions
                </Link>
                <Link to="/for-business" className="text-gray-700 hover:text-orange-600 font-medium">
                  For Business
                </Link>
                <div className="pt-4 border-t border-gray-200 flex flex-col space-y-2">
                  {user ? (
                    <>
                      <div className="text-sm text-gray-600 px-4">Welcome, {user.full_name}</div>
                      {isAdmin() && (
                        <Button variant="outline" asChild>
                          <Link to="/admin">Admin Dashboard</Link>
                        </Button>
                      )}
                      <Button variant="ghost" asChild>
                        <Link to="/dashboard">My Dashboard</Link>
                      </Button>
                      <Button 
                        variant="outline" 
                        onClick={handleLogout}
                        className="text-red-600 hover:text-red-700"
                      >
                        Sign Out
                      </Button>
                    </>
                  ) : (
                    <>
                      <Button variant="ghost" asChild>
                        <Link to="/signin">Sign In</Link>
                      </Button>
                      <Button className="bg-orange-600 hover:bg-orange-700 text-white" asChild>
                        <Link to="/signup">Start Learning</Link>
                      </Button>
                    </>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </nav>
    </>
  );
};

export default Navbar;