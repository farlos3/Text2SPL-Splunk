# Splunk Processing Pipeline - Backend Implementation

## Overview
The backend has been enhanced with a comprehensive **Splunk Relevance Detection + Prompt Fixer** pipeline that automatically identifies Splunk-related queries and generates optimized SPL queries.

## 🔧 Pipeline Architecture

```
User Input → Relevance Detection → Prompt Enhancement → Company Selection → RAG Extraction → SPL Generation → Validation
     ↓               ↓                   ↓                 ↓               ↓               ↓            ↓
"show login    →    ✅ Splunk        →  "Show failed   → HealthPlus    →  Elements    → Final SPL  → ✅ Valid
 fails"             Related            authentication     detected       extracted
                    (85% conf)         events in the
                                      last 24 hours"
```

## 🎯 Key Features Implemented

### 1. **Splunk Relevance Detection** (`SPLService.is_splunk_related()`)
- **Syntax matching**: Detects SPL commands (`index=`, `| stats`, etc.)
- **Domain keywords**: Identifies Splunk-related terms
- **Security patterns**: Recognizes security/IT queries
- **Time patterns**: Detects temporal queries
- **Semantic similarity**: Uses embeddings for context understanding
- **LLM fallback**: AI-powered intent analysis

### 2. **Prompt Enhancement** (`SPLService.prompt_fixer()`)
- Improves ambiguous queries
- Adds missing context
- Clarifies user intent
- Standardizes terminology

### 3. **Company Context Selection** (`SPLService._pick_best_company()`)
- Direct company name matching
- Product name identification  
- Domain/use case analysis
- Keyword-based scoring

### 4. **RAG-Enhanced Generation**
- Document retrieval from Splunk docs
- Cross-encoder reranking
- Context-aware element extraction

### 5. **Syntax Validation & Clean Output**
- SPL syntax checking
- Query optimization
- Clean formatting

## 📁 File Changes Made

### `apps/backend/app/services/chat_service.py`
```python
async def process_message(self, message: str) -> str:
    # ✅ Enhanced with full pipeline
    
    # Step 1: Relevance Detection
    is_related, confidence, method = self.spl_service.is_splunk_related(message)
    
    # Step 2: Prompt Enhancement  
    improved_query = self.spl_service.prompt_fixer(message)
    
    # Step 3: SPL Generation with enhanced pipeline
    result = self.spl_service.generate_spl_query(message, verbose=False)
```

### `apps/backend/app/services/spl_service.py`
```python
def generate_spl_query(self, user_query: str, verbose: bool = False) -> SPLResponse:
    # ✅ Full pipeline implementation
    
    # Step 1: Splunk Relevance Detection
    is_related, conf, method = self.is_splunk_related(user_query, embedding_threshold=0.35)
    
    # Step 2: Prompt Enhancement
    improved = self.prompt_fixer(user_query)
    
    # Step 3: RAG with improved prompt
    top_k_docs = self.select_top_k(improved, k=4, initial_n=8)
    
    # Step 4: SPL Generation with improved prompt
    spl_query = self._generate_unified_spl_query(improved, company, extracted_elements=extracted)
```

## 🚀 API Endpoints

### Chat Endpoint with Pipeline
```
POST /api/chat
{
  "content": "Show failed logins for HealthPlus"
}
```

**Response includes:**
- Relevance detection results
- Query enhancement details  
- Company context selection
- Generated SPL with validation

### Pipeline Status Endpoint
```
GET /api/chat/pipeline-status
```

**Response:**
```json
{
  "success": true,
  "pipeline_status": {
    "spl_service_available": true,
    "groq_client_available": true,
    "features": {
      "splunk_relevance_detection": true,
      "prompt_enhancement": true,
      "company_context_selection": true,
      "rag_enhanced_generation": true,
      "syntax_validation": true
    },
    "detection_methods": ["syntax_match", "domain_match", "security_keyword_match", ...]
  }
}
```

## 🔍 Detection Methods

1. **syntax_match** - Direct SPL syntax detection
2. **domain_match** - Splunk terminology 
3. **security_keyword_match** - Security-related terms
4. **time_pattern_match** - Temporal queries
5. **embedding_match** - Semantic similarity
6. **llm_intent** - AI-powered classification

## 🧪 Testing

Run the pipeline test:
```bash
cd apps/backend
python test_pipeline.py
```

This tests:
- ✅ Relevance detection accuracy
- ✅ Prompt enhancement quality
- ✅ Full chat pipeline integration
- ✅ SPL generation with validation

## 💡 Example Interactions

### Input: "show login fails healthplus"
```
🔍 Relevance Detection: ✅ Confirmed (confidence: 85%, method: security_keyword_match)
📝 Query Enhancement: "Show failed authentication events for HealthPlus in the last 24 hours"
🏢 Company Context: HealthPlus - Medical Systems
Generated SPL:
```spl
index=HealthPlus_windows sourcetype=wineventlog EventCode=4625 earliest=-24h
| stats count by src_ip, Account_Name
| sort - count
```

### Input: "What is artificial intelligence?"
```
❌ Query not identified as Splunk-related (confidence: 15%, method: embedding_match)
→ Processed as general chat
```

## ✅ Implementation Status

- [x] **Splunk Relevance Detection** - Multiple detection methods
- [x] **Prompt Enhancement** - AI-powered query improvement  
- [x] **Company Context Selection** - Smart company matching
- [x] **RAG Integration** - Document-enhanced generation
- [x] **Syntax Validation** - SPL query validation
- [x] **Pipeline Integration** - Full chat service integration
- [x] **API Endpoints** - Complete backend API
- [x] **Error Handling** - Robust error management
- [x] **Logging & Debugging** - Comprehensive logging
- [x] **Testing Framework** - Automated pipeline testing

The backend now provides a complete Splunk processing pipeline with intelligent query detection, enhancement, and SPL generation!
