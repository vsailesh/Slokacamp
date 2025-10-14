import React, { useState } from 'react';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import HeroSection from './HeroSection';
import CourseCard from './CourseCard';
import { topCourses, careerTracks, skillTracks, liveClasses, testimonials, features } from '../data/mockData';
import { Users, Award, Clock, Star, ChevronRight, Play } from 'lucide-react';
import { Link } from 'react-router-dom';

const Homepage = () => {
  const [activeTab, setActiveTab] = useState('top-courses');

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <HeroSection />

      {/* Course Categories Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">A path for every spiritual goal</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Whether you're beginning your Sanskrit journey or deepening your Ayurvedic knowledge, 
              we have the perfect learning path for you.
            </p>
          </div>

          {/* Tabs for different course types */}
          <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
            <TabsList className="grid w-full grid-cols-2 lg:grid-cols-4 mb-8">
              <TabsTrigger value="top-courses" className="text-sm font-medium">Top Courses</TabsTrigger>
              <TabsTrigger value="career-tracks" className="text-sm font-medium">Career Tracks</TabsTrigger>
              <TabsTrigger value="skill-tracks" className="text-sm font-medium">Skill Tracks</TabsTrigger>
              <TabsTrigger value="live-classes" className="text-sm font-medium">Live Classes</TabsTrigger>
            </TabsList>

            <TabsContent value="top-courses" className="space-y-8">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {topCourses.slice(0, 6).map((course) => (
                  <CourseCard key={course.id} course={course} showCategory />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="career-tracks" className="space-y-8">
              <div className="grid md:grid-cols-2 gap-6">
                {careerTracks.map((track) => (
                  <CourseCard key={track.id} course={track} showCategory />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="skill-tracks" className="space-y-8">
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {skillTracks.map((track) => (
                  <CourseCard key={track.id} course={track} showCategory />
                ))}
              </div>
            </TabsContent>

            <TabsContent value="live-classes" className="space-y-8">
              <div className="grid md:grid-cols-2 gap-6">
                {liveClasses.map((liveClass) => (
                  <div key={liveClass.id} className="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 border border-gray-100 p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-bold text-gray-900 mb-2">{liveClass.title}</h3>
                        <p className="text-orange-600 font-medium text-sm mb-1">with {liveClass.instructor}</p>
                        <div className="flex items-center text-gray-600 text-sm space-x-4">
                          <span>⏰ {liveClass.time}</span>
                          <span>⏱ {liveClass.duration}</span>
                        </div>
                      </div>
                      <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-xs font-medium">
                        LIVE
                      </span>
                    </div>
                    
                    <p className="text-gray-600 text-sm mb-4">{liveClass.description}</p>
                    
                    <div className="flex justify-between items-center">
                      <div className="flex items-center text-gray-500 text-sm">
                        <Users className="w-4 h-4 mr-1" />
                        {liveClass.attendees} attending
                      </div>
                      <Button className="bg-orange-600 hover:bg-orange-700 text-white">
                        Join Class
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </TabsContent>
          </Tabs>

          <div className="text-center mt-12">
            <Button variant="outline" size="lg" asChild>
              <Link to="/courses" className="flex items-center">
                Explore All Courses
                <ChevronRight className="w-5 h-5 ml-2" />
              </Link>
            </Button>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-16 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">A learning model that powers spiritual transformation</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Our unique approach combines ancient wisdom with modern technology to create an engaging and effective learning experience.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
            {features.map((feature, index) => {
              const IconComponent = {
                Users: Users,
                Award: Award,
                Clock: Clock,
                Users: Users
              }[feature.icon] || Users;

              return (
                <div key={index} className="text-center">
                  <div className="w-16 h-16 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto mb-4">
                    <IconComponent className="w-8 h-8 text-white" />
                  </div>
                  <h3 className="text-xl font-bold text-gray-900 mb-2">{feature.title}</h3>
                  <p className="text-gray-600">{feature.description}</p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Testimonials Section */}
      <section className="py-16 bg-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold text-gray-900 mb-4">Why 2.5M+ choose SlokaCamp</h2>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Join millions of learners worldwide who are transforming their lives through ancient wisdom.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {testimonials.slice(0, 3).map((testimonial) => (
              <div key={testimonial.id} className="bg-gray-50 rounded-xl p-6 hover:bg-gray-100 transition-colors">
                <div className="flex items-center mb-4">
                  <img 
                    src={testimonial.image} 
                    alt={testimonial.name}
                    className="w-12 h-12 rounded-full object-cover mr-4"
                  />
                  <div>
                    <h4 className="font-bold text-gray-900">{testimonial.name}</h4>
                    <p className="text-sm text-gray-600">{testimonial.role}</p>
                  </div>
                </div>
                <p className="text-gray-700 italic">"{testimonial.quote}"</p>
                <div className="flex items-center mt-3">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-orange-600 to-red-600">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl lg:text-5xl font-bold text-white mb-6">
            Begin your spiritual learning journey today
          </h2>
          <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
            Join 2.5M+ learners worldwide and start mastering Sanskrit slokas and Ayurvedic wisdom with expert guidance.
          </p>
          
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button 
              size="lg" 
              className="bg-white text-orange-600 hover:bg-gray-100 px-8 py-4 text-lg font-semibold transition-all duration-300 transform hover:scale-105"
              asChild
            >
              <Link to="/signup">Start Learning for Free</Link>
            </Button>
            
            <Button 
              variant="outline" 
              size="lg" 
              className="border-2 border-white text-white hover:bg-white hover:text-orange-600 px-8 py-4 text-lg font-semibold transition-all duration-300"
              asChild
            >
              <Link to="/demo" className="flex items-center">
                <Play className="w-5 h-5 mr-2" />
                Watch How It Works
              </Link>
            </Button>
          </div>
          
          <p className="text-orange-200 text-sm mt-6">
            Free forever. No credit card required. Start learning in 2 minutes.
          </p>
        </div>
      </section>
    </div>
  );
};

export default Homepage;