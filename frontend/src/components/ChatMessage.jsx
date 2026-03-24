/**
 * Chat Message Component
 */
import React from 'react';
import ReactMarkdown from 'react-markdown';
import { FileText } from 'lucide-react';

export default function ChatMessage({ message }) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4 message-enter`}>
      <div
        className={`max-w-xs lg:max-w-md xl:max-w-lg rounded-lg px-4 py-3 ${
          isUser
            ? 'bg-blue-600 text-white'
            : 'bg-gray-200 text-gray-800'
        }`}
      >
        {isUser ? (
          <p className="text-sm">{message.content}</p>
        ) : (
          <>
            <div className="prose prose-sm max-w-none text-sm">
              <ReactMarkdown>{message.content}</ReactMarkdown>
            </div>
            {message.sources && message.sources.length > 0 && (
              <div className="mt-3 pt-3 border-t border-gray-300 text-xs">
                <p className="font-semibold mb-2">📚 Sources:</p>
                <ul className="space-y-1">
                  {message.sources.map((source, idx) => (
                    <li key={idx} className="flex items-center space-x-2">
                      <FileText size={14} />
                      <span>{source}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
