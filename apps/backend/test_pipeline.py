#!/usr/bin/env python3
"""
Test script to demonstrate Splunk Relevance Detection + Prompt Fixer pipeline
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__)))

from app.services.chat_service import ChatService
from app.services.spl_service import SPLService
import asyncio

def test_relevance_detection():
    """Test Splunk relevance detection with various queries"""
    print("🔍 Testing Splunk Relevance Detection Pipeline")
    print("=" * 60)
    
    # Initialize services
    spl_service = SPLService()
    
    test_queries = [
        # Clearly Splunk-related queries
        "Show failed login attempts in the last 24 hours",
        "Find authentication events with EventCode 4625", 
        "index=security sourcetype=wineventlog failed login",
        
        # Security queries that should be detected
        "Monitor SSH connections from external IPs",
        "Detect suspicious user account activities", 
        "Show system changes in Windows registry",
        "Find brute force login attacks",
        
        # Borderline queries
        "Generate a report of network traffic",
        "Find errors in application logs",
        "Show me login problems for HealthPlus",
        
        # Non-Splunk queries
        "What is the weather today?",
        "How to cook pasta?",
        "Explain machine learning algorithms"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{i}. Query: {query}")
        
        # Test relevance detection
        is_related, confidence, method = spl_service.is_splunk_related(query)
        status = "✅ Splunk-related" if is_related else "❌ Not Splunk-related"
        print(f"   Detection: {status}")
        print(f"   Confidence: {confidence:.3f}")
        print(f"   Method: {method}")
        
        # Test prompt fixing for Splunk-related queries
        if is_related:
            try:
                improved = spl_service.prompt_fixer(query)
                if improved != query:
                    print(f"   Original:  {query}")
                    print(f"   Improved:  {improved}")
                else:
                    print(f"   Prompt:    No changes needed")
            except Exception as e:
                print(f"   Prompt Fix: Error - {e}")

async def test_full_chat_pipeline():
    """Test the full chat service pipeline"""
    print("\n\n🚀 Testing Full Chat Service Pipeline")
    print("=" * 60)
    
    chat_service = ChatService()
    
    # Get pipeline status
    status = chat_service.get_pipeline_status()
    print(f"Pipeline Status:")
    print(f"  - SPL Service: {'✅' if status['spl_service_available'] else '❌'}")
    print(f"  - Groq Client: {'✅' if status['groq_client_available'] else '❌'}")
    print(f"  - Features: {list(status['features'].keys())}")
    
    # Test with sample queries
    test_queries = [
        "Show failed login attempts for HealthPlus in the last 24 hours",
        "What is artificial intelligence?",  # Non-Splunk query
        "Find suspicious service account activity on Windows servers"
    ]
    
    for query in test_queries:
        print(f"\n📝 Testing: {query}")
        try:
            response = await chat_service.process_message(query)
            print(f"Response length: {len(response)} characters")
            if "SPL Query Generated" in response:
                print("✅ SPL query was generated")
            elif "Not identified as Splunk-related" in response:
                print("❌ Query not identified as Splunk-related")
            else:
                print("💬 General chat response provided")
        except Exception as e:
            print(f"❌ Error: {e}")

def test_spl_generation():
    """Test direct SPL generation"""
    print("\n\n📊 Testing SPL Generation")
    print("=" * 60)
    
    spl_service = SPLService()
    
    test_queries = [
        "Show failed login attempts for HealthPlus in the last 24 hours",
        "Find new services installed on TechNova Windows systems today",
        "Monitor authentication failures across all companies"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        result = spl_service.generate_spl_query(query, verbose=True)
        
        if result.success:
            print(f"✅ Success!")
            print(f"   Company: {result.company}")
            print(f"   Confidence: {result.confidence:.1%}")
            print(f"   SPL: {result.spl_query[:100]}..." if len(result.spl_query) > 100 else f"   SPL: {result.spl_query}")
        else:
            print(f"❌ Failed: {result.error}")

if __name__ == "__main__":
    print("🎯 Splunk Processing Pipeline Test Suite")
    print("Testing Relevance Detection + Prompt Fixer + SPL Generation")
    print("=" * 80)
    
    # Test 1: Relevance Detection
    test_relevance_detection()
    
    # Test 2: Full Pipeline  
    asyncio.run(test_full_chat_pipeline())
    
    # Test 3: Direct SPL Generation
    test_spl_generation()
    
    print("\n" + "=" * 80)
    print("✅ Pipeline testing completed!")
