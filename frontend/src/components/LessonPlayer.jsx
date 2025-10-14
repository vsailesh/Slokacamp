import React, { useState } from 'react';
import { Button } from './ui/button';
import { Card, CardContent } from './ui/card';
import { Progress } from './ui/progress';
import { Badge } from './ui/badge';
import { ChevronLeft, ChevronRight, Play, Pause, RotateCcw, BookOpen, Headphones, CheckCircle, Volume2 } from 'lucide-react';
import { Link, useParams } from 'react-router-dom';

const LessonPlayer = () => {
  const { lessonId } = useParams();
  const [isPlaying, setIsPlaying] = useState(false);
  const [showTranscript, setShowTranscript] = useState(true);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration] = useState(720); // 12 minutes in seconds
  
  // Mock lesson data
  const lesson = {
    id: 6,
    title: "Pronunciation Practice",
    course: "Introduction to Sanskrit Slokas",
    courseId: 1,
    chapterTitle: "Sanskrit Alphabet & Sounds",
    type: "audio",
    duration: "12 min",
    description: "Master the correct pronunciation of Sanskrit vowels and consonants with guided practice sessions.",
    content: {
      audioUrl: "/audio/sanskrit-pronunciation.mp3",
      transcript: [
        {
          time: 0,
          text: "Welcome to Sanskrit pronunciation practice. In this lesson, we'll focus on mastering the correct pronunciation of Sanskrit sounds.",
          sanskrit: ""
        },
        {
          time: 30,
          text: "Let's start with vowels. The first vowel is 'अ' (a), pronounced like 'u' in 'but'.",
          sanskrit: "अ"
        },
        {
          time: 60,
          text: "Next is 'आ' (ā), pronounced like 'a' in 'father'. Notice the longer sound.",
          sanskrit: "आ"
        },
        {
          time: 90,
          text: "The vowel 'इ' (i) is pronounced like 'i' in 'bit'.",
          sanskrit: "इ"
        },
        {
          time: 120,
          text: "And 'ई' (ī) is the longer version, like 'ee' in 'see'.",
          sanskrit: "ई"
        },
        {
          time: 180,
          text: "Now let's practice 'उ' (u), pronounced like 'u' in 'put'.",
          sanskrit: "उ"
        },
        {
          time: 210,
          text: "The longer version 'ऊ' (ū) is like 'oo' in 'moon'.",
          sanskrit: "ऊ"
        },
        {
          time: 270,
          text: "Let's practice a simple word: 'गुरु' (guru) - teacher or guide.",
          sanskrit: "गुरु"
        },
        {
          time: 330,
          text: "Another word: 'शान्ति' (śānti) - peace. Notice the correct pronunciation.",
          sanskrit: "शान्ति"
        },
        {
          time: 420,
          text: "Now let's practice the sacred syllable 'ॐ' (Om). Take a deep breath and chant slowly.",
          sanskrit: "ॐ"
        },
        {
          time: 480,
          text: "Remember, consistency in practice is key. Repeat these sounds daily for best results.",
          sanskrit: ""
        }
      ],
      practiceWords: [
        { word: "अ", transliteration: "a", meaning: "vowel sound", audio: "/audio/a.mp3" },
        { word: "आ", transliteration: "ā", meaning: "long vowel", audio: "/audio/aa.mp3" },
        { word: "गुरु", transliteration: "guru", meaning: "teacher", audio: "/audio/guru.mp3" },
        { word: "शान्ति", transliteration: "śānti", meaning: "peace", audio: "/audio/shanti.mp3" },
        { word: "ॐ", transliteration: "Om", meaning: "sacred sound", audio: "/audio/om.mp3" }
      ]
    },
    navigation: {
      previousLesson: { id: 5, title: "Consonants (व्यंजन)" },
      nextLesson: { id: 7, title: "Gayatri Mantra" }
    },
    progress: 45
  };

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const getCurrentTranscript = () => {
    return lesson.content.transcript.find((item, index) => {
      const nextItem = lesson.content.transcript[index + 1];
      return currentTime >= item.time && (!nextItem || currentTime < nextItem.time);
    });
  };

  const playPause = () => {
    setIsPlaying(!isPlaying);
    // Simulate audio playback
    if (!isPlaying) {
      const interval = setInterval(() => {
        setCurrentTime(prev => {
          if (prev >= duration) {
            clearInterval(interval);
            setIsPlaying(false);
            return duration;
          }
          return prev + 1;
        });
      }, 1000);
    }
  };

  const resetAudio = () => {
    setCurrentTime(0);
    setIsPlaying(false);
  };

  const currentTranscript = getCurrentTranscript();

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Button variant="ghost" size="sm" asChild>
                <Link to={`/course/${lesson.courseId}`}>
                  <ChevronLeft className="w-4 h-4 mr-1" />
                  Back to Course
                </Link>
              </Button>
              <div className="h-6 w-px bg-gray-300"></div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">{lesson.title}</h1>
                <p className="text-sm text-gray-600">{lesson.course} • {lesson.chapterTitle}</p>
              </div>
            </div>
            
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-600">
                Progress: {lesson.progress}%
              </div>
              <Progress value={lesson.progress} className="w-24" />
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2 space-y-6">
            {/* Audio Player */}
            <Card>
              <CardContent className="p-8">
                <div className="text-center space-y-6">
                  <div className="w-24 h-24 bg-gradient-to-br from-orange-500 to-red-500 rounded-full flex items-center justify-center mx-auto">
                    <Headphones className="w-12 h-12 text-white" />
                  </div>
                  
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 mb-2">{lesson.title}</h2>
                    <p className="text-gray-600">{lesson.description}</p>
                  </div>
                  
                  {/* Audio Controls */}
                  <div className="space-y-4">
                    <div className="flex items-center justify-center space-x-4">
                      <Button variant="outline" size="sm" onClick={resetAudio}>
                        <RotateCcw className="w-4 h-4" />
                      </Button>
                      
                      <Button size="lg" onClick={playPause} className="w-16 h-16 rounded-full">
                        {isPlaying ? <Pause className="w-6 h-6" /> : <Play className="w-6 h-6" />}
                      </Button>
                      
                      <Button variant="outline" size="sm">
                        <Volume2 className="w-4 h-4" />
                      </Button>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="space-y-2">
                      <Progress value={(currentTime / duration) * 100} className="w-full" />
                      <div className="flex justify-between text-sm text-gray-600">
                        <span>{formatTime(currentTime)}</span>
                        <span>{formatTime(duration)}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>

            {/* Current Transcript */}
            {currentTranscript && (
              <Card>
                <CardContent className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">Current Audio</h3>
                    <Badge variant="outline">{formatTime(currentTranscript.time)}</Badge>
                  </div>
                  
                  {currentTranscript.sanskrit && (
                    <div className="text-center mb-4 p-4 bg-orange-50 rounded-lg">
                      <div className="text-3xl font-sanskrit text-gray-800 mb-2">
                        {currentTranscript.sanskrit}
                      </div>
                    </div>
                  )}
                  
                  <p className="text-gray-700 text-lg leading-relaxed">{currentTranscript.text}</p>
                </CardContent>
              </Card>
            )}

            {/* Practice Words */}
            <Card>
              <CardContent className="p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Practice Words</h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {lesson.content.practiceWords.map((word, index) => (
                    <div key={index} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50">
                      <div className="flex items-center space-x-3">
                        <div className="text-2xl font-sanskrit">{word.word}</div>
                        <div>
                          <div className="font-medium text-gray-900">{word.transliteration}</div>
                          <div className="text-sm text-gray-600">{word.meaning}</div>
                        </div>
                      </div>
                      <Button variant="ghost" size="sm">
                        <Play className="w-4 h-4" />
                      </Button>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Sidebar */}
          <div className="lg:col-span-1 space-y-6">
            {/* Transcript Toggle */}
            <Card>
              <CardContent className="p-4">
                <Button 
                  variant="outline" 
                  className="w-full" 
                  onClick={() => setShowTranscript(!showTranscript)}
                >
                  <BookOpen className="w-4 h-4 mr-2" />
                  {showTranscript ? 'Hide' : 'Show'} Full Transcript
                </Button>
              </CardContent>
            </Card>

            {/* Full Transcript */}
            {showTranscript && (
              <Card>
                <CardContent className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-4">Full Transcript</h3>
                  <div className="space-y-3 max-h-96 overflow-y-auto">
                    {lesson.content.transcript.map((item, index) => (
                      <div 
                        key={index} 
                        className={`p-3 rounded-lg cursor-pointer transition-colors ${
                          currentTranscript?.time === item.time 
                            ? 'bg-orange-100 border border-orange-200' 
                            : 'bg-gray-50 hover:bg-gray-100'
                        }`}
                        onClick={() => setCurrentTime(item.time)}
                      >
                        <div className="flex items-start justify-between mb-2">
                          <Badge variant="outline" className="text-xs">
                            {formatTime(item.time)}
                          </Badge>
                        </div>
                        
                        {item.sanskrit && (
                          <div className="text-lg font-sanskrit text-center mb-2 text-gray-800">
                            {item.sanskrit}
                          </div>
                        )}
                        
                        <p className="text-sm text-gray-700">{item.text}</p>
                      </div>
                    ))}
                  </div>
                </CardContent>
              </Card>
            )}

            {/* Navigation */}
            <Card>
              <CardContent className="p-4">
                <h3 className="font-semibold text-gray-900 mb-4">Navigation</h3>
                <div className="space-y-3">
                  {lesson.navigation.previousLesson && (
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link to={`/lesson/${lesson.navigation.previousLesson.id}`}>
                        <ChevronLeft className="w-4 h-4 mr-2" />
                        {lesson.navigation.previousLesson.title}
                      </Link>
                    </Button>
                  )}
                  
                  <Button className="w-full bg-orange-600 hover:bg-orange-700">
                    <CheckCircle className="w-4 h-4 mr-2" />
                    Mark Complete
                  </Button>
                  
                  {lesson.navigation.nextLesson && (
                    <Button variant="outline" className="w-full justify-start" asChild>
                      <Link to={`/lesson/${lesson.navigation.nextLesson.id}`}>
                        {lesson.navigation.nextLesson.title}
                        <ChevronRight className="w-4 h-4 ml-2" />
                      </Link>
                    </Button>
                  )}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LessonPlayer;