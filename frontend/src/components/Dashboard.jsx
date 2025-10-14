import React, { useState } from 'react';
import { Button } from './ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { BookOpen, Clock, Award, TrendingUp, Calendar, Users, Play, CheckCircle } from 'lucide-react';
import { Link } from 'react-router-dom';

const Dashboard = () => {
  const [activeTab, setActiveTab] = useState('progress');

  const enrolledCourses = [
    {
      id: 1,
      title: 'Introduction to Sanskrit Slokas',
      progress: 75,
      totalLessons: 12,
      completedLessons: 9,
      lastAccessed: '2 hours ago',
      nextLesson: 'Bhagavad Gita Chapter 2',
      category: 'slokas',
      timeSpent: '8h 30m',
      streak: 7
    },
    {
      id: 2,
      title: 'Ayurvedic Fundamentals',
      progress: 45,
      totalLessons: 16,
      completedLessons: 7,
      lastAccessed: '1 day ago',
      nextLesson: 'Understanding Doshas',
      category: 'ayurveda',
      timeSpent: '6h 15m',
      streak: 3
    },
    {
      id: 3,
      title: 'Vedic Chanting Techniques',
      progress: 90,
      totalLessons: 8,
      completedLessons: 7,
      lastAccessed: '3 hours ago',
      nextLesson: 'Advanced Pronunciation',
      category: 'slokas',
      timeSpent: '4h 45m',
      streak: 12
    }
  ];

  const recentActivity = [
    { type: 'completed', course: 'Sanskrit Slokas', lesson: 'Pronunciation Basics', time: '2 hours ago', xp: 50 },
    { type: 'started', course: 'Ayurvedic Fundamentals', lesson: 'Introduction to Ayurveda', time: '1 day ago', xp: 25 },
    { type: 'achievement', course: 'Vedic Chanting', lesson: 'Week 1 Complete!', time: '2 days ago', xp: 100 },
    { type: 'practice', course: 'Sanskrit Slokas', lesson: 'Daily Practice Session', time: '3 days ago', xp: 30 }
  ];

  const upcomingLiveClasses = [
    {
      id: 1,
      title: 'Weekly Sanskrit Circle',
      instructor: 'Dr. Priya Sharma',
      time: 'Today at 7:00 PM IST',
      duration: '90 mins',
      enrolled: true
    },
    {
      id: 2,
      title: 'Ayurvedic Consultation Workshop',
      instructor: 'Vaidya Rajesh Kumar',
      time: 'Tomorrow at 6:00 PM IST',
      duration: '120 mins',
      enrolled: false
    }
  ];

  const stats = {
    totalXP: 2450,
    coursesCompleted: 3,
    currentStreak: 7,
    totalHours: 24.5
  };

  const getCategoryIcon = (category) => {
    return category === 'slokas' ? '🕉' : '🌿';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">My Learning Dashboard</h1>
              <p className="text-gray-600">Continue your spiritual learning journey</p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-center">
                <div className="text-2xl font-bold text-orange-600">{stats.totalXP}</div>
                <div className="text-sm text-gray-600">Total XP</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-600">{stats.currentStreak}</div>
                <div className="text-sm text-gray-600">Day Streak 🔥</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
          <TabsList className="grid w-full grid-cols-4 mb-8">
            <TabsTrigger value="progress" className="text-sm font-medium">My Progress</TabsTrigger>
            <TabsTrigger value="courses" className="text-sm font-medium">My Courses</TabsTrigger>
            <TabsTrigger value="activity" className="text-sm font-medium">Recent Activity</TabsTrigger>
            <TabsTrigger value="live" className="text-sm font-medium">Live Classes</TabsTrigger>
          </TabsList>

          {/* My Progress Tab */}
          <TabsContent value="progress" className="space-y-8">
            {/* Stats Cards */}
            <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Total XP</CardTitle>
                  <TrendingUp className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalXP}</div>
                  <p className="text-xs text-muted-foreground">+180 from last week</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Courses Completed</CardTitle>
                  <Award className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.coursesCompleted}</div>
                  <p className="text-xs text-muted-foreground">2 in progress</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Current Streak</CardTitle>
                  <Calendar className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.currentStreak} days</div>
                  <p className="text-xs text-muted-foreground">Keep it up! 🔥</p>
                </CardContent>
              </Card>
              
              <Card>
                <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                  <CardTitle className="text-sm font-medium">Learning Time</CardTitle>
                  <Clock className="h-4 w-4 text-muted-foreground" />
                </CardHeader>
                <CardContent>
                  <div className="text-2xl font-bold">{stats.totalHours}h</div>
                  <p className="text-xs text-muted-foreground">This month</p>
                </CardContent>
              </Card>
            </div>

            {/* Continue Learning */}
            <Card>
              <CardHeader>
                <CardTitle>Continue Learning</CardTitle>
                <CardDescription>Pick up where you left off</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {enrolledCourses.slice(0, 2).map(course => (
                  <div key={course.id} className="flex items-center space-x-4 p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                    <div className="text-2xl">{getCategoryIcon(course.category)}</div>
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{course.title}</h3>
                      <p className="text-sm text-gray-600">Next: {course.nextLesson}</p>
                      <div className="mt-2">
                        <Progress value={course.progress} className="w-full" />
                        <div className="flex justify-between text-xs text-gray-500 mt-1">
                          <span>{course.completedLessons}/{course.totalLessons} lessons</span>
                          <span>{course.progress}% complete</span>
                        </div>
                      </div>
                    </div>
                    <Button className="bg-orange-600 hover:bg-orange-700" asChild>
                      <Link to={`/learn/${course.id}`}>Continue</Link>
                    </Button>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* My Courses Tab */}
          <TabsContent value="courses" className="space-y-6">
            <div className="grid gap-6">
              {enrolledCourses.map(course => (
                <Card key={course.id}>
                  <CardContent className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-4">
                        <div className="text-3xl">{getCategoryIcon(course.category)}</div>
                        <div className="flex-1">
                          <h3 className="text-xl font-bold text-gray-900 mb-2">{course.title}</h3>
                          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 text-sm text-gray-600 mb-4">
                            <div className="flex items-center">
                              <BookOpen className="w-4 h-4 mr-1" />
                              {course.completedLessons}/{course.totalLessons} lessons
                            </div>
                            <div className="flex items-center">
                              <Clock className="w-4 h-4 mr-1" />
                              {course.timeSpent}
                            </div>
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              {course.lastAccessed}
                            </div>
                            <div className="flex items-center">
                              <TrendingUp className="w-4 h-4 mr-1" />
                              {course.streak} day streak
                            </div>
                          </div>
                          
                          <div className="mb-4">
                            <Progress value={course.progress} className="w-full mb-2" />
                            <div className="flex justify-between text-sm">
                              <span className="text-gray-600">{course.progress}% Complete</span>
                              <span className="text-gray-600">Next: {course.nextLesson}</span>
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex space-x-2">
                        <Button variant="outline" asChild>
                          <Link to={`/course/${course.id}`}>View Details</Link>
                        </Button>
                        <Button className="bg-orange-600 hover:bg-orange-700" asChild>
                          <Link to={`/learn/${course.id}`}>Continue Learning</Link>
                        </Button>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </TabsContent>

          {/* Recent Activity Tab */}
          <TabsContent value="activity" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Recent Activity</CardTitle>
                <CardDescription>Your learning progress over the past week</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {recentActivity.map((activity, index) => (
                  <div key={index} className="flex items-center space-x-4 p-3 border border-gray-200 rounded-lg">
                    <div className="w-10 h-10 rounded-full bg-green-100 flex items-center justify-center">
                      {activity.type === 'completed' && <CheckCircle className="w-5 h-5 text-green-600" />}
                      {activity.type === 'started' && <Play className="w-5 h-5 text-blue-600" />}
                      {activity.type === 'achievement' && <Award className="w-5 h-5 text-yellow-600" />}
                      {activity.type === 'practice' && <BookOpen className="w-5 h-5 text-purple-600" />}
                    </div>
                    <div className="flex-1">
                      <p className="font-medium text-gray-900">
                        {activity.type === 'completed' && 'Completed lesson:'} 
                        {activity.type === 'started' && 'Started lesson:'}
                        {activity.type === 'achievement' && 'Achievement unlocked:'}
                        {activity.type === 'practice' && 'Practice session:'}
                        {' '}{activity.lesson}
                      </p>
                      <p className="text-sm text-gray-600">{activity.course} • {activity.time}</p>
                    </div>
                    <Badge variant="outline">+{activity.xp} XP</Badge>
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>

          {/* Live Classes Tab */}
          <TabsContent value="live" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle>Upcoming Live Classes</CardTitle>
                <CardDescription>Join live sessions with expert instructors</CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                {upcomingLiveClasses.map(liveClass => (
                  <div key={liveClass.id} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center">
                        <Users className="w-6 h-6 text-red-600" />
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900">{liveClass.title}</h3>
                        <p className="text-sm text-gray-600">with {liveClass.instructor}</p>
                        <div className="flex items-center text-sm text-gray-500 mt-1">
                          <Clock className="w-4 h-4 mr-1" />
                          {liveClass.time} • {liveClass.duration}
                        </div>
                      </div>
                    </div>
                    
                    {liveClass.enrolled ? (
                      <Badge className="bg-green-100 text-green-800">Enrolled</Badge>
                    ) : (
                      <Button variant="outline">Enroll</Button>
                    )}
                  </div>
                ))}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
};

export default Dashboard;