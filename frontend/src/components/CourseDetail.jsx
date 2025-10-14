import React from 'react';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { Progress } from './ui/progress';
import { Clock, Users, BookOpen, Play, CheckCircle, Lock, Star, Award } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

const CourseDetail = () => {
  const { courseId } = useParams();
  
  // Mock course data - would be fetched from API
  const course = {
    id: 1,
    title: "Introduction to Sanskrit Slokas",
    description: "Master the basics of Sanskrit pronunciation and learn fundamental slokas from ancient texts including Bhagavad Gita, Upanishads, and Vedic hymns.",
    instructor: {
      name: "Dr. Priya Sharma",
      title: "Sanskrit Scholar & Spiritual Teacher",
      image: "https://images.unsplash.com/photo-1494790108755-2616c4f6d2cc?w=400&h=400&fit=crop&crop=face",
      bio: "Dr. Sharma has 15+ years of experience teaching Sanskrit and Vedic studies at prestigious institutions."
    },
    level: "Basic",
    duration: "4 hours",
    learners: "45.2K",
    rating: 4.8,
    reviewCount: 2840,
    category: "slokas",
    price: "Free",
    enrolled: true,
    progress: 45,
    completedLessons: 5,
    totalLessons: 12,
    skills: ["Sanskrit Reading", "Pronunciation", "Spiritual Practice", "Meditation"],
    whatYouLearn: [
      "Master Sanskrit alphabet (Devanagari script)",
      "Proper pronunciation of Sanskrit sounds",
      "Understand meaning of fundamental slokas",
      "Daily practice routine for spiritual growth",
      "Connect with ancient wisdom traditions"
    ],
    chapters: [
      {
        id: 1,
        title: "Introduction to Sanskrit",
        lessons: [
          { id: 1, title: "What is Sanskrit?", duration: "5 min", type: "video", completed: true },
          { id: 2, title: "Importance in Spiritual Practice", duration: "8 min", type: "video", completed: true },
          { id: 3, title: "Your Learning Journey", duration: "3 min", type: "text", completed: true }
        ],
        completed: true
      },
      {
        id: 2,
        title: "Sanskrit Alphabet & Sounds",
        lessons: [
          { id: 4, title: "Vowels (स्वर)", duration: "12 min", type: "interactive", completed: true },
          { id: 5, title: "Consonants (व्यंजन)", duration: "15 min", type: "interactive", completed: true },
          { id: 6, title: "Pronunciation Practice", duration: "10 min", type: "audio", completed: false, current: true }
        ],
        completed: false
      },
      {
        id: 3,
        title: "Basic Slokas",
        lessons: [
          { id: 7, title: "Gayatri Mantra", duration: "18 min", type: "video", completed: false },
          { id: 8, title: "Peace Mantras", duration: "20 min", type: "interactive", completed: false },
          { id: 9, title: "Daily Practice Slokas", duration: "25 min", type: "video", completed: false }
        ],
        completed: false
      },
      {
        id: 4,
        title: "Bhagavad Gita Essentials",
        lessons: [
          { id: 10, title: "Chapter 2: Key Verses", duration: "30 min", type: "video", completed: false },
          { id: 11, title: "Understanding Context", duration: "15 min", type: "text", completed: false },
          { id: 12, title: "Final Practice & Assessment", duration: "20 min", type: "quiz", completed: false }
        ],
        completed: false
      }
    ],
    reviews: [
      {
        id: 1,
        name: "Arjun Patel",
        rating: 5,
        date: "2 weeks ago",
        comment: "Excellent course! Dr. Sharma's teaching style makes Sanskrit accessible to beginners. The pronunciation guides are incredibly helpful."
      },
      {
        id: 2,
        name: "Maya Singh",
        rating: 5,
        date: "1 month ago",
        comment: "I've always wanted to learn Sanskrit but found it intimidating. This course breaks it down perfectly. Love the interactive exercises!"
      },
      {
        id: 3,
        name: "Raj Krishnan",
        rating: 4,
        date: "3 weeks ago",
        comment: "Great content and structure. Would love to see more advanced courses from Dr. Sharma."
      }
    ]
  };

  const getLessonIcon = (type) => {
    switch (type) {
      case 'video': return <Play className="w-4 h-4" />;
      case 'interactive': return <BookOpen className="w-4 h-4" />;
      case 'audio': return <Users className="w-4 h-4" />;
      case 'quiz': return <Award className="w-4 h-4" />;
      default: return <BookOpen className="w-4 h-4" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Course Header */}
      <div className="bg-gradient-to-br from-orange-600 to-red-600 text-white">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="grid lg:grid-cols-3 gap-8">
            <div className="lg:col-span-2">
              <div className="flex items-center space-x-2 mb-4">
                <Badge className="bg-white/20 text-white">{course.level} Level</Badge>
                <Badge className="bg-white/20 text-white">🕉 Sanskrit</Badge>
              </div>
              
              <h1 className="text-4xl lg:text-5xl font-bold mb-4">{course.title}</h1>
              <p className="text-xl text-orange-100 mb-6">{course.description}</p>
              
              <div className="flex flex-wrap items-center gap-6 text-orange-100">
                <div className="flex items-center">
                  <Clock className="w-5 h-5 mr-2" />
                  {course.duration}
                </div>
                <div className="flex items-center">
                  <Users className="w-5 h-5 mr-2" />
                  {course.learners} learners
                </div>
                <div className="flex items-center">
                  <Star className="w-5 h-5 mr-2 fill-current" />
                  {course.rating} ({course.reviewCount} reviews)
                </div>
                <div className="flex items-center">
                  <BookOpen className="w-5 h-5 mr-2" />
                  {course.totalLessons} lessons
                </div>
              </div>
            </div>
            
            {/* Course Card */}
            <div className="lg:col-span-1">
              <Card className="bg-white">
                <CardContent className="p-6">
                  {course.enrolled ? (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-3xl mb-2">🕉</div>
                        <p className="text-sm text-gray-600 mb-4">Your Progress</p>
                        <Progress value={course.progress} className="w-full mb-2" />
                        <p className="text-sm text-gray-600">
                          {course.completedLessons}/{course.totalLessons} lessons • {course.progress}% complete
                        </p>
                      </div>
                      
                      <Button className="w-full bg-orange-600 hover:bg-orange-700" asChild>
                        <Link to={`/learn/${course.id}`}>Continue Learning</Link>
                      </Button>
                      
                      <Button variant="outline" className="w-full" asChild>
                        <Link to={`/practice/${course.id}`}>Practice Mode</Link>
                      </Button>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="text-center">
                        <div className="text-4xl font-bold text-green-600 mb-2">{course.price}</div>
                        <p className="text-sm text-gray-600">Full course access</p>
                      </div>
                      
                      <Button className="w-full bg-orange-600 hover:bg-orange-700">
                        Enroll Now
                      </Button>
                      
                      <Button variant="outline" className="w-full">
                        Try Free Lesson
                      </Button>
                    </div>
                  )}
                  
                  <div className="mt-6 pt-6 border-t border-gray-200">
                    <h4 className="font-semibold text-gray-900 mb-3">This course includes:</h4>
                    <ul className="space-y-2 text-sm text-gray-600">
                      <li className="flex items-center">
                        <Play className="w-4 h-4 mr-2" />
                        Interactive video lessons
                      </li>
                      <li className="flex items-center">
                        <BookOpen className="w-4 h-4 mr-2" />
                        Practice exercises
                      </li>
                      <li className="flex items-center">
                        <Users className="w-4 h-4 mr-2" />
                        Audio pronunciation guides
                      </li>
                      <li className="flex items-center">
                        <Award className="w-4 h-4 mr-2" />
                        Certificate of completion
                      </li>
                    </ul>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>

      {/* Course Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="grid lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Tabs defaultValue="content" className="w-full">
              <TabsList className="grid w-full grid-cols-4">
                <TabsTrigger value="content">Course Content</TabsTrigger>
                <TabsTrigger value="overview">Overview</TabsTrigger>
                <TabsTrigger value="instructor">Instructor</TabsTrigger>
                <TabsTrigger value="reviews">Reviews</TabsTrigger>
              </TabsList>
              
              <TabsContent value="content" className="space-y-6 mt-6">
                <div className="space-y-4">
                  {course.chapters.map((chapter) => (
                    <Card key={chapter.id}>
                      <CardHeader>
                        <div className="flex items-center justify-between">
                          <CardTitle className="text-lg">Chapter {chapter.id}: {chapter.title}</CardTitle>
                          {chapter.completed && (
                            <CheckCircle className="w-5 h-5 text-green-600" />
                          )}
                        </div>
                      </CardHeader>
                      <CardContent>
                        <div className="space-y-3">
                          {chapter.lessons.map((lesson) => (
                            <div key={lesson.id} className="flex items-center justify-between p-3 rounded-lg border border-gray-200">
                              <div className="flex items-center space-x-3">
                                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                                  lesson.completed ? 'bg-green-100' : lesson.current ? 'bg-orange-100' : 'bg-gray-100'
                                }`}>
                                  {lesson.completed ? (
                                    <CheckCircle className="w-4 h-4 text-green-600" />
                                  ) : lesson.current ? (
                                    <Play className="w-4 h-4 text-orange-600" />
                                  ) : (
                                    <Lock className="w-4 h-4 text-gray-400" />
                                  )}
                                </div>
                                <div>
                                  <h4 className="font-medium text-gray-900">{lesson.title}</h4>
                                  <div className="flex items-center text-sm text-gray-600">
                                    {getLessonIcon(lesson.type)}
                                    <span className="ml-1">{lesson.type} • {lesson.duration}</span>
                                  </div>
                                </div>
                              </div>
                              
                              {(lesson.completed || lesson.current) && (
                                <Button variant="ghost" size="sm" asChild>
                                  <Link to={`/lesson/${lesson.id}`}>
                                    {lesson.current ? 'Continue' : 'Review'}
                                  </Link>
                                </Button>
                              )}
                            </div>
                          ))}
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
              
              <TabsContent value="overview" className="mt-6">
                <div className="space-y-8">
                  <div>
                    <h3 className="text-xl font-bold mb-4">What you'll learn</h3>
                    <ul className="grid md:grid-cols-2 gap-3">
                      {course.whatYouLearn.map((item, index) => (
                        <li key={index} className="flex items-start">
                          <CheckCircle className="w-5 h-5 text-green-600 mr-3 mt-0.5 flex-shrink-0" />
                          <span className="text-gray-700">{item}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h3 className="text-xl font-bold mb-4">Skills you'll gain</h3>
                    <div className="flex flex-wrap gap-2">
                      {course.skills.map((skill, index) => (
                        <Badge key={index} variant="secondary">{skill}</Badge>
                      ))}
                    </div>
                  </div>
                </div>
              </TabsContent>
              
              <TabsContent value="instructor" className="mt-6">
                <Card>
                  <CardContent className="p-6">
                    <div className="flex items-start space-x-4">
                      <img 
                        src={course.instructor.image} 
                        alt={course.instructor.name}
                        className="w-20 h-20 rounded-full object-cover"
                      />
                      <div className="flex-1">
                        <h3 className="text-xl font-bold text-gray-900">{course.instructor.name}</h3>
                        <p className="text-orange-600 font-medium mb-3">{course.instructor.title}</p>
                        <p className="text-gray-600">{course.instructor.bio}</p>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              </TabsContent>
              
              <TabsContent value="reviews" className="mt-6">
                <div className="space-y-6">
                  <div className="flex items-center space-x-4 mb-6">
                    <div className="text-4xl font-bold text-gray-900">{course.rating}</div>
                    <div>
                      <div className="flex items-center mb-1">
                        {[...Array(5)].map((_, i) => (
                          <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                        ))}
                      </div>
                      <p className="text-sm text-gray-600">{course.reviews.length} reviews</p>
                    </div>
                  </div>
                  
                  {course.reviews && course.reviews.map((review) => (
                    <Card key={review.id}>
                      <CardContent className="p-6">
                        <div className="flex items-start justify-between mb-3">
                          <div>
                            <h4 className="font-semibold text-gray-900">{review.name}</h4>
                            <p className="text-sm text-gray-600">{review.date}</p>
                          </div>
                          <div className="flex items-center">
                            {[...Array(review.rating)].map((_, i) => (
                              <Star key={i} className="w-4 h-4 text-yellow-400 fill-current" />
                            ))}
                          </div>
                        </div>
                        <p className="text-gray-700">{review.comment}</p>
                      </CardContent>
                    </Card>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </div>
          
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-6 space-y-6">
              {/* Related Courses */}
              <Card>
                <CardHeader>
                  <CardTitle>Related Courses</CardTitle>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                    <div className="text-xl">🌿</div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">Ayurvedic Fundamentals</h4>
                      <p className="text-sm text-gray-600">Basic Level • 6 hours</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg">
                    <div className="text-xl">🕉</div>
                    <div className="flex-1">
                      <h4 className="font-medium text-gray-900">Advanced Sanskrit Grammar</h4>
                      <p className="text-sm text-gray-600">Advanced Level • 8 hours</p>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CourseDetail;