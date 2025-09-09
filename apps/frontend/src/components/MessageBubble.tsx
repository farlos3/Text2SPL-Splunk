import { Bot, User, Copy, CheckCircle, Database, Building2, FileText, TrendingUp, Search, Code, Sparkles } from 'lucide-react';
import { Message } from '@/types/chat';
import { useState } from 'react';

interface MessageBubbleProps {
  message: Message;
}

export default function MessageBubble({ message }: MessageBubbleProps) {
  const [copied, setCopied] = useState(false);

  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error('Failed to copy text: ', err);
    }
  };

  const formatMessage = (text: string) => {
    // Show only the SPL block (clean, minimal)
    if (text.includes('**SPL Query Generated**')) {
      const parts = text.split('```spl');
      if (parts.length > 1) {
        const afterCodeSplit = parts[1].split('```');
        let splCode = afterCodeSplit[0];
        // Normalize escaped line breaks and tabs (e.g., "\n" -> newline)
        const normalizedSpl = splCode
          .replace(/\\n/g, '\n')
          .replace(/\\t/g, '\t')
          .replace(/\r/g, '');
        // For better readability, break lines at each pipe operator
        // Example: index=a | stats count BY host ->
        // index=a\n| stats count BY host
        const displayedSpl = normalizedSpl.replace(/\s*\|\s*/g, ' \n| ');
        return (
          <div className="relative bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl overflow-hidden border border-slate-700/50 shadow-2xl animate-fade-in">
            <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-green-500/10"></div>
            <div className="relative">
              <div className="flex items-center justify-between px-6 py-3 bg-slate-800/50 border-b border-slate-700/50">
                <div className="flex items-center gap-3">
                  <div className="w-6 h-6 bg-gradient-to-r from-green-500 to-emerald-500 rounded-lg flex items-center justify-center">
                    <Code className="w-4 h-4 text-white" />
                  </div>
                  <span className="text-sm font-medium text-slate-300">SPL Query</span>
                </div>
                <button
                  onClick={() => handleCopy(normalizedSpl.trim())}
                  className="flex items-center gap-2 px-3 py-1.5 text-xs bg-slate-700/50 hover:bg-slate-600/50 text-slate-300 hover:text-white rounded-lg transition-all-smooth btn-hover"
                >
                  {copied ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
                  {copied ? 'Copied!' : 'Copy'}
                </button>
              </div>
              <div className="relative">
                <div className="p-6 max-h-60 md:max-h-80 lg:max-h-96 overflow-y-auto overflow-x-hidden code-scroll">
                  <pre className="text-sm md:text-base font-mono leading-relaxed">
                    <code className="text-green-400 block whitespace-pre-wrap break-words">{displayedSpl.trim()}</code>
                  </pre>
                </div>
                {/* Show scroll hint if content might be long */}
                {normalizedSpl.length > 300 && (
                  <div className="px-6 pb-3">
                    <div className="text-xs text-slate-400 text-center">
                      ⬆ Scroll to view full query
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        );
      }
    }

    // Regular message formatting
    return <p className="text-sm leading-relaxed whitespace-pre-wrap">{text}</p>;
  };

  return (
    <div
      className={`flex gap-4 ${message.sender === 'user' ? 'justify-end' : 'justify-start'} animate-fade-in`}
    >
      {message.sender === 'assistant' && (
        <div className="w-10 h-10 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg animate-pulse-soft">
          <Sparkles className="w-6 h-6 text-white" />
        </div>
      )}
      
      <div
        className={`${
          message.sender === 'user' 
            ? 'max-w-xs md:max-w-md lg:max-w-2xl' 
            : 'max-w-full md:max-w-4xl lg:max-w-5xl'
        } px-6 py-4 ${
          message.sender === 'user'
            ? 'bg-gradient-to-r from-blue-500 to-indigo-600 text-white rounded-2xl rounded-br-lg shadow-lg'
            : 'bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm text-gray-900 dark:text-white border border-gray-200/50 dark:border-gray-700/50 rounded-2xl rounded-bl-lg shadow-xl hover:shadow-2xl transition-all-smooth'
        }`}
      >
        {formatMessage(message.content)}
        <div className={`flex justify-between items-center mt-4 pt-3 border-t ${
          message.sender === 'user' 
            ? 'border-blue-300/30' 
            : 'border-gray-200/50 dark:border-gray-700/50'
        }`}>
          <div className="flex items-center gap-2">
            <p className={`text-xs font-medium ${
              message.sender === 'user' ? 'text-blue-100' : 'text-gray-500 dark:text-gray-400'
            }`}>
              {message.timestamp.toLocaleTimeString('th-TH', { 
                hour: '2-digit', 
                minute: '2-digit',
                timeZone: 'Asia/Bangkok'
              })}
            </p>
            {message.sender === 'assistant' && (
              <div className="flex items-center gap-1">
                <div className="w-1 h-1 bg-green-500 rounded-full"></div>
                <span className="text-xs text-green-600 dark:text-green-400 font-medium">AI</span>
              </div>
            )}
          </div>
          {message.sender === 'assistant' && !message.content.includes('**SPL Query Generated**') && (
            <button
              onClick={() => handleCopy(message.content)}
              className="flex items-center gap-1 px-2 py-1 text-xs bg-gray-100/50 dark:bg-gray-700/50 hover:bg-gray-200/50 dark:hover:bg-gray-600/50 text-gray-600 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300 rounded-md transition-all-smooth"
            >
              {copied ? <CheckCircle className="w-3 h-3" /> : <Copy className="w-3 h-3" />}
              {copied ? 'Copied' : 'Copy'}
            </button>
          )}
        </div>
      </div>

      {message.sender === 'user' && (
        <div className="w-10 h-10 bg-gradient-to-r from-gray-600 to-gray-700 rounded-xl flex items-center justify-center flex-shrink-0 shadow-lg">
          <User className="w-6 h-6 text-white" />
        </div>
      )}
    </div>
  );
}
