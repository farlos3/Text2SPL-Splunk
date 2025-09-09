import { ChatMessage, ChatResponse, ApiError } from '@/types/chat';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// SPL-related types
export interface SPLRequest {
  query: string;
  verbose?: boolean;
}

export interface SPLResponse {
  success: boolean;
  spl_query?: string;
  company?: string;
  index?: string;
  sourcetype?: string;
  confidence?: number;
  detection_method?: string;
  syntax_valid?: boolean;
  issues?: string[];
  error?: string;
  original_query?: string;
  improved_query?: string;
}

export interface RelevanceCheckResponse {
  is_splunk_related: boolean;
  confidence: number;
  detection_method: string;
}

export interface SPLValidationResponse {
  is_valid: boolean;
  issues: string[];
  suggestions?: string[];
}

class ApiService {
  private baseUrl: string;

  constructor(baseUrl: string = API_BASE_URL) {
    this.baseUrl = baseUrl;
  }

  // Health check endpoint
  async healthCheck(): Promise<{ status: string; message: string }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/health`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Health check failed:', error);
      throw error;
    }
  }

  // Send chat message
  async sendMessage(content: string): Promise<ChatResponse> {
    try {
      const messageData: ChatMessage = {
        content,
        sender: 'user'
      };

      const response = await fetch(`${this.baseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(messageData),
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: ChatResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Send message failed:', error);
      throw error;
    }
  }

  // Get chat history (placeholder)
  async getChatHistory(): Promise<{ messages: any[] }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/chat/history`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Get chat history failed:', error);
      throw error;
    }
  }

  // SPL Generation Methods
  
  // Generate SPL query from natural language
  async generateSPL(query: string, verbose: boolean = false): Promise<SPLResponse> {
    try {
      const requestData: SPLRequest = { query, verbose };
      
      const response = await fetch(`${this.baseUrl}/api/spl/generate-spl`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: SPLResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Generate SPL failed:', error);
      throw error;
    }
  }

  // Check if query is Splunk-related (using relevance detection)
  async checkSplunkRelevance(query: string): Promise<RelevanceCheckResponse> {
    try {
      const requestData: SPLRequest = { query };
      
      const response = await fetch(`${this.baseUrl}/api/spl/check-relevance`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: RelevanceCheckResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Check relevance failed:', error);
      throw error;
    }
  }

  // Validate SPL syntax
  async validateSPL(spl_query: string): Promise<SPLValidationResponse> {
    try {
      const response = await fetch(`${this.baseUrl}/api/spl/validate-spl`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ spl_query }),
      });

      if (!response.ok) {
        const errorData: ApiError = await response.json();
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data: SPLValidationResponse = await response.json();
      return data;
    } catch (error) {
      console.error('Validate SPL failed:', error);
      throw error;
    }
  }

  // Get available companies
  async getCompanies(): Promise<{ companies: any[]; total: number }> {
    try {
      const response = await fetch(`${this.baseUrl}/api/spl/companies`);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Get companies failed:', error);
      throw error;
    }
  }
}

// Export singleton instance
export const apiService = new ApiService();
export default ApiService;
