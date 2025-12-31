import React, { useState, useRef, useEffect } from 'react';
import { X, Send, Bot, Minimize2, Maximize2, Loader2 } from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';

const AITutorWidget = ({ context = {}, onClose }) => {
  const { user, token } = useAuth();
  const [isOpen, setIsOpen] = useState(true);
  const [isMinimized, setIsMinimized] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content: 'Namaste! 🙏 I am your AI Tutor for SlokaCamp. I can help you with:\n\n• Explaining Sanskrit slokas and their meanings\n• Teaching Ayurvedic concepts and practices\n• Answering questions about courses and lessons\n• Generating practice quizzes\n• Translation of Sanskrit texts\n\nHow can I assist you today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId, setSessionId] = useState(null);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || '';

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (!isMinimized && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isMinimized]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage = {
      role: 'user',
      content: input.trim(),
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${backendUrl}/api/ai/chat/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          message: userMessage.content,
          session_id: sessionId,
          context_type: context.type || 'general',
          context_data: context.data || {},
          use_rag: true
        })
      });

      const data = await response.json();

      if (data.success) {
        // Save session ID for conversation continuity
        if (data.session_id && !sessionId) {
          setSessionId(data.session_id);
        }

        const assistantMessage = {
          role: 'assistant',
          content: data.response,
          timestamp: new Date(),
          toolCalls: data.tool_calls || []
        };

        setMessages(prev => [...prev, assistantMessage]);
      } else {
        // Error handling
        setMessages(prev => [...prev, {
          role: 'assistant',
          content: data.response || 'I apologize, but I encountered an error. Please try again.',
          timestamp: new Date(),
          isError: true
        }]);
      }
    } catch (error) {
      console.error('AI chat error:', error);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I apologize, but I am having trouble connecting right now. Please try again in a moment.',
        timestamp: new Date(),
        isError: true
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple formatting for line breaks
    return content.split('\n').map((line, i) => (
      <React.Fragment key={i}>
        {line}
        {i < content.split('\n').length - 1 && <br />}
      </React.Fragment>
    ));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {isMinimized ? (
        // Minimized view - just the bot icon
        <button
          onClick={() => setIsMinimized(false)}
          className="bg-gradient-to-r from-orange-500 to-pink-600 text-white rounded-full p-4 shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 transform hover:scale-110"
        >
          <Bot size={28} />
          {messages.length > 1 && (
            <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center animate-pulse">
              {messages.length - 1}
            </span>
          )}
        </button>
      ) : (
        // Full chat widget
        <div className="bg-white rounded-2xl shadow-2xl border border-gray-200 flex flex-col" style={{ width: '400px', height: '600px' }}>
          {/* Header */}
          <div className="bg-gradient-to-r from-orange-500 to-pink-600 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-white/20 rounded-full p-2">
                <Bot size={24} />
              </div>
              <div>
                <h3 className="font-bold text-lg">AI Tutor</h3>
                <p className="text-xs text-white/80">Always here to help</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={() => setIsMinimized(true)}
                className="hover:bg-white/20 p-2 rounded-lg transition-colors"
              >
                <Minimize2 size={18} />
              </button>
              {onClose && (
                <button
                  onClick={onClose}
                  className="hover:bg-white/20 p-2 rounded-lg transition-colors"
                >
                  <X size={18} />
                </button>
              )}
            </div>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gradient-to-b from-orange-50/30 to-white">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                    message.role === 'user'
                      ? 'bg-gradient-to-r from-orange-500 to-pink-600 text-white'
                      : message.isError
                      ? 'bg-red-50 border border-red-200 text-red-700'
                      : 'bg-white border border-gray-200 text-gray-800'
                  }`}
                >
                  <div className="text-sm whitespace-pre-wrap">
                    {formatMessage(message.content)}
                  </div>
                  {message.toolCalls && message.toolCalls.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-gray-300 text-xs text-gray-500">
                      🔧 Used tools: {message.toolCalls.map(t => t.name).join(', ')}
                    </div>
                  )}
                  <div className="text-xs mt-1 opacity-60">
                    {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </div>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-white border border-gray-200 rounded-2xl px-4 py-3">
                  <Loader2 className="animate-spin text-orange-500" size={20} />
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200 bg-white rounded-b-2xl">
            <div className="flex items-center space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything about Sanskrit, Ayurveda..."
                className="flex-1 px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                disabled={isLoading}
              />
              <button
                onClick={sendMessage}
                disabled={isLoading || !input.trim()}
                className="bg-gradient-to-r from-orange-500 to-pink-600 text-white rounded-xl px-4 py-3 hover:shadow-lg disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-105"
              >
                <Send size={20} />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AITutorWidget;
