import { Send, Lightbulb } from 'lucide-react';
import { useState } from 'react';

interface ChatInputProps {
  inputText: string;
  setInputText: (text: string) => void;
  onSendMessage: () => void;
  onGenerateSPL?: () => void; // New prop for SPL generation
  onCheckRelevance?: () => void; // New prop for relevance check
  isTyping: boolean;
}

export default function ChatInput({ inputText, setInputText, onSendMessage, onGenerateSPL, onCheckRelevance, isTyping }: ChatInputProps) {
  const [showExamples, setShowExamples] = useState(false);

  const exampleQueries = [
    "Show all failed logins for HealthPlus within the last 24 hours",
    "Identify unusual service account activity on AirLogix production servers",
    "Find top 10 source IPs with failed login attempts for TechNova",
    "Show brute force attempts with more than 5 failed logins in 15 minutes",
    "Analyze changes to critical system files in the last 48 hours"
  ];

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      onSendMessage();
    }
  };

  const handleExampleClick = (example: string) => {
    setInputText(example);
    setShowExamples(false);
  };

  return (
    <div className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700">
      {/* Example queries */}
      {showExamples && (
        <div className="border-b border-gray-200 dark:border-gray-700 p-4 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20">
          <div className="max-w-4xl mx-auto">
            <h3 className="text-sm font-semibold text-blue-800 dark:text-blue-200 mb-3 flex items-center gap-2">
              <span>💡</span>
              Example Security Queries:
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              {exampleQueries.map((example, index) => {
                const categories = [
                  { color: 'border-l-green-400 bg-green-50 dark:bg-green-900/20', icon: '🔐' },
                  { color: 'border-l-yellow-400 bg-yellow-50 dark:bg-yellow-900/20', icon: '⚠️' },
                  { color: 'border-l-purple-400 bg-purple-50 dark:bg-purple-900/20', icon: '🔍' },
                  { color: 'border-l-red-400 bg-red-50 dark:bg-red-900/20', icon: '🛡️' },
                  { color: 'border-l-blue-400 bg-blue-50 dark:bg-blue-900/20', icon: '📊' }
                ];
                const category = categories[index % categories.length];
                
                return (
                  <button
                    key={index}
                    onClick={() => handleExampleClick(example)}
                    className={`text-left p-3 text-xs border-l-4 ${category.color} hover:shadow-md dark:hover:bg-gray-700/50 rounded-r-lg border border-l-0 border-gray-200 dark:border-gray-600 transition-all duration-200 hover:scale-[1.02]`}
                  >
                    <div className="flex items-start gap-2">
                      <span className="text-sm">{category.icon}</span>
                      <div className="text-gray-700 dark:text-gray-200">{example}</div>
                    </div>
                  </button>
                );
              })}
            </div>
            <div className="mt-3 text-xs text-blue-600 dark:text-blue-300 bg-white/50 dark:bg-gray-700/50 p-2 rounded">
              <strong>💡 Tip:</strong> Include company name (AirLogix, TechNova, SafeBank, etc.), time range, and specific security event for best results
            </div>
          </div>
        </div>
      )}

      <div className="p-4">
        <div className="max-w-4xl mx-auto">
          {/* Help text */}
          <div className="flex items-center justify-between mb-3">
            <button
              onClick={() => setShowExamples(!showExamples)}
              className="flex items-center gap-1.5 text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 px-2 py-1 rounded-md hover:bg-blue-50 dark:hover:bg-blue-900/20 transition-colors"
            >
              <Lightbulb className="w-4 h-4" />
              {showExamples ? 'Hide' : 'Show'} Examples
            </button>
            <div className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
              <span className="hidden md:inline">🔒 Security Analysis</span>
              <span className="mx-1">•</span>
              <span>📊 Log Monitoring</span>
              <span className="mx-1">•</span>
              <span>🏢 Multi-Company Support</span>
            </div>
          </div>

          <div className="flex gap-2">
            <div className="flex-1 relative">
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="🔍 Describe your security investigation... (e.g., 'Identify unusual service account activity on AirLogix production servers')"
                className="w-full px-4 py-3 pr-12 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 shadow-sm"
                rows={1}
                style={{ minHeight: '52px', maxHeight: '140px' }}
              />
            </div>
            
            {/* Relevance Check Button */}
            {onCheckRelevance && (
              <button
                onClick={onCheckRelevance}
                disabled={!inputText.trim() || isTyping}
                className="px-3 py-3 bg-yellow-500 text-white rounded-lg hover:bg-yellow-600 focus:outline-none focus:ring-2 focus:ring-yellow-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Check if query is Splunk-related"
              >
                🔍
              </button>
            )}
            
            {/* SPL Generation Button */}
            {onGenerateSPL && (
              <button
                onClick={onGenerateSPL}
                disabled={!inputText.trim() || isTyping}
                className="px-3 py-3 bg-green-500 text-white rounded-lg hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                title="Generate SPL Query"
              >
                📊
              </button>
            )}
            
            {/* General Chat Button */}
            <button
              onClick={onSendMessage}
              disabled={!inputText.trim() || isTyping}
              className="px-4 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              title="General Chat"
            >
              <Send className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
