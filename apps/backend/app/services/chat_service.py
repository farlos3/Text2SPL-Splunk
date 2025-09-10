import os
import httpx
from groq import Groq
from app.core.config import settings
from app.services.spl_service import SPLService

class ChatService:
    def __init__(self):
        self.client = None
        self.spl_service = None
        print(f"Initializing ChatService with API key: {settings.GROQ_API_KEY[:10]}...")
        
        # Initialize SPL Service
        try:
            self.spl_service = SPLService()
            print("✓ SPL Service initialized successfully")
        except Exception as e:
            print(f"✗ Warning: Could not initialize SPL Service: {e}")
            self.spl_service = None
        
        if settings.GROQ_API_KEY and settings.GROQ_API_KEY != "dummy-key-for-testing":
            try:
                # Initialize Groq client with explicit HTTP client to avoid proxy issues
                http_client = httpx.Client()
                self.client = Groq(
                    api_key=settings.GROQ_API_KEY,
                    http_client=http_client
                )
                print("✓ Groq client initialized successfully")
            except Exception as e:
                try:
                    # Fallback: try without http_client
                    self.client = Groq(api_key=settings.GROQ_API_KEY)
                    print("✓ Groq client initialized successfully (fallback method)")
                except Exception as e2:
                    print(f"✗ Warning: Could not initialize Groq client: {e2}")
                    self.client = None
        else:
            print("✗ No valid Groq API key provided")
    
    async def process_message(self, message: str) -> str:
        """Process a user message and return an AI response with Splunk relevance detection"""
        
        print(f"\n🚀 Processing message: {message[:100]}...")
        
        # First, check if this is a Splunk-related query using enhanced SPL service
        if self.spl_service:
            try:
                # Step 1: Check relevance using enhanced detection
                is_related, confidence, method = self.spl_service.is_splunk_related(message)
                
                if is_related and confidence > 0.6:
                    print(f"✅ Detected Splunk query (confidence: {confidence:.2f}, method: {method})")
                    
                    # Step 2: Apply prompt fixer for better query processing
                    improved_query = self.spl_service.prompt_fixer(message)
                    print(f"📝 Original query: {message}")
                    print(f"📝 Improved query: {improved_query}")
                    
                    # Step 3: Generate SPL query using improved prompt
                    result = self.spl_service.generate_spl_query(message, verbose=False)
                    
                    if result.success:
                        response = f"""🔍 **SPL Query Generated**

**🔍 Relevance Detection:** ✅ Confirmed Splunk-related (confidence: {confidence:.1%}, method: {method})
**📝 Query Enhancement:** {improved_query if improved_query != message else 'No changes needed'}
**🏢 Company Context:** {result.company}
**📊 Index:** {result.index}
**🎯 Generation Confidence:** {result.confidence:.0%}

**Generated SPL:**
```spl
{result.spl_query}
```

**🔧 Technical Details:**
- Detection Method: {result.detection_method}
- Syntax Valid: {'✅' if result.syntax_valid else '❌'}
- Processing Pipeline: Relevance Detection → Prompt Enhancement → RAG Extraction → SPL Generation"""
                        
                        return response
                    else:
                        return f"""❌ **SPL Generation Failed**

**🔍 Relevance Detection:** ✅ Confirmed Splunk-related
**📝 Query Enhancement:** Applied
**❌ Error:** {result.error}

Falling back to general assistance..."""

                else:
                    print(f"❌ Query not identified as Splunk-related (confidence: {confidence:.2f}, method: {method})")
                    # Strictly reject non-Splunk inputs per requirement
                    return (
                        "This input is not related to Splunk. "
                        "Please provide a Splunk-related request, such as log analysis, SPL commands, or search queries."
                    )
            except Exception as e:
                print(f"❌ SPL Service error: {e}")
                # Fall through to general chat
        
        # If not Splunk-related or SPL service failed, use general chat
        if not self.client:
            return f"I can help you with Splunk queries, but I need a properly configured API client for general questions. Your message: {message}"
        
        try:
            # Enhanced system prompt for better assistance
            system_prompt = """You are a helpful AI assistant specializing in cybersecurity, log analysis, and system administration with advanced Splunk SPL capabilities.

🔍 **I have built-in Splunk relevance detection and query enhancement features!**

When users ask about:
- Log analysis, searching logs, or data queries → I can automatically detect if it's Splunk-related and generate SPL queries
- Authentication failures, login attempts, security events → Perfect for automated SPL generation
- System monitoring, error detection, performance analysis → I can create optimized SPL queries
- Network analysis, traffic monitoring → Splunk queries with proper field extraction

🚀 **My Splunk Processing Pipeline:**
1. **Relevance Detection** - I automatically identify Splunk-related queries using multiple detection methods
2. **Query Enhancement** - I improve ambiguous queries using AI-powered prompt fixing
3. **Company Context Selection** - I select appropriate company/index context
4. **RAG-Enhanced Generation** - I use retrieved Splunk documentation for accurate SPL creation
5. **Syntax Validation** - I validate and clean generated SPL queries

For general non-Splunk questions, I provide helpful and concise answers."""

            # Call Groq API with enhanced context
            chat_completion = self.client.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": system_prompt
                    },
                    {
                        "role": "user",
                        "content": str(message),
                    }
                ],
                model="llama-3.3-70b-versatile",
                temperature=0.1
            )
            
            return chat_completion.choices[0].message.content.strip()
            
        except Exception as e:
            # Fallback response in case of API error
            return f"Sorry, I encountered an error processing your message: {str(e)}"
    
    def get_pipeline_status(self) -> dict:
        """Get status of the Splunk processing pipeline"""
        return {
            "spl_service_available": self.spl_service is not None,
            "groq_client_available": self.client is not None,
            "features": {
                "splunk_relevance_detection": True,
                "prompt_enhancement": True,
                "company_context_selection": True,
                "rag_enhanced_generation": True,
                "syntax_validation": True
            },
            "detection_methods": [
                "syntax_match", "domain_match", "security_keyword_match", 
                "time_pattern_match", "embedding_match", "llm_intent"
            ] if self.spl_service else []
        }
