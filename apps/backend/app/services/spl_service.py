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
        
        # Fix common SPL syntax issues
        result = result.strip()
        
        # Replace 'limit' with 'head' (Splunk best practice)
        result = re.sub(r'\|\s*limit\s+(\d+)', r'| head \1', result, flags=re.IGNORECASE)
        
        return result
    
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
- Grouping/sorting/head patterns (stats by <fields>, sort - <field>, head N - NEVER use limit).
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
- Grouping/Sorting/Head Commands
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
            query_lower = user_query.lower()
            words = re.findall(r"\b\w+\b", query_lower)
            words = [w for w in words if len(w) > 2]
            
            # Intelligent platform detection using LLM
            def _detect_platform_context(query_text):
                """Use LLM to intelligently detect platform context"""
                platform_prompt = f"""Analyze this query to determine the target platform/technology:

Query: "{query_text}"

Consider these factors:
- Specific tools/applications mentioned (Windows Defender, PowerShell, sudo, systemctl, etc.)
- File paths and system directories (C:\\, /etc/, /var/, etc.)
- Log sources and event types (EventCode, syslog, WinEventLog, etc.)
- Administrative commands and processes
- Operating system context clues

Return JSON only:
{{
    "primary_platform": "windows|linux|mixed|unknown",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation",
    "technology_indicators": ["list", "of", "key", "indicators"]
}}"""
                
                try:
                    response = self.call_model(platform_prompt, temperature=0.1)
                    json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
                    if json_match:
                        result = json.loads(json_match.group(0))
                        return {
                            "platform": result.get("primary_platform", "unknown"),
                            "confidence": float(result.get("confidence", 0.5)),
                            "reasoning": result.get("reasoning", ""),
                            "indicators": result.get("technology_indicators", [])
                        }
                except Exception as e:
                    print(f"LLM platform detection error: {e}")
                
                # Fallback to basic keyword detection
                query_lower = query_text.lower()
                windows_signals = ['defender', 'powershell', 'registry', 'eventcode', 'c:\\']
                linux_signals = ['sudo', '/etc/', '/var/', 'systemctl', 'bash']
                
                win_score = sum(1 for signal in windows_signals if signal in query_lower)
                linux_score = sum(1 for signal in linux_signals if signal in query_lower)
                
                if win_score > linux_score:
                    return {"platform": "windows", "confidence": 0.7, "reasoning": "Basic keyword fallback", "indicators": []}
                elif linux_score > win_score:
                    return {"platform": "linux", "confidence": 0.7, "reasoning": "Basic keyword fallback", "indicators": []}
                else:
                    return {"platform": "unknown", "confidence": 0.3, "reasoning": "No clear platform indicators", "indicators": []}
            
            # Detect platform context
            platform_context = _detect_platform_context(user_query)
            has_windows_context = platform_context["platform"] == "windows"
            has_linux_context = platform_context["platform"] == "linux"
            
            best_matches = []
            scores = []

            for i, c in enumerate(data):
                company_name_lower = c['company_name'].lower()
                product_lower = c.get('product_name', '').lower()
                
                # Direct company match (highest priority)
                if company_name_lower in query_lower:
                    confidence = 0.95
                    match_reason = f"Direct mention of {c['company_name']}"
                    
                    # Platform-specific match gets higher confidence
                    if has_linux_context and 'linux' in product_lower:
                        confidence = 0.98
                        match_reason = f"Direct {c['company_name']} + Linux context"
                    elif has_windows_context and 'win' in product_lower:
                        confidence = 0.98
                        match_reason = f"Direct {c['company_name']} + Windows context"
                    elif not has_linux_context and 'win' in product_lower:
                        # Default to Windows if no explicit Linux context
                        confidence = 0.96
                        match_reason = f"Direct {c['company_name']} (default Windows)"
                    
                    best_matches.append({
                        "company_name": c["company_name"],
                        "product_name": c["product_name"],
                        "index": c.get("index"),
                        "sourcetype": c.get("sourcetype"),
                        "data_model": c.get("data_model", []),
                        "confidence_score": confidence,
                        "method": "company_name_direct_match",
                        "explicit_company": True,
                        "match_reason": match_reason,
                        "company_index": i
                    })

                # Context keyword scoring for fallback
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
            
            # Return best direct match if found
            if best_matches:
                best_match = max(best_matches, key=lambda x: x['confidence_score'])
                return best_match

            # Fallback to keyword scoring
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
            
            # Ultimate fallback
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

        # Orchestrate selection with proper priority order
        # 1. First check for EXPLICIT company mentions (highest priority)
        try:
            dyn = _dynamic_keyword_company_matching(user_query, self.company_data)
            if dyn.get("method") in ["company_name_direct_match", "platform_match"]:
                print(f"🎯 Direct company match found: {dyn['company_name']} (confidence: {dyn['confidence_score']})")
                return dyn
        except Exception as e:
            print(f"Dynamic matching error: {e}")
            dyn = None

        # 2. Then check for cross-company patterns (only if no specific company found)
        cross_company_result = self._detect_cross_company_queries(user_query)
        if cross_company_result:
            print(f"🌐 Cross-company query detected (confidence: {cross_company_result['confidence_score']})")
            return cross_company_result

        # 2.5. Check for generic queries that might benefit from cross-company analysis
        generic_result = self._detect_generic_queries(user_query)
        if generic_result:
            print(f"📊 Generic query detected - suggesting cross-company analysis")
            return generic_result

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
    
    def _detect_cross_company_queries(self, user_query: str) -> Optional[Dict[str, Any]]:
        """LLM-based detection for cross-company queries that should use index=*"""
        
        system_prompt = """You are an expert at detecting cross-company/enterprise-wide queries for Splunk analysis.

CRITICAL: Only classify as cross-company if the query EXPLICITLY requires data from ALL companies/organizations.

EXPLICIT CROSS-COMPANY INDICATORS (must be present):
- Clear mentions: "all companies", "enterprise-wide", "organization-wide", "across all organizations"
- Comparative analysis: "compare across companies", "enterprise trends", "organization-wide patterns"
- Explicit scope: "every company", "entire organization", "targeting all organizations"

SINGLE COMPANY INDICATORS (strong rejection):
- ANY specific company name: "For SafeBank", "TechNova systems", "HealthPlus", "AirLogix", "GreenEnergy", "EduSmart", "FinServe"
- Company-specific context: "At [Company]", "[Company] logs", "[Company] systems"

IMPORTANT RULES:
1. If ANY company name is mentioned → ALWAYS single company (confidence = 0.1)
2. Only return cross-company if confidence >= 0.8 AND no company names present
3. Be very conservative - when in doubt, choose single company

Return ONLY valid JSON:
{
    "is_cross_company": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation of decision"
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Query: {user_query}"}
        ]
        
        try:
            response = self.call_model(messages, temperature=0.1)
            
            # Extract JSON from response
            json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group(0))
                
                is_cross_company = result.get("is_cross_company", False)
                confidence = float(result.get("confidence", 0.5))
                reasoning = result.get("reasoning", "LLM analysis")
                
                # Extra validation: check for company names in query
                company_names = [c["company_name"] for c in self.company_data]
                has_company_name = any(name.lower() in user_query.lower() for name in company_names)
                
                if has_company_name:
                    print(f"🚫 Company name detected in query, rejecting cross-company classification")
                    return None
                
                # Require high confidence for cross-company detection
                if is_cross_company and confidence >= 0.8:
                    print(f"✅ LLM cross-company detection: confidence={confidence}, reasoning={reasoning}")
                    return {
                        "company_name": "All Companies",
                        "product_name": "Cross-Company Analysis",
                        "index": "*",
                        "sourcetype": None,
                        "data_model": [],
                        "confidence_score": confidence,
                        "method": "llm_cross_company_detection",
                        "company_index": -1,
                        "is_cross_company": True,
                        "reasoning": reasoning
                    }
                else:
                    print(f"❌ LLM rejected cross-company (confidence={confidence}, reasoning={reasoning})")
                    return None
                    
        except Exception as e:
            print(f"LLM cross-company detection error: {e}")
            
        # Fallback to simple pattern matching if LLM fails
        q = user_query.lower()
        
        # Only the most obvious patterns as fallback
        obvious_patterns = [
            "all companies", "all organizations", "enterprise-wide", "organization-wide",
            "across all companies", "across all organizations", "targeting all organizations"
        ]
        
        if any(pattern in q for pattern in obvious_patterns):
            return {
                "company_name": "All Companies",
                "product_name": "Cross-Company Analysis",
                "index": "*",
                "sourcetype": None,
                "data_model": [],
                "confidence_score": 0.90,
                "method": "fallback_pattern_detection",
                "company_index": -1,
                "is_cross_company": True,
                "reasoning": "Fallback pattern matching"
            }
        
        return None
    
    def _detect_generic_queries(self, user_query: str) -> Optional[Dict[str, Any]]:
        """Detect generic queries that don't specify a company but could benefit from cross-company analysis"""
        
        # Generic patterns that often need cross-company analysis
        generic_patterns = [
            r"monitor\s+.*\s+(on|across|from)\s+.*servers?",  # "Monitor X on servers"
            r"show\s+.*\s+(login|authentication|access)\s+attempts?",  # "Show login attempts"  
            r"find\s+.*\s+(suspicious|malicious|unusual)\s+",  # "Find suspicious activity"
            r"detect\s+.*\s+(attack|intrusion|threat)",  # "Detect attacks"
            r"analyze\s+.*\s+(patterns?|trends?|behavior)",  # "Analyze patterns"
            r"track\s+.*\s+(changes?|modifications?)",  # "Track changes"
            r"identify\s+.*\s+(systems?|hosts?|users?)\s+with",  # "Identify systems with"
        ]
        
        query_lower = user_query.lower()
        
        # Check if query matches generic patterns AND doesn't mention specific company
        company_names = [c["company_name"].lower() for c in self.company_data]
        has_company_mention = any(f"for {company}" in query_lower for company in company_names)
        
        if has_company_mention:
            return None  # Has specific company mention
        
        # Check for generic patterns
        is_generic = any(re.search(pattern, query_lower) for pattern in generic_patterns)
        
        if is_generic:
            # Additional check: does it mention systems/servers in plural (suggesting enterprise scope)?
            enterprise_indicators = ['servers', 'systems', 'hosts', 'machines', 'devices', 'endpoints']
            has_enterprise_scope = any(indicator in query_lower for indicator in enterprise_indicators)
            
            if has_enterprise_scope:
                return {
                    "company_name": "All Companies",
                    "product_name": "Cross-Company Analysis", 
                    "index": "*",
                    "sourcetype": None,
                    "data_model": [],
                    "confidence_score": 0.75,
                    "method": "generic_cross_company_suggestion",
                    "company_index": -1,
                    "is_cross_company": True,
                    "reasoning": "Generic query with enterprise scope - suggesting cross-company analysis"
                }
        
        return None
    
    def _generate_unified_spl_query(self, user_query: str, company: Dict[str, Any], extracted_elements: str = "", qa_pairs: List[Dict] = None) -> str:
        """Generate SPL using unified template with strict index/sourcetype validation"""
        # Enhanced context with cross-company awareness (define early)
        is_cross_company = company.get('is_cross_company', False) or company.get('index') == '*'
        
        # Validate and enforce correct index/sourcetype format
        def _validate_company_context(company_info):
            """Ensure company context follows index-sourcetype.json format"""
            index = company_info.get('index', 'main')
            sourcetype = company_info.get('sourcetype', 'WinEventLog')
            company_name = company_info.get('company_name', 'Default')
            
            # For cross-company queries
            if is_cross_company or index == '*':
                return {
                    'index': '*',
                    'sourcetype_clause': '(sourcetype=WinEventLog OR sourcetype=linux_secure OR sourcetype=syslog OR sourcetype=linux_syslog)',
                    'needs_company_extraction': True
                }
            
            # For single company queries - ensure proper format
            if not index.endswith('_win') and not index.endswith('_linux'):
                # Try to infer from available data
                for company_data in self.company_data:
                    if company_data['company_name'].lower() == company_name.lower():
                        return {
                            'index': company_data['index'],
                            'sourcetype_clause': f'sourcetype={company_data["sourcetype"]}',
                            'needs_company_extraction': False
                        }
                
                # Fallback - assume Windows if no clear indication
                return {
                    'index': f'{company_name}_win',
                    'sourcetype_clause': 'sourcetype=WinEventLog',
                    'needs_company_extraction': False
                }
            
            # Index format is already correct
            return {
                'index': index,
                'sourcetype_clause': f'sourcetype={sourcetype}',
                'needs_company_extraction': False
            }
        
        # Get validated context
        validated_context = _validate_company_context(company)
        
        try:
            template = """You are an expert Splunk SPL query generator. Create a single, correct, efficient query using standard Splunk search syntax.

CRITICAL REQUIREMENTS:
INDEX FORMAT: Must use EXACT format from index-sourcetype.json:
- Single company: index=CompanyName_win or index=CompanyName_linux  
- Cross-company: index=* with multiple sourcetypes

MANDATORY INDEX & SOURCETYPE RULES:
{index_sourcetype_instruction}

FIELD NORMALIZATION STANDARDS:
- user := coalesce(TargetUserName, User_Name, user, account, dest_user)
- src := coalesce(Source_Network_Address, src_ip, src, rhost, host)  
- Windows events: Use EventCode (4624=login success, 4625=login failure, 5001/5025=Defender events)
- Linux events: Use text patterns ("Accepted password", "Failed password", "sudo")

QUERY STRUCTURE:
1. index={target_index} {sourcetype_clause} earliest=<timeframe>
2. Add specific search conditions based on request
3. Apply field normalization with eval/coalesce  
{company_extraction}4. Use appropriate aggregations (stats, timechart, etc.)
5. Sort results and use 'head' command for limiting (NEVER use 'limit')

Company Context: {company_name}
User Request: {query}

Generate ONLY the SPL query (no explanations). Use 'head' command instead of 'limit' for result limiting:"""

            # Determine instruction based on context
            if validated_context['needs_company_extraction']:
                index_instruction = "Cross-company query: MUST use index=* (sourcetype=WinEventLog OR sourcetype=linux_secure OR sourcetype=syslog OR sourcetype=linux_syslog)"
                company_extraction = "3. Extract company with: rex field=index \"(?<company>\\w+)_\"\n"
            else:
                index_instruction = f"Single company query: MUST use exact index format: {validated_context['index']} {validated_context['sourcetype_clause']}"
                company_extraction = "3. No company extraction needed\n"
            
            # Enhanced QA example selection with validation
            qa_examples = ""
            if qa_pairs:
                if is_cross_company:
                    # Get cross-company examples that use index=*
                    cross_company_examples = [
                        qa for qa in qa_pairs 
                        if isinstance(qa, dict) and qa.get("answer", "").startswith("index=*")
                    ]
                    if cross_company_examples:
                        relevant_examples = self._get_most_relevant_qa_examples(user_query, cross_company_examples, k=2)
                    else:
                        relevant_examples = self._get_most_relevant_qa_examples(user_query, qa_pairs, k=2)
                else:
                    # Get single company examples with proper index format
                    company_name = company.get('company_name', '')
                    company_examples = [
                        qa for qa in qa_pairs 
                        if isinstance(qa, dict) and 
                        qa.get("question", "").lower().startswith(f"for {company_name.lower()}") and
                        (f"index={company_name}_win" in qa.get("answer", "") or f"index={company_name}_linux" in qa.get("answer", ""))
                    ]
                    if company_examples:
                        relevant_examples = self._get_most_relevant_qa_examples(user_query, company_examples, k=2)
                    else:
                        relevant_examples = self._get_most_relevant_qa_examples(user_query, qa_pairs, k=2)
                
                qa_examples = "\n\nRELEVANT EXAMPLES:\n" + "\n".join([f"Q: {qa['question']}\nA: {qa['answer']}" for qa in relevant_examples])
            
            prompt = template.format(
                index_sourcetype_instruction=index_instruction,
                target_index=validated_context['index'],
                sourcetype_clause=validated_context['sourcetype_clause'],
                company_extraction=company_extraction,
                company_name=company.get('company_name', 'Unknown'),
                query=user_query
            ) + qa_examples
            
            spl_output = self.call_model(prompt, temperature=0.1)
            
            # Clean up output if wrapped in code blocks
            if "```" in spl_output:
                m = re.search(r"```(?:spl|splunk)?\s*(.*?)\s*```", spl_output, re.S)
                if m:
                    spl_output = m.group(1).strip()
            
            # Final validation - ensure correct index format
            lines = spl_output.split('\n')
            first_line = lines[0].strip()
            
            if not is_cross_company and not first_line.startswith(f'index={validated_context["index"]}'):
                # Force correct index format
                if '|' in first_line:
                    search_part, pipe_part = first_line.split('|', 1)
                    corrected_line = f'index={validated_context["index"]} {validated_context["sourcetype_clause"]} {search_part.split("earliest=")[-1] if "earliest=" in search_part else "earliest=-24h"}'
                    spl_output = corrected_line + '\n| ' + pipe_part + '\n' + '\n'.join(lines[1:])
                else:
                    corrected_line = f'index={validated_context["index"]} {validated_context["sourcetype_clause"]} ' + first_line.replace('index=*', '').replace('index=', '').strip()
                    spl_output = corrected_line + '\n' + '\n'.join(lines[1:])
            
            return spl_output.strip()
            
        except Exception as e:
            print(f"Error in _generate_unified_spl_query: {e}")
            
            # Enhanced fallback with correct index format
            if is_cross_company:
                index_part = "index=* (sourcetype=WinEventLog OR sourcetype=linux_secure OR sourcetype=syslog OR sourcetype=linux_syslog)"
                company_extract = "\n| rex field=index \"(?<company>\\w+)_\""
            else:
                index_part = f'index={validated_context["index"]} {validated_context["sourcetype_clause"]}'
                company_extract = ""
            
            if "failed login" in user_query.lower() or "login fail" in user_query.lower():
                return f"""{index_part} earliest=-24h
| search EventCode=4625 OR match(_raw, "Failed password|authentication failure|logon failure"){company_extract}
| eval user=coalesce(User_Name, user, account, dest_user)
| eval src=coalesce(src_ip, src, Source_Network_Address, host)
| stats count by user src
| sort - count
| head 10"""
            elif "defender" in user_query.lower() and "disable" in user_query.lower():
                return f"""{index_part} earliest=-7d
| search (EventCode=5001 OR EventCode=5025 OR "Defender disabled" OR "protection disabled"){company_extract}
| stats latest(_time) as last_event by host
| convert ctime(last_event) as Time
| sort - last_event"""
            else:
                return f"""{index_part} earliest=-24h{company_extract}
| stats count
| sort - count"""
