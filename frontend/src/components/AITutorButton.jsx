import React, { useState } from 'react';
import { Bot } from 'lucide-react';
import AITutorWidget from './AITutorWidget';
import { useAuth } from '../contexts/AuthContext';

const AITutorButton = ({ context = {} }) => {
  const [isOpen, setIsOpen] = useState(false);
  const { user } = useAuth();

  // Only show for authenticated users
  if (!user) return null;

  return (
    <>
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 z-50 bg-gradient-to-r from-orange-500 to-pink-600 text-white rounded-full p-4 shadow-2xl hover:shadow-orange-500/50 transition-all duration-300 transform hover:scale-110 group"
          title="Chat with AI Tutor"
        >
          <Bot size={28} className="group-hover:rotate-12 transition-transform" />
          <span className="absolute -top-2 -right-2 bg-green-500 w-4 h-4 rounded-full border-2 border-white animate-pulse"></span>
        </button>
      )}
      {isOpen && (
        <AITutorWidget
          context={context}
          onClose={() => setIsOpen(false)}
        />
      )}
    </>
  );
};

export default AITutorButton;
