'use client';

import { useState, useRef, useEffect } from 'react';
import { Send, MessageSquare, Settings, User, Sparkles, Menu, X, Moon, Sun } from 'lucide-react';
import { Message } from '@/types/chat';
import MessageBubble from '@/components/MessageBubble';
import { apiService } from '@/services/api';

export default function ChatBot() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isDarkMode, setIsDarkMode] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Dark mode detection and management
  useEffect(() => {
    // Check localStorage first
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setIsDarkMode(savedTheme === 'dark');
      document.documentElement.classList.toggle('dark', savedTheme === 'dark');
    } else {
      // Check system preference
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDarkMode(prefersDark);
      document.documentElement.classList.toggle('dark', prefersDark);
    }
  }, []);

  const toggleDarkMode = () => {
    const newDarkMode = !isDarkMode;
    setIsDarkMode(newDarkMode);
    document.documentElement.classList.toggle('dark', newDarkMode);
    localStorage.setItem('theme', newDarkMode ? 'dark' : 'light');
  };

  const handleSendMessage = async () => {
    console.log('handleSendMessage called');
    console.log('inputText:', inputText);
    console.log('inputText.trim():', inputText.trim());
    console.log('isTyping:', isTyping);
    
    if (!inputText.trim()) {
      console.log('No input text, returning');
      return;
    }

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputText,  // เปลี่ยนจาก text เป็น content
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    const currentInputText = inputText;
    setInputText('');
    setIsTyping(true);
    setError(null);

    try {
      console.log('Calling API with message:', currentInputText);
      
      // เรียก API จริง
      const response = await apiService.sendMessage(currentInputText);
      console.log('API response:', response);
      
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: response.content,
        sender: 'assistant',  // เปลี่ยนจาก bot เป็น assistant
        timestamp: new Date()
      };
      
      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      setError(error instanceof Error ? error.message : 'Failed to send message');
      
      // เพิ่มข้อความ error
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        content: 'Sorry, there was an error connecting to the server. Please try again.',
        sender: 'assistant',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setSidebarOpen(false);
  };

  // SPL Generation function
  const handleGenerateSPL = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      content: inputText,
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setError(null);

    try {
      const result = await apiService.generateSPL(inputText, false);
      
      let response = '';
      if (result.success && result.spl_query) {
        response = `🔍 **SPL Query Generated**
        
**Company Context:** ${result.company || 'N/A'}
**Index:** ${result.index || 'N/A'}
**Confidence:** ${result.confidence ? (result.confidence * 100).toFixed(0) + '%' : 'N/A'}

**Generated SPL:**
\`\`\`spl
${result.spl_query}
\`\`\`

**Detection Method:** ${result.detection_method || 'N/A'}
**Syntax Valid:** ${result.syntax_valid ? '✅' : '❌'}

${result.improved_query && result.improved_query !== inputText ? `**Improved Query:** ${result.improved_query}` : ''}
${result.issues && result.issues.length > 0 ? `**Issues:** ${result.issues.join(', ')}` : ''}`;
      } else {
        response = `❌ **SPL Generation Failed**

Error: ${result.error || 'Unknown error'}

Please try rephrasing your query or use general chat for assistance.`;
      }

      const assistantMessage: Message = {
        id: Date.now().toString() + '-assistant',
        content: response,
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('SPL generation error:', error);
      setError(error instanceof Error ? error.message : 'Failed to generate SPL query');
    } finally {
      setIsTyping(false);
    }
  };

  // Relevance checking function
  const handleCheckRelevance = async () => {
    if (!inputText.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString() + '-relevance',
      content: inputText + ' [Relevance Check]',
      sender: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputText('');
    setIsTyping(true);
    setError(null);

    try {
      const result = await apiService.checkSplunkRelevance(inputText);
      
      const response = `🔍 **Splunk Relevance Check**

**Query:** "${inputText}"
**Is Splunk-related:** ${result.is_splunk_related ? '✅ Yes' : '❌ No'}
**Confidence:** ${(result.confidence * 100).toFixed(1)}%
**Detection Method:** ${result.detection_method}

${result.is_splunk_related 
  ? '✅ This query can be converted to SPL. Try the SPL Generation button!' 
  : '❌ This query doesn\'t appear to be related to Splunk. Try general chat instead.'}`;

      const assistantMessage: Message = {
        id: Date.now().toString() + '-relevance-response',
        content: response,
        sender: 'assistant',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Relevance check error:', error);
      setError(error instanceof Error ? error.message : 'Failed to check relevance');
    } finally {
      setIsTyping(false);
    }
  };

  const suggestedPrompts = [
    "Help me create an SPL query to find failed login attempts",
    "Explain how to use the stats command in Splunk", 
    "How to filter events by source type",
    "Guide me through analyzing network traffic logs"
  ];

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-50 to-blue-50 dark:from-slate-950 dark:to-blue-950 transition-all-smooth">
      {/* Mobile Menu Button */}
      <div className="md:hidden fixed top-4 left-4 z-50 flex gap-2">
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-3 bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 rounded-xl shadow-lg backdrop-blur-sm hover:shadow-xl transition-all-smooth btn-hover"
        >
          {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
        </button>
        
        {/* Mobile Dark Mode Toggle */}
        <button
          onClick={toggleDarkMode}
          className="p-3 bg-white/80 dark:bg-gray-800/80 border border-gray-200/50 dark:border-gray-700/50 rounded-xl shadow-lg backdrop-blur-sm hover:shadow-xl transition-all-smooth btn-hover"
          title={isDarkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
        >
          {isDarkMode ? (
            <Sun className="w-5 h-5 text-yellow-500" />
          ) : (
            <Moon className="w-5 h-5 text-blue-600" />
          )}
        </button>
      </div>

      {/* Sidebar */}
      <div className={`
        w-72 bg-white/70 dark:bg-gray-900/70 backdrop-blur-md border-r border-gray-200/50 dark:border-gray-800/50 flex flex-col shadow-xl
        md:relative md:translate-x-0
        ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'}
        fixed md:static top-0 left-0 h-full z-40 transition-all duration-500 ease-in-out
      `}>
        {/* New Chat Button */}
        <div className="p-6">
          <button 
            onClick={clearConversation}
            className="w-full flex items-center gap-3 px-6 py-4 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gradient-to-r from-blue-50 to-indigo-50 dark:from-blue-900/20 dark:to-indigo-900/20 hover:from-blue-100 hover:to-indigo-100 dark:hover:from-blue-900/30 dark:hover:to-indigo-900/30 rounded-xl border border-blue-200/50 dark:border-blue-700/50 transition-all-smooth btn-hover shadow-sm"
          >
            <div className="w-5 h-5 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-md flex items-center justify-center">
              <MessageSquare className="w-3 h-3 text-white" />
            </div>
            New Chat
          </button>
        </div>

        {/* Chat History (placeholder) */}
        <div className="flex-1 px-6">
          <div className="text-xs font-semibold text-gray-500 dark:text-gray-400 mb-4 tracking-wider uppercase">Recent Chats</div>
          
        </div>

        {/* Bottom Actions */}
        <div className="p-6 border-t border-gray-200/50 dark:border-gray-800/50 space-y-2">
          {/* Dark Mode Toggle */}
          <button
            onClick={toggleDarkMode}
            className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg transition-all-smooth btn-hover"
          >
            <div className="w-5 h-5 bg-gradient-to-r from-yellow-400 to-orange-500 dark:from-blue-400 dark:to-purple-500 rounded-md flex items-center justify-center">
              {isDarkMode ? (
                <Sun className="w-3 h-3 text-white" />
              ) : (
                <Moon className="w-3 h-3 text-white" />
              )}
            </div>
            {isDarkMode ? 'Light Mode' : 'Dark Mode'}
          </button>
          
          {/* Settings */}
          <div className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-gray-600 dark:text-gray-400 hover:bg-white/50 dark:hover:bg-gray-800/50 rounded-lg cursor-pointer transition-all-smooth btn-hover">
            <div className="w-5 h-5 bg-gradient-to-r from-gray-400 to-gray-500 rounded-md flex items-center justify-center">
              <Settings className="w-3 h-3 text-white" />
            </div>
            Settings
          </div>
        </div>
      </div>

      {/* Mobile Overlay */}
      {sidebarOpen && (
        <div 
          className="md:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-30 transition-all-smooth"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            /* Welcome Screen */
            <div className="flex flex-col items-center justify-center h-full px-6 text-center animate-fade-in">
              <div className="mb-12">
                <div className="relative mb-6 mx-auto">
                  <div className="w-20 h-20 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 rounded-2xl flex items-center justify-center shadow-2xl animate-pulse-soft">
                    <Sparkles className="w-10 h-10 text-white" />
                  </div>
                  <div className="absolute -top-1 -right-1 w-6 h-6 bg-green-500 rounded-full border-2 border-white dark:border-gray-900 shadow-lg"></div>
                </div>
                <h1 className="text-4xl font-bold bg-gradient-to-r from-gray-900 via-blue-800 to-indigo-900 dark:from-white dark:via-blue-200 dark:to-indigo-200 bg-clip-text text-transparent mb-4">
                  How can I help you today?
                </h1>
                <p className="text-lg text-gray-600 dark:text-gray-400 max-w-2xl leading-relaxed">
                  I&apos;m your AI assistant specialized in SPL queries and data analysis. 
                  Ready to help you with Splunk searches, data modeling, and cybersecurity investigations.
                </p>
              </div>

              {/* Suggested Prompts */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4 max-w-4xl w-full">
                {suggestedPrompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => setInputText(prompt)}
                    className="group p-6 text-left bg-white/80 dark:bg-gray-800/80 hover:bg-white dark:hover:bg-gray-800 rounded-2xl border border-gray-200/50 dark:border-gray-700/50 hover:border-blue-300 dark:hover:border-blue-600 transition-all-smooth shadow-lg hover:shadow-xl btn-hover backdrop-blur-sm"
                  >
                    <div className="flex items-start gap-3">
                      <div className="w-8 h-8 bg-gradient-to-r from-blue-500 to-indigo-500 rounded-lg flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform">
                        <Sparkles className="w-4 h-4 text-white" />
                      </div>
                      <div>
                        <div className="text-sm font-semibold text-gray-900 dark:text-white mb-1 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors">
                          {prompt}
                        </div>
                        <div className="text-xs text-gray-500 dark:text-gray-400">
                          Click to try this prompt
                        </div>
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          ) : (
            /* Messages */
            <div className="max-w-4xl mx-auto py-8 px-6 md:px-8">
              {/* Error Notification */}
              {error && (
                <div className="mb-6 p-5 bg-red-50/80 dark:bg-red-900/20 border border-red-200/50 dark:border-red-700/50 rounded-2xl shadow-lg backdrop-blur-sm animate-fade-in">
                  <div className="flex items-center gap-3">
                    <div className="w-6 h-6 bg-red-500 rounded-full flex items-center justify-center flex-shrink-0">
                      <X className="w-4 h-4 text-white" />
                    </div>
                    <div className="text-sm text-red-700 dark:text-red-400">
                      <strong>Error:</strong> {error}
                    </div>
                  </div>
                </div>
              )}
              
              {messages.map((message, index) => (
                <div key={message.id} className="mb-8 message-enter" style={{ animationDelay: `${index * 0.1}s` }}>
                  <MessageBubble message={message} />
                </div>
              ))}

              {/* Typing Indicator */}
              {isTyping && (
                <div className="mb-8 animate-fade-in">
                  <div className="flex gap-4">
                    <div className="w-10 h-10 bg-gradient-to-r from-blue-500 via-purple-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg animate-pulse-soft">
                      <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <div className="flex-1">
                      <div className="font-semibold text-gray-900 dark:text-white mb-2">Assistant is thinking...</div>
                      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-sm rounded-2xl p-4 border border-gray-200/50 dark:border-gray-700/50 shadow-lg">
                        <div className="typing-dots">
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                          <div className="typing-dot"></div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-200/50 dark:border-gray-800/50 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md p-6">
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-blue-500/10 to-indigo-500/10 rounded-2xl blur-xl"></div>
              <textarea
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me about SPL queries, data analysis, or anything else..."
                className="relative w-full px-6 py-4 pr-16 bg-white/90 dark:bg-gray-800/90 backdrop-blur-sm border border-gray-200/50 dark:border-gray-700/50 rounded-2xl resize-none focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-300 dark:focus:border-blue-600 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 text-sm leading-relaxed shadow-lg hover:shadow-xl transition-all-smooth"
                rows={1}
                style={{ minHeight: '56px', maxHeight: '200px' }}
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim() || isTyping}
                className={`absolute right-3 top-1/2 -translate-y-1/2 p-3 rounded-xl transition-all-smooth shadow-lg hover:shadow-xl ${
                  !inputText.trim() || isTyping
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 btn-hover'
                } text-white`}
                title={!inputText.trim() ? 'Please type a message' : isTyping ? 'Processing...' : 'Send message'}
              >
                {isTyping ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
