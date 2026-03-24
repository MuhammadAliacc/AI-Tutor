/**
 * Chat Page
 */
import React, { useState, useEffect, useRef } from 'react';
import Navbar from '../components/Navbar';
import ChatMessage from '../components/ChatMessage';
import { useChatStore } from '../store';
import { queryService } from '../services/api';
import { Send, AlertCircle, Loader } from 'lucide-react';

export default function ChatPage() {
  const [question, setQuestion] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);
  const messages = useChatStore((state) => state.messages);
  const addMessage = useChatStore((state) => state.addMessage);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleAskQuestion = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setError('');
    
    // Add user message
    addMessage({
      role: 'user',
      content: question,
    });

    setQuestion('');
    setIsLoading(true);

    try {
      const response = await queryService.askQuestion(question);
      const data = response.data;

      // Add AI response
      addMessage({
        role: 'assistant',
        content: data.answer,
        sources: data.source_documents?.map((doc) => doc.name) || [],
        confidence: data.confidence_score,
      });
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to get response. Please try again.');
      addMessage({
        role: 'assistant',
        content: `Sorry, I encountered an error: ${err.response?.data?.detail || 'Unknown error'}`,
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      <Navbar />

      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        <div className="max-w-4xl mx-auto">
          {messages.length === 0 ? (
            <div className="text-center py-20">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-6">
                <span className="text-4xl">🎓</span>
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">Welcome to AI Tutor</h2>
              <p className="text-gray-600">
                Ask any questions about the uploaded learning materials.
                The AI will provide accurate, document-grounded answers.
              </p>
            </div>
          ) : (
            messages.map((msg, idx) => <ChatMessage key={idx} message={msg} />)
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {error && (
        <div className="max-w-4xl mx-auto w-full px-4 mb-4">
          <div className="p-4 bg-red-100 border border-red-400 rounded-lg flex items-start space-x-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        </div>
      )}

      {/* Input Form */}
      <div className="border-t border-gray-200 bg-white p-4">
        <form onSubmit={handleAskQuestion} className="max-w-4xl mx-auto">
          <div className="flex items-end space-x-3">
            <div className="flex-1">
              <textarea
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' && e.ctrlKey) {
                    handleAskQuestion(e);
                  }
                }}
                placeholder="Ask me anything about the learning materials..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-600 focus:border-transparent resize-none"
                rows="3"
                disabled={isLoading}
              />
              <p className="text-xs text-gray-500 mt-1">
                Ctrl+Enter to send
              </p>
            </div>
            <button
              type="submit"
              disabled={isLoading || !question.trim()}
              className="flex-shrink-0 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-semibold transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center space-x-2"
            >
              {isLoading ? (
                <>
                  <Loader size={20} className="animate-spin" />
                  <span className="hidden sm:inline">Thinking...</span>
                </>
              ) : (
                <>
                  <Send size={20} />
                  <span className="hidden sm:inline">Send</span>
                </>
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
