import React from 'react';
import { Link } from 'react-router-dom';
import { Button } from './ui/button';

const Footer = () => {
  return (
    <footer className="bg-gray-900 text-white py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {/* Brand */}
          <div className="lg:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 bg-gradient-to-br from-orange-500 to-red-500 rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">🕉</span>
              </div>
              <span className="text-2xl font-bold">SlokaCamp</span>
            </div>
            <p className="text-gray-300 max-w-md mb-6">
              Master Sanskrit slokas and Ayurvedic wisdom through interactive learning. 
              Join 2.5M+ learners worldwide on their spiritual journey.
            </p>
            <div className="flex space-x-4">
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                Twitter
              </Button>
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                Facebook
              </Button>
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                Instagram
              </Button>
              <Button variant="ghost" size="sm" className="text-gray-300 hover:text-white">
                YouTube
              </Button>
            </div>
          </div>

          {/* Learning Paths */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Learning Paths</h3>
            <ul className="space-y-3 text-gray-300">
              <li><Link to="/slokas" className="hover:text-white transition-colors">Sanskrit Slokas</Link></li>
              <li><Link to="/ayurveda" className="hover:text-white transition-colors">Ayurveda</Link></li>
              <li><Link to="/meditation" className="hover:text-white transition-colors">Meditation</Link></li>
              <li><Link to="/yoga" className="hover:text-white transition-colors">Yoga Philosophy</Link></li>
              <li><Link to="/astrology" className="hover:text-white transition-colors">Vedic Astrology</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h3 className="text-lg font-semibold mb-4">Company</h3>
            <ul className="space-y-3 text-gray-300">
              <li><Link to="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/careers" className="hover:text-white transition-colors">Careers</Link></li>
              <li><Link to="/for-business" className="hover:text-white transition-colors">For Business</Link></li>
              <li><Link to="/blog" className="hover:text-white transition-colors">Blog</Link></li>
              <li><Link to="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
        </div>

        <div className="border-t border-gray-800 mt-12 pt-8 flex flex-col md:flex-row justify-between items-center">
          <p className="text-gray-400 text-sm mb-4 md:mb-0">
            © 2024 SlokaCamp. All rights reserved. Spreading ancient wisdom through modern technology.
          </p>
          <div className="flex space-x-6 text-sm text-gray-400">
            <Link to="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link>
            <Link to="/terms" className="hover:text-white transition-colors">Terms of Service</Link>
            <Link to="/help" className="hover:text-white transition-colors">Help Center</Link>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;