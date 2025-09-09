export interface Message {
  id: string;
  content: string;  // ใช้ content แทน text ให้ตรงกับ backend
  sender: 'user' | 'assistant';  // ใช้ assistant แทน bot
  timestamp: Date;
}

export interface ChatMessage {
  content: string;
  sender: string;
  timestamp?: Date;
}

export interface ChatResponse {
  content: string;
  sender: string;
  timestamp?: Date;
}

export interface ChatState {
  messages: Message[];
  isTyping: boolean;
  inputText: string;
}

export interface ApiError {
  detail: string;
}
