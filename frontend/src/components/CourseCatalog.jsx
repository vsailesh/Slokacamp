import React, { useState } from 'react';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Search, Filter, Clock, Users, BookOpen, Star, Play } from 'lucide-react';
import { Link } from 'react-router-dom';
import { topCourses, careerTracks, skillTracks } from '../data/mockData';

const CourseCatalog = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedLevel, setSelectedLevel] = useState('all');
  const [sortBy, setSortBy] = useState('popular');
  const [activeTab, setActiveTab] = useState('all-courses');

  // Combine all courses for the "All Courses" tab
  const allCourses = [
    ...topCourses,
    ...careerTracks.map(track => ({ ...track, type: 'track' })),
    ...skillTracks.map(track => ({ ...track, type: 'track' }))
  ];

  const categories = [
    { value: 'all', label: 'All Categories' },
    { value: 'slokas', label: 'Sanskrit Slokas' },
    { value: 'ayurveda', label: 'Ayurveda' },
    { value: 'career', label: 'Career Tracks' },
    { value: 'skill', label: 'Skill Tracks' }
  ];

  const levels = [
    { value: 'all', label: 'All Levels' },
    { value: 'basic', label: 'Basic' },
    { value: 'intermediate', label: 'Intermediate' },
    { value: 'advanced', label: 'Advanced' }
  ];

  const filterCourses = (courses) => {
    return courses.filter(course => {
      const matchesSearch = course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           course.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'all' || course.category === selectedCategory;
      const matchesLevel = selectedLevel === 'all' || course.level.toLowerCase() === selectedLevel;
      
      return matchesSearch && matchesCategory && matchesLevel;
    });
  };

  const sortCourses = (courses) => {
    const sorted = [...courses];
    switch (sortBy) {
      case 'popular':
        return sorted.sort((a, b) => parseInt(b.learners) - parseInt(a.learners));
      case 'newest':
        return sorted; // Would sort by creation date in real app
      case 'title':
        return sorted.sort((a, b) => a.title.localeCompare(b.title));
      case 'duration':
        return sorted.sort((a, b) => parseInt(a.duration) - parseInt(b.duration));
      default:
        return sorted;
    }
  };

  const CourseCard = ({ course }) => {
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
        case 'slokas': return '🕉';
        case 'ayurveda': return '🌿';
        case 'career': return '🎯';
        case 'skill': return '⚡';
        default: return '📚';
      }
    };

    return (
      <Card className="hover:shadow-lg transition-shadow duration-300">
        <CardContent className="p-0">
          {/* Course Image Placeholder */}
          <div className="h-48 bg-gradient-to-br from-orange-100 to-red-100 flex items-center justify-center">
            <div className="text-4xl">{getCategoryIcon(course.category)}</div>
          </div>
          
          <div className="p-6">
            <div className="flex items-center justify-between mb-2">
              <Badge className={getLevelColor(course.level)}>
                {course.level} Level
              </Badge>
              {course.type === 'track' && (
                <Badge variant="outline">Track</Badge>
              )}
            </div>
            
            <h3 className="text-lg font-bold text-gray-900 mb-2 line-clamp-2">{course.title}</h3>
            <p className="text-sm text-gray-600 mb-4 line-clamp-3">{course.description}</p>
            
            <div className="flex items-center justify-between text-sm text-gray-500 mb-4">
              <div className="flex items-center space-x-4">
                <div className="flex items-center">
                  <Clock className="w-4 h-4 mr-1" />
                  {course.duration}
                </div>
                <div className="flex items-center">
                  <Users className="w-4 h-4 mr-1" />
                  {course.learners}
                </div>
              </div>
              <div className="flex items-center">
                <Star className="w-4 h-4 mr-1 text-yellow-400 fill-current" />
                <span>4.8</span>
              </div>
            </div>
            
            <div className="flex space-x-2">
              <Button className="flex-1 bg-orange-600 hover:bg-orange-700" asChild>
                <Link to={`/course/${course.id}`}>
                  <BookOpen className="w-4 h-4 mr-2" />
                  View Course
                </Link>
              </Button>
              
              {course.category === 'slokas' && (
                <Button variant="outline" size="sm" asChild>
                  <Link to={`/practice/${course.id}`}>
                    <Play className="w-4 h-4" />
                  </Link>
                </Button>
              )}
            </div>
          </div>
        </CardContent>
      </Card>
    );
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">Explore Our Course Catalog</h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover comprehensive courses in Sanskrit, Ayurveda, and spiritual practices. 
              Start your journey toward ancient wisdom today.
            </p>
          </div>
          
          {/* Search and Filters */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
              <Input 
                placeholder="Search courses..." 
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            
            <Select value={selectedCategory} onValueChange={setSelectedCategory}>
              <SelectTrigger>
                <Filter className="w-4 h-4 mr-2" />
                <SelectValue placeholder="Category" />
              </SelectTrigger>
              <SelectContent>
                {categories.map(category => (
                  <SelectItem key={category.value} value={category.value}>
                    {category.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={selectedLevel} onValueChange={setSelectedLevel}>
              <SelectTrigger>
                <SelectValue placeholder="Level" />
              </SelectTrigger>
              <SelectContent>
                {levels.map(level => (
                  <SelectItem key={level.value} value={level.value}>
                    {level.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            
            <Select value={sortBy} onValueChange={setSortBy}>
              <SelectTrigger>
                <SelectValue placeholder="Sort by" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="popular">Most Popular</SelectItem>
                <SelectItem value="newest">Newest</SelectItem>
                <SelectItem value="title">Title A-Z</SelectItem>
                <SelectItem value="duration">Duration</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="all-courses">All Courses ({allCourses.length})</TabsTrigger>
            <TabsTrigger value="individual">Individual Courses</TabsTrigger>
            <TabsTrigger value="career-tracks">Career Tracks</TabsTrigger>
            <TabsTrigger value="skill-tracks">Skill Tracks</TabsTrigger>
          </TabsList>

          <TabsContent value="all-courses">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortCourses(filterCourses(allCourses)).map(course => (
                <CourseCard key={`${course.category}-${course.id}`} course={course} />
              ))}
            </div>
            
            {filterCourses(allCourses).length === 0 && (
              <div className="text-center py-12">
                <div className="text-6xl mb-4">🔍</div>
                <h3 className="text-xl font-semibold text-gray-900 mb-2">No courses found</h3>
                <p className="text-gray-600">Try adjusting your search or filter criteria.</p>
              </div>
            )}
          </TabsContent>

          <TabsContent value="individual">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortCourses(filterCourses(topCourses)).map(course => (
                <CourseCard key={course.id} course={course} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="career-tracks">
            <div className="grid md:grid-cols-2 gap-6">
              {sortCourses(filterCourses(careerTracks)).map(course => (
                <CourseCard key={course.id} course={{ ...course, type: 'track' }} />
              ))}
            </div>
          </TabsContent>

          <TabsContent value="skill-tracks">
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {sortCourses(filterCourses(skillTracks)).map(course => (
                <CourseCard key={course.id} course={{ ...course, type: 'track' }} />
              ))}
            </div>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default CourseCatalog;