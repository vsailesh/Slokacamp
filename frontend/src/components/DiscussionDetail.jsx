import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import Navbar from './Navbar';
import Footer from './Footer';

const DiscussionDetail = () => {
  const { id } = useParams();
  const { user, token } = useAuth();
  const navigate = useNavigate();
  const [discussion, setDiscussion] = useState(null);
  const [loading, setLoading] = useState(true);
  const [replyContent, setReplyContent] = useState('');

  useEffect(() => {
    loadDiscussion();
  }, [id]);

  const loadDiscussion = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_BACKEND_URL}/api/discussions/${id}/`);
      const data = await response.json();
      setDiscussion(data);
    } catch (error) {
      console.error('Error loading discussion:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleReply = async (e) => {
    e.preventDefault();
    if (!token) {
      navigate('/signin');
      return;
    }

    try {
      const response = await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/discussions/${id}/replies/`,
        {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
          body: JSON.stringify({ content: replyContent }),
        }
      );

      if (response.ok) {
        setReplyContent('');
        loadDiscussion();
      }
    } catch (error) {
      console.error('Error posting reply:', error);
    }
  };

  const handleUpvote = async (replyId) => {
    if (!token) {
      navigate('/signin');
      return;
    }

    try {
      await fetch(
        `${process.env.REACT_APP_BACKEND_URL}/api/discussion-replies/${replyId}/upvote/`,
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );
      loadDiscussion();
    } catch (error) {
      console.error('Error upvoting reply:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
        </div>
        <Footer />
      </div>
    );
  }

  if (!discussion) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Navbar />
        <div className="max-w-4xl mx-auto px-4 py-12 text-center">
          <p className="text-gray-600">Discussion not found</p>
        </div>
        <Footer />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Back Button */}
        <button
          onClick={() => navigate('/discussions')}
          className="mb-6 text-blue-600 hover:text-blue-700 flex items-center gap-2"
        >
          ← Back to Discussions
        </button>

        {/* Discussion */}
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                {discussion.title}
              </h1>
              <div className="flex items-center gap-3 text-sm text-gray-500">
                <span>Asked by {discussion.user.full_name}</span>
                <span>•</span>
                <span>{new Date(discussion.created_at).toLocaleDateString()}</span>
                <span>•</span>
                <span>{discussion.views} views</span>
              </div>
            </div>
            {discussion.is_resolved && (
              <span className="px-3 py-1 bg-green-100 text-green-800 text-sm rounded-full">
                ✓ Resolved
              </span>
            )}
          </div>
          <p className="text-gray-700 whitespace-pre-wrap">{discussion.content}</p>
        </div>

        {/* Replies */}
        <div className="mb-6">
          <h2 className="text-xl font-bold text-gray-900 mb-4">
            {discussion.replies.length} {discussion.replies.length === 1 ? 'Reply' : 'Replies'}
          </h2>
          
          <div className="space-y-4">
            {discussion.replies.map((reply) => (
              <div key={reply.id} className="bg-white rounded-lg shadow p-6">
                <div className="flex gap-4">
                  <div className="flex flex-col items-center">
                    <button
                      onClick={() => handleUpvote(reply.id)}
                      className="text-gray-400 hover:text-blue-600 transition-colors"
                    >
                      ▲
                    </button>
                    <span className="text-lg font-semibold text-gray-700">
                      {reply.upvotes}
                    </span>
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold text-gray-900">
                        {reply.user.full_name}
                      </span>
                      {reply.is_accepted && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          ✓ Accepted Answer
                        </span>
                      )}
                      <span className="text-sm text-gray-500">
                        {new Date(reply.created_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-gray-700 whitespace-pre-wrap">{reply.content}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Reply Form */}
        {user ? (
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Your Answer</h3>
            <form onSubmit={handleReply}>
              <textarea
                value={replyContent}
                onChange={(e) => setReplyContent(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows="6"
                placeholder="Write your answer here..."
                required
              />
              <div className="mt-4 flex justify-end">
                <button
                  type="submit"
                  className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Post Answer
                </button>
              </div>
            </form>
          </div>
        ) : (
          <div className="bg-white rounded-lg shadow p-6 text-center">
            <p className="text-gray-600 mb-4">Sign in to post an answer</p>
            <button
              onClick={() => navigate('/signin')}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Sign In
            </button>
          </div>
        )}
      </div>

      <Footer />
    </div>
  );
};

export default DiscussionDetail;