import { Database, Shield, Activity } from 'lucide-react';

export default function ChatHeader() {
  return (
    <div className="bg-gradient-to-r from-blue-600 to-indigo-600 dark:from-blue-700 dark:to-indigo-700 text-white p-4 shadow-lg">
      <div className="max-w-4xl mx-auto">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
            <Database className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold">
              Splunk SPL Generator
            </h1>
            <p className="text-blue-100 text-sm">
              AI-Powered Security Query Assistant
            </p>
          </div>
        </div>
        
        <div className="flex items-center gap-6 text-xs text-blue-100">
          <div className="flex items-center gap-1">
            <Shield className="w-3 h-3" />
            <span>Security Analysis</span>
          </div>
          <div className="flex items-center gap-1">
            <Activity className="w-3 h-3" />
            <span>Log Monitoring</span>
          </div>
          <div className="flex items-center gap-1">
            <Database className="w-3 h-3" />
            <span>Multi-Company Support</span>
          </div>
        </div>
      </div>
    </div>
  );
}
