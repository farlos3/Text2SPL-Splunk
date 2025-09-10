"""
SPL Generation Service
Adapted from Markdown-OCR-tech-flow.ipynb
"""

import os
import json
import re
import time
import warnings
import logging
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*")
logging.getLogger("transformers").setLevel(logging.ERROR)

try:
    from transformers import logging as transformers_logging
    transformers_logging.set_verbosity_error()
except ImportError:
    pass

# LangChain imports
from langchain_community.document_loaders import UnstructuredPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain.schema import Document
from sentence_transformers import CrossEncoder

# Groq client
from groq import Groq

from app.models.spl import SPLResponse, CompanyInfo, RelevanceCheckResponse

class SPLService:
    def __init__(self):
        """Initialize SPL Service with all required components"""
        self.groq_model = "llama-3.3-70b-versatile"
        self.groq_api_key = os.environ.get("GROQ_API_KEY")
        self.client = Groq(api_key=self.groq_api_key) if self.groq_api_key else None
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # Initialize cross encoder for reranking
        self.cross_encoder = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")
        
        # Load data files
        self._load_data_files()
        
        # Initialize vector store
        self._initialize_vector_store()
        
        # Cache for intent anchors
        self._anchor_embs = None
        
        # Splunk keywords and patterns
        self._initialize_splunk_patterns()
    
    def _load_data_files(self):
        """Load QA pairs and company data"""
        # Try multiple possible paths for data files
        possible_bases = [
            "f:/University/AISecOps/KBTG Cyber Security/INTERN/LLM/Splunk Query Docs/",
            "./data/",
            "../data/",
            os.path.join(os.path.dirname(__file__), "..", "..", "data")
        ]
        
        # Load QA pairs
        self.qa_pairs = []
        for base_path in possible_bases:
            try:
                qa_json_path = os.path.join(base_path, "qa_pairs-normal.json")
                with open(qa_json_path, "r", encoding="utf-8") as f:
                    self.qa_pairs = json.load(f)
                print(f"Loaded QA pairs from: {qa_json_path}")
                break
            except FileNotFoundError:
                continue
        
        if not self.qa_pairs:
            print("Warning: QA pairs file not found in any path, using empty list")
        
        # Load company data
        self.company_data = []
        for base_path in possible_bases:
            try:
                company_json_path = os.path.join(base_path, "index-sourcetype.json")
                with open(company_json_path, "r", encoding="utf-8") as f:
                    self.company_data = json.load(f)
                print(f"Loaded company data from: {company_json_path}")
                break
            except FileNotFoundError:
                continue
        
        if not self.company_data:
            # Default company data if file not found
            self.company_data = [
                {
                    "company_name": "Default",
                    "product_name": "System",
                    "index": "main",
                    "sourcetype": "*",
                    "domain": "General",
                    "use_cases": "Log analysis",
                    "data_model": []
                }
            ]
            print("Warning: Company data file not found, using default")
    
    def _initialize_vector_store(self):
        """Initialize FAISS vector store with document chunks"""
        # Check if we have pre-processed documents
        output_md_path = "f:/University/AISecOps/KBTG Cyber Security/INTERN/LLM/Splunk Query Docs/output.md"
        
        try:
            with open(output_md_path, "r", encoding="utf-8") as f:
                content_doc = f.read()
            
            # Split into chunks
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=25000,
                chunk_overlap=3300,
                separators=["\\n\\n", "\\n", ".", " "]
            )
            chunks_doc = text_splitter.split_text(content_doc)
            
            # Create FAISS vector store
            documents = [Document(page_content=c) for c in chunks_doc]
            self.vectorstore_doc = FAISS.from_documents(documents, self.embedding_model)
            
        except FileNotFoundError:
            # Create empty vector store if no documents found
            documents = [Document(page_content="Default Splunk documentation")]
            self.vectorstore_doc = FAISS.from_documents(documents, self.embedding_model)
            print("Warning: Documentation file not found, using minimal vector store")
    
    def _initialize_splunk_patterns(self):
        """Initialize Splunk syntax and domain keywords"""
        self.splunk_syntax_keywords = [
            'index=', 'sourcetype=', 'source=', 'host=', 'earliest=', 'latest=',
            '| stats', '| table', '| search', '| where', '| fields', '| rename',
            '| eval', '| timechart', '| transaction', '| bucket', '| top', 
            '| rare', '| chart', '| dedup', '| rex', '| spath', '| sort',
            '| head', '| tail', '| join', '| lookup', '| mvexpand', '| mvcombine',
            '| outputlookup', '| multikv', '| inputlookup', '| append',
            '| collect', '| datamodel', '| dbinspect', '| metadata', '| savedsearch'
        ]
        
        self.splunk_domain_keywords = [
            'splunk', 'spl', 'dashboard', 'search head', 'indexer', 'forwarder',
            'knowledge object', 'search app', 'security essentials', 'itsi', 'enterprise security',
            'monitoring console', 'universal forwarder', 'heavy forwarder', 'deployment server',
            'search processing language', 'search job', 'event log', 'field extraction', 'pivot',
            'lookup table', 'eventtypes', 'tags', 'props.conf', 'transforms.conf'
        ]
        
        self.splunk_intent_anchors = [
            "Find logs or events matching specific criteria",
            "Search for specific patterns in log data",
            "Filter events by time range",
            "Analyze system performance metrics",
            "Monitor security incidents",
            "Extract fields from log data",
            "Create statistics from event data",
            "Visualize trends in time-series data",
            "Calculate metrics from events",
            "Detect anomalies in system behavior",
            "Detect suspicious login activities",
            "Find unusual access patterns",
            "Monitor authentication failures",
            "Track network connections",
            "Investigate security alerts",
            "Monitor application performance",
            "Track system resource utilization",
            "Alert on service outages",
            "Analyze error rates",
            "Report on system availability"
        ]
    
    def call_model(self, messages, model=None, temperature=0):
        """Call Groq LLM"""
        if self.client is None:
            raise RuntimeError("Groq client not configured. Set GROQ_API_KEY environment variable.")
        
        if not isinstance(messages, list):
            messages = [{"role": "user", "content": str(messages)}]
        
        model = model or self.groq_model
        resp = self.client.chat.completions.create(
            model=model, 
            messages=messages, 
            temperature=temperature
        )
        return resp.choices[0].message.content.strip()
    
    def _ensure_anchor_cache(self):
        """Ensure intent anchor embeddings are cached"""
        if self._anchor_embs is None:
            self._anchor_embs = np.array([
                self.embedding_model.embed_query(a) for a in self.splunk_intent_anchors
            ])
    
    def is_splunk_related(self, query: str, embedding_threshold=0.30, llm_threshold=0.5) -> Tuple[bool, float, str]:
        """Enhanced Splunk relevance detection"""
        q = query.lower()
        
        # Direct syntax match (highest confidence)
        if any(k in q for k in self.splunk_syntax_keywords):
            return True, 0.95, "syntax_match"
        
        # Domain keywords match
        if any(k in q for k in self.splunk_domain_keywords):
            return True, 0.88, "domain_match"
        
        # Enhanced security and system monitoring keywords
        security_keywords = [
            'login', 'logon', 'authentication', 'auth', 'failed', 'success', 'failure',
            'security', 'alert', 'attack', 'intrusion', 'breach', 'threat',
            'service', 'process', 'system', 'registry', 'change', 'modification',
            'network', 'connection', 'traffic', 'port', 'firewall',
            'event', 'log', 'audit', 'monitor', 'detect', 'search',
            'user', 'account', 'access', 'permission', 'group',
            'ssh', 'rdp', 'windows', 'linux', 'server'
        ]
        
        if any(keyword in q for keyword in security_keywords):
            return True, 0.80, "security_keyword_match"
        
        # Time-based queries (common in log analysis)
        time_patterns = ['last', 'recent', 'past', 'today', 'yesterday', 'hour', 'day', 'week', 'month']
        if any(pattern in q for pattern in time_patterns):
            return True, 0.75, "time_pattern_match"
        
        # Embedding similarity check
        self._ensure_anchor_cache()
        qvec = self.embedding_model.embed_query(q)
        sims = cosine_similarity([qvec], self._anchor_embs)[0]
        max_score = float(np.max(sims))
        if max_score >= embedding_threshold:
            return True, max_score, "embedding_match"
        
        # LLM-based intent analysis fallback
        is_related, conf, method = self._llm_is_splunk_related(query, threshold=llm_threshold)
        return is_related, conf, method
    
    def _llm_is_splunk_related(self, query: str, model=None, threshold=0.5) -> Tuple[bool, float, str]:
        """LLM-based Splunk intent classification"""
        system = (
            "You are an expert Splunk SPL intent classifier. "
            "Return only JSON: {\"is_splunk_related\": true/false, \"confidence\": float, \"reasoning\": str}. "
            "Classify if the query is about Splunk data search, analysis, or reporting."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Query: {query}\\nClassify intent."}
        ]
        
        try:
            resp = self.call_model(messages, model=model)
            m = re.search(r"\\{.*\\}", resp, re.S)
            obj_str = m.group(0) if m else ""
            obj_str = obj_str.replace("'", '"')
            obj = json.loads(obj_str)
        except Exception:
            obj = {"is_splunk_related": False, "confidence": 0.0, "reasoning": "fallback"}
        
        return obj["is_splunk_related"], obj["confidence"], "llm_intent"
    
    def prompt_fixer(self, user_input: str) -> str:
        """Improve user prompt for better SPL generation"""
        system = (
            "You are an expert prompt engineer for Splunk SPL. Return only the improved prompt."
        )
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": f"Original request:\\n{user_input}\\n\\nNow provide an improved prompt"}
        ]
        return self.call_model(messages)
    
    def rerank_chunks(self, retrieved_docs, query):
        """Rerank retrieved documents using cross-encoder"""
        scores = []
        for doc in retrieved_docs:
            score = self.cross_encoder.predict([(query, doc.page_content)])
            scores.append((doc, float(score[0])))
        return sorted(scores, key=lambda x: x[1], reverse=True)
    
    def select_top_k(self, query: str, k=4, initial_n=8):
        """Select top-k documents with reranking"""
        retrieved = self.vectorstore_doc.similarity_search(query, k=initial_n)
        ranked = self.rerank_chunks(retrieved, query)
        return [doc for doc, _ in ranked[:k]]
    
    def validate_spl_syntax(self, spl_query: str) -> List[str]:
        """Validate SPL query syntax"""
        issues = []
        
        # Check for basic index specification
        if "index=" not in spl_query and "| " not in spl_query.split('\\n')[0]:
            issues.append("Query should specify an index (e.g., index=main)")
        
        # Check for proper pipe usage
        lines = spl_query.split('\\n')
        for i, line in enumerate(lines):
            if i > 0 and line.strip() and not line.strip().startswith('|') and not line.strip().startswith('#'):
                issues.append(f"Line {i+1}: missing pipe |")
        
        # Check for common syntax issues
        if '=' in spl_query and ' = ' in spl_query:
            issues.append("Use = without spaces for field assignments")
        
        return issues
    
    def _clean_spl_output(self, spl_query: str) -> str:
        """Clean and format SPL query for better display"""
        import re
        
        # Remove any markdown code blocks
        spl_query = re.sub(r'```(?:spl|splunk)?\n?', '', spl_query)
        spl_query = re.sub(r'```\n?', '', spl_query)
        
        # Remove extra whitespace and normalize formatting
        spl_query = spl_query.strip()
        
        # Clean up pipe formatting - ensure proper spacing
        spl_query = re.sub(r'\s*\|\s*', ' | ', spl_query)
        
        # Clean up field assignments
        spl_query = re.sub(r'\s*=\s*', '=', spl_query)
        
        # Remove any explanatory text at the beginning or end
        lines = spl_query.split('\n')
        clean_lines = []
        
        for line in lines:
            line = line.strip()
            # Skip explanatory or comment lines
            if (line.startswith('This query') or 
                line.startswith('The above') or 
                line.startswith('Note:') or
                line.startswith('Explanation:') or
                line.startswith('This SPL') or
                line.startswith('Generated') or
                line.startswith('**') or
                not line):
                continue
            clean_lines.append(line)
        
        # Join lines with proper formatting
        if len(clean_lines) > 1:
            # Multi-line query - format with proper indentation
            result = clean_lines[0]  # First line (usually the search)
            for line in clean_lines[1:]:
                if line.strip().startswith('|'):
                    result += '\n' + line
                else:
                    result += ' ' + line
        else:
            result = ' '.join(clean_lines)
        
        return result.strip()
    
    def check_relevance(self, query: str) -> RelevanceCheckResponse:
        """Check if query is Splunk-related"""
        is_related, confidence, method = self.is_splunk_related(query)
        return RelevanceCheckResponse(
            is_splunk_related=is_related,
            confidence=confidence,
            method=method
        )
    
    def _get_most_relevant_qa_examples(self, query: str, qa_pairs: List[Dict], k: int = 5) -> List[Dict]:
        """Get the most relevant QA examples for a given query"""
        if not qa_pairs:
            return []
        
        valid_qa = [qa for qa in qa_pairs if isinstance(qa, dict) and qa.get("question") and qa.get("answer")]
        if not valid_qa:
            return []
        
        query_embedding = self.embedding_model.embed_query(query)
        qa_embedding = [self.embedding_model.embed_query(qa["question"]) for qa in valid_qa]
        similarities = cosine_similarity([query_embedding], qa_embedding)[0]
        top_indices = np.argsort(-similarities)[:k]
        
        return [valid_qa[i] for i in top_indices]
    
    def _generate_partial_answers(self, top_k_docs, qa_pairs, query, k_qa=10, batch_char_limit=5000, delay=0):
        """Generate partial answers using RAG (retrieval augmented generation)"""
        if not top_k_docs or not qa_pairs:
            return []
        
        spl_template = """You are an expert Splunk SPL analyzer. Your task is to extract relevant SPL elements from the given inputs.

CONTEXT TYPES:
1. Documentation Chunk — explanations, command usage, examples, descriptions.
2. QA Pairs — each contains a user question and an SPL answer.

OBJECTIVE:
Extract useful SPL elements that are explicitly present or clearly implied. Keep outputs general and reusable (avoid hardcoded org-specific assumptions).

EXTRACT THE FOLLOWING (deduplicate across sources):
- Index names and sourcetypes (literal values as they appear).
- Field names and common aliases seen with coalesce patterns (e.g., user fields, source IP/host fields, service path fields).
- Search commands and syntax (search, where, eval, bin/bucket, stats, eventstats, streamstats, sort, head, top, dedup, join).
- Statistical functions (count, dc, sum, avg, min, max, percentile if present) and their typical usage contexts.
- Filtering conditions and operators (AND/OR/IN, match/regex, like, isnull/isnotnull).
- Time range specs and bucketing (earliest=..., latest=..., @d, bin/timechart span=...).
- Grouping/sorting/limit patterns (stats by <fields>, sort - <field>, head/top N).
- Subsearch/join patterns (e.g., correlating two datasets; history vs today).
- Visualization commands (timechart, chart) and common parameter shapes.
- Any COMPLETE example queries present in the sources.

INSTRUCTIONS:
- DO NOT generate or rewrite a new query.
- Be specific about syntax and parameters; quote literal values as shown.
- If both sources mention the same concept, mention it once.
- Prioritize elements that directly relate to the QA question/answer.
- If nothing useful is present, return "No relevant information".

Question: {question}
Documentation Chunk: {doc_chunk}
QA Question: {qa_question}
QA Answer: {qa_answer}

RETURN FORMAT (clear labeled sections):
- Indexes & Sourcetypes
- Fields & Aliases (with typical coalesce groups)
- Commands & Syntax
- Stats & Aggregations
- Filters & Operators
- Time & Bucketing
- Grouping/Sorting/Limits
- Subsearch/Join Patterns
- Visualization
- Complete Examples
"""
        
        valid_qa = [qa for qa in qa_pairs if isinstance(qa, dict) and qa.get("question") and qa.get("answer")]
        query_embedding = self.embedding_model.embed_query(query)
        qa_embedding = [self.embedding_model.embed_query(qa["question"]) for qa in valid_qa]
        similarities = cosine_similarity([query_embedding], qa_embedding)[0]
        top_m = min(k_qa, len(valid_qa))
        top_indices = np.argsort(-similarities)[:top_m]

        partial_answers = []
        for i, doc in enumerate(top_k_docs):
            qa_idx = top_indices[i % len(top_indices)]
            qa_q = valid_qa[qa_idx]["question"]
            qa_a = valid_qa[qa_idx]["answer"]
            prompt = spl_template.format(
                question=query,
                doc_chunk=(getattr(doc, "page_content", str(doc)) or "")[:batch_char_limit],
                qa_question=qa_q,
                qa_answer=qa_a
            )
            ans = self.call_model(prompt)
            partial_answers.append(ans)
            if delay:
                time.sleep(delay)
        return partial_answers
    
    def generate_spl_query(self, user_query: str, verbose: bool = False) -> SPLResponse:
        """Main SPL generation function"""
        try:
            # Check if query is Splunk-related
            is_related, conf, method = self.is_splunk_related(user_query, embedding_threshold=0.35)
            if not is_related:
                return SPLResponse(
                    success=False,
                    error="Not Splunk-related",
                    confidence=conf,
                    detection_method=method
                )
            
            # Select best company context
            company = self._pick_best_company(user_query, verbose=verbose)
            
            # Improve prompt
            improved = self.prompt_fixer(user_query)
            
            # Try to extract elements using RAG (if available)
            extracted = ""
            try:
                if self.vectorstore_doc:
                    top_k_docs = self.select_top_k(improved, k=4, initial_n=8)
                    partials = self._generate_partial_answers(
                        top_k_docs, self.qa_pairs, improved, k_qa=10
                    )
                    extracted = "\n".join(partials)
            except Exception:
                pass
            
            # Generate SPL using unified template
            spl_query = self._generate_unified_spl_query(improved, company, extracted_elements=extracted, qa_pairs=self.qa_pairs)
            
            # Validate syntax
            issues = self.validate_spl_syntax(spl_query)
            
            # Clean the SPL query before returning
            clean_spl = self._clean_spl_output(spl_query)
            
            return SPLResponse(
                success=True,
                spl_query=clean_spl,
                company=f"{company['company_name']} - {company['product_name']}",
                index=company["index"],
                sourcetype=company["sourcetype"],
                confidence=company["confidence_score"],
                detection_method=company["method"],
                syntax_valid=len(issues) == 0,
                issues=issues
            )
            
        except Exception as e:
            return SPLResponse(
                success=False,
                error=str(e)
            )
    
    def _pick_best_company(self, user_query: str, verbose: bool = False) -> Dict[str, Any]:
        """Enhanced multi-method company selection (dynamic + LLM + semantic), mirroring notebook flow"""
        if not self.company_data:
            return {
                "company_name": "Default",
                "product_name": "System",
                "index": "main",
                "sourcetype": "*",
                "data_model": [],
                "confidence_score": 0.5,
                "method": "fallback",
                "company_index": 0
            }

        # Helper: flat company description
        def _company_descriptions(data):
            descs = []
            for c in data:
                descs.append(
                    f"{c.get('company_name','')} {c.get('product_name','')} "
                    f"{c.get('domain','')} {c.get('use_cases','')} "
                    f"{c.get('index','')} {c.get('sourcetype','')}"
                )
            return descs

        # Strategy A: Dynamic keyword + direct/platform match (fast path)
        def _dynamic_keyword_company_matching(user_query, data):
            words = re.findall(r"\b\w+\b", user_query.lower())
            words = [w for w in words if len(w) > 2]
            scores = []

            for i, c in enumerate(data):
                # Direct company match
                if c['company_name'].lower() in user_query.lower():
                    # Optional platform refinement
                    product_lower = c.get('product_name', '').lower()
                    if 'linux' in user_query.lower() and 'linux' in product_lower:
                        return {
                            "company_name": c["company_name"],
                            "product_name": c["product_name"],
                            "index": c.get("index"),
                            "sourcetype": c.get("sourcetype"),
                            "data_model": c.get("data_model", []),
                            "confidence_score": 0.98,
                            "method": "company_name_direct_match",
                            "explicit_company": True,
                            "match_reason": f"Direct {c['company_name']} + Linux",
                            "company_index": i
                        }
                    if 'windows' in user_query.lower() and 'win' in product_lower:
                        return {
                            "company_name": c["company_name"],
                            "product_name": c["product_name"],
                            "index": c.get("index"),
                            "sourcetype": c.get("sourcetype"),
                            "data_model": c.get("data_model", []),
                            "confidence_score": 0.98,
                            "method": "company_name_direct_match",
                            "explicit_company": True,
                            "match_reason": f"Direct {c['company_name']} + Windows",
                            "company_index": i
                        }
                    return {
                        "company_name": c["company_name"],
                        "product_name": c["product_name"],
                        "index": c.get("index"),
                        "sourcetype": c.get("sourcetype"),
                        "data_model": c.get("data_model", []),
                        "confidence_score": 0.95,
                        "method": "company_name_direct_match",
                        "explicit_company": True,
                        "match_reason": f"Direct mention of {c['company_name']}",
                        "company_index": i
                    }

                # Product/platform match
                product_lower = c.get('product_name', '').lower()
                if 'linux' in user_query.lower() and 'linux' in product_lower:
                    return {
                        "company_name": c["company_name"],
                        "product_name": c["product_name"],
                        "index": c.get("index"),
                        "sourcetype": c.get("sourcetype"),
                        "data_model": c.get("data_model", []),
                        "confidence_score": 0.9,
                        "method": "platform_match",
                        "explicit_company": True,
                        "match_reason": "Platform match: Linux",
                        "company_index": i
                    }
                if 'windows' in user_query.lower() and 'win' in product_lower:
                    return {
                        "company_name": c["company_name"],
                        "product_name": c["product_name"],
                        "index": c.get("index"),
                        "sourcetype": c.get("sourcetype"),
                        "data_model": c.get("data_model", []),
                        "confidence_score": 0.9,
                        "method": "platform_match",
                        "explicit_company": True,
                        "match_reason": "Platform match: Windows",
                        "company_index": i
                    }

                # Context keyword scoring
                text = f"{c['company_name']} {c['product_name']} {c.get('domain','')} {c.get('use_cases','')} {c.get('index','')} {c.get('sourcetype','')}".lower()
                tokens = set(re.findall(r"\b\w+\b", text))
                common_words = set(words).intersection(tokens)
                inter = len(common_words)
                freq = sum(1 for w in words if w in tokens) / (len(words) or 1)
                domain_text = f"{c.get('domain','')} {c.get('use_cases','')}".lower()
                domain_tokens = set(re.findall(r"\b\w+\b", domain_text))
                domain_match = len(set(words).intersection(domain_tokens)) / (len(domain_tokens) or 1)
                weighted_score = inter * 0.3 + freq * 0.4 + domain_match * 0.3
                scores.append((i, weighted_score, common_words))

            if scores:
                idx, score, matched_words = max(scores, key=lambda x: x[1])
                c = data[idx]
                return {
                    "company_name": c["company_name"],
                    "product_name": c["product_name"],
                    "index": c.get("index"),
                    "sourcetype": c.get("sourcetype"),
                    "data_model": c.get("data_model", []),
                    "confidence_score": float(score),
                    "method": "context_keyword_match",
                    "match_reason": f"Context match with keywords: {', '.join(list(matched_words)[:5])}",
                    "company_index": idx
                }
            c = data[0]
            return {
                "company_name": c["company_name"],
                "product_name": c["product_name"],
                "index": c.get("index"),
                "sourcetype": c.get("sourcetype"),
                "data_model": c.get("data_model", []),
                "confidence_score": 0.1,
                "method": "default_fallback",
                "company_index": 0
            }

        # Strategy B: LLM-based analysis
        def _llm_analyze_company_context_advanced(user_query, data):
            descs = []
            for i, c in enumerate(data):
                descs.append(
                    f"Company {i}: {c['company_name']} - {c['product_name']}\n"
                    f"- Domain: {c.get('domain', 'N/A')}\n"
                    f"- Use Cases: {c.get('use_cases', 'N/A')}\n"
                    f"- Index: {c.get('index','')}\n- Sourcetype: {c.get('sourcetype','')}\n"
                    f"- Data Models: {', '.join(c.get('data_model', []))}"
                )
            prompt = (
                f"Analyze the query and select the most appropriate company configuration.\n"
                f"QUERY: {user_query}\n\n"
                f"ANALYSIS STEPS:\n"
                f"1. Check explicit company/abbreviation in the query.\n"
                f"2. Consider technological context (systems, applications, data types).\n"
                f"3. Match domain/use cases with the query's intent.\n\n"
                f"Companies available: {', '.join([c['company_name'] for c in data])}\n\n"
                f"COMPANIES:\n" + "\n".join(descs) +
                "\n\nRespond as JSON with keys: selected_company_index (0-based), confidence_score (0.0-1.0), reasoning, explicit_company_mentioned (true/false), company_name_mentioned, query_context (brief)."
            )
            try:
                resp = self.call_model(prompt)
                m = re.search(r"\{.*\}", resp, re.S)
                obj = json.loads(m.group(0)) if m else {"selected_company_index": 0, "confidence_score": 0.3, "reasoning": "fallback", "explicit_company_mentioned": False}
            except Exception:
                obj = {"selected_company_index": 0, "confidence_score": 0.3, "reasoning": "fallback", "explicit_company_mentioned": False}
            idx = obj.get("selected_company_index", 0)
            idx = idx if 0 <= idx < len(data) else 0
            c = data[idx]
            confidence = float(obj.get("confidence_score", 0.5))
            if obj.get("explicit_company_mentioned", False):
                confidence = max(0.9, confidence)
            return {
                "company_name": c["company_name"],
                "product_name": c["product_name"],
                "index": c.get("index"),
                "sourcetype": c.get("sourcetype"),
                "data_model": c.get("data_model", []),
                "confidence_score": confidence,
                "explicit_company": obj.get("explicit_company_mentioned", False),
                "company_mentioned": obj.get("company_name_mentioned", ""),
                "query_context": obj.get("query_context", ""),
                "reasoning": obj.get("reasoning", ""),
                "method": "llm_analysis",
                "company_index": idx
            }

        # Strategy C: Semantic matching with embeddings
        def _semantic_company_matching(user_query, data):
            descs = _company_descriptions(data)
            qv = self.embedding_model.embed_query(user_query)
            dvs = self.embedding_model.embed_documents(descs)
            sims = cosine_similarity([qv], dvs)[0]
            idx = int(np.argmax(sims))
            c = data[idx]
            return {
                "company_name": c["company_name"],
                "product_name": c["product_name"],
                "index": c.get("index"),
                "sourcetype": c.get("sourcetype"),
                "data_model": c.get("data_model", []),
                "confidence_score": float(sims[idx]),
                "method": "semantic_matching",
                "company_index": idx
            }

        # Orchestrate selection similar to notebook
        try:
            dyn = _dynamic_keyword_company_matching(user_query, self.company_data)
            if dyn.get("method") in ["company_name_direct_match", "platform_match"]:
                return dyn
        except Exception:
            dyn = None

        candidates = []
        if dyn:
            candidates.append(dyn)
        try:
            llm_res = _llm_analyze_company_context_advanced(user_query, self.company_data)
            if llm_res.get("explicit_company", False):
                return llm_res
            candidates.append(llm_res)
        except Exception:
            pass
        try:
            sem = _semantic_company_matching(user_query, self.company_data)
            candidates.append(sem)
        except Exception:
            pass

        if not candidates:
            c = self.company_data[0]
            return {
                "company_name": c["company_name"],
                "product_name": c["product_name"],
                "index": c.get("index"),
                "sourcetype": c.get("sourcetype"),
                "data_model": c.get("data_model", []),
                "confidence_score": 0.3,
                "method": "default_fallback",
                "company_index": 0
            }

        best = max(candidates, key=lambda r: r.get("confidence_score", 0))
        return best
    
    def _generate_unified_spl_query(self, user_query: str, company: Dict[str, Any], extracted_elements: str = "", qa_pairs: List[Dict] = None) -> str:
        """Generate SPL using unified template (from notebook)"""
        template = """You are an expert Splunk SPL query generator. Create a single, correct, efficient query using standard Splunk search syntax.

CRITICAL RULES (Generalized):
1) Use standard index/sourcetype syntax: index=<index> sourcetype=<sourcetype> when those are known or inferable from context; otherwise keep selection broad but relevant (e.g., index=* if truly cross-domain).
2) Select index/sourcetype based on cues in the request (company names, platforms like Windows/Linux, technologies, or data sources mentioned). Do not hardcode any fixed inventory.
3) Include time filters when implied or requested (e.g., earliest=-24h, -72h, -7d, @d). Use bucketing (bin/timechart) for time trends.
4) Prefer precise conditions when available (e.g., EventCode for Windows) and use textual matches as fallback when codes/fields are unknown.
5) Normalize commonly variable fields with coalesce patterns if applicable (keep general):
   - user := coalesce(User_Name, user, account, dest_user)
   - src  := coalesce(Source_Network_Address, src_ip, src, host)
   - path := coalesce(ImagePath, Service_File_Name)
6) Keep queries efficient and readable:
   - Use where/isnotnull to filter nulls.
   - Use stats/eventstats/timechart appropriately.
   - Avoid unnecessary append when schemas differ; consider eventstats/join only with clear join keys.
7) Output SPL only (no explanation).

HARD CONSTRAINTS (Must follow exactly):
- You MUST use the provided company context below. Do not switch companies or indices.
- Use index={index} exactly (do not substitute another index). If {index} is missing, stop and ask for company/index.
- If sourcetype is specified (not *), use sourcetype={sourcetype}. If {sourcetype} is *, infer a plausible sourcetype from the platform (e.g., linux: linux_secure/syslog; windows: WinEventLog).
- Do NOT invent or use other company names, indices, or sourcetypes not consistent with the context.

COMPANY IDENTIFICATION (Flexible):
- If a company/system is mentioned, map it to a plausible index naming pattern (e.g., <Company>_<platform>) only if the context or provided examples justify it.
- If not mentioned or unclear, choose a reasonable generic scope without making unsupported assumptions.

QUERY ANALYSIS:
- Identify any company/organization/system cues.
- Determine the data intent (e.g., authentication, change/config, service, IDS-like, performance).
- Build the search with appropriate index/sourcetype scope, time bounds, filters, and grouping.
- Use appropriate search commands and statistical functions.
- Apply normalization (coalesce) and grouping (stats/timechart/table) as needed.

CONTEXT:
- Company: {company_name} ({product_name})
- Base Index: {index} (use appropriately based on query context)
- Sourcetype: {sourcetype}

USER REQUEST: {query}

EXTRACTED ELEMENTS:
{extracted_elements}

RELEVANT QA EXAMPLES (study patterns; do not copy blindly):
{qa_examples}

GENERATE SPL (single query; standard format when known):
"""
        
        # Get the most relevant QA examples for this query
        qa_examples = ""
        if qa_pairs:
            relevant_examples = self._get_most_relevant_qa_examples(user_query, qa_pairs, k=3)
            qa_examples = "\n\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in relevant_examples])
        
        ctx = {
            "company_name": company.get('company_name', 'Unknown'),
            "product_name": company.get('product_name', 'Unknown'),
            "index": company.get('index', 'main'),
            "sourcetype": company.get('sourcetype', '*'),
            "query": user_query,
            "extracted_elements": extracted_elements or 'Use standard index and sourcetype search with appropriate time filters and field filtering',
            "qa_examples": qa_examples or 'No similar examples available.'
        }
        
        prompt = template.format(**ctx)
        spl_output = self.call_model(prompt)
        
        # Clean up output if wrapped in code blocks
        if "```" in spl_output:
            m = re.search(r"```(?:spl)?\s*(.*?)\s*```", spl_output, re.S)
            if m:
                spl_output = m.group(1).strip()
        
        return spl_output
