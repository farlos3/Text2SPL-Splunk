import { Bot } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex gap-3 justify-start">
      <div className="w-8 h-8 bg-blue-500 rounded-full flex items-center justify-center flex-shrink-0">
        <Bot className="w-5 h-5 text-white" />
      </div>
      <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg rounded-bl-none px-4 py-2">
        <div className="flex space-x-1">
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
          <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
        </div>
      </div>
    </div>
  );
}
