#!/usr/bin/env python3
"""
Test Script for SPL Service - Multiple Query Examples
Testing improved company selection and index format validation
"""

import sys
import os
sys.path.append('./apps/backend')

# Test cases to validate the improved SPL service
TEST_QUERIES = [
    # Single Company - Windows Queries
    {
        "query": "For TechNova, identify systems with disabled Windows Defender in the last week",
        "expected_index": "TechNova_win",
        "expected_sourcetype": "WinEventLog",
        "description": "Windows Defender query for specific company"
    },
    {
        "query": "For HealthPlus, show all successful logins in the last 24 hours", 
        "expected_index": "HealthPlus_win",
        "expected_sourcetype": "WinEventLog",
        "description": "Successful login query for specific company"
    },
    {
        "query": "For SafeBank, find failed login attempts from the past day",
        "expected_index": "SafeBank_win", 
        "expected_sourcetype": "WinEventLog",
        "description": "Failed login query for banking company"
    },
    {
        "query": "For FinServe, show PowerShell executions in the last hour",
        "expected_index": "FinServe_win",
        "expected_sourcetype": "WinEventLog", 
        "description": "PowerShell monitoring for financial services"
    },
    
    # Single Company - Linux Queries
    {
        "query": "For GreenEnergy, show Linux sudo authentication attempts in the last 24 hours",
        "expected_index": "GreenEnergy_linux",
        "expected_sourcetype": "linux_secure",
        "description": "Linux sudo query for energy company"
    },
    {
        "query": "For EduSmart, monitor SSH login attempts on Linux systems today",
        "expected_index": "EduSmart_linux", 
        "expected_sourcetype": "linux_secure",
        "description": "SSH monitoring for education company"
    },
    
    # Cross-Company Queries
    {
        "query": "Show the top 10 source IPs generating failed login attempts across all companies in the last hour",
        "expected_index": "*",
        "expected_sourcetype": "multiple", 
        "description": "Cross-company failed login analysis"
    },
    {
        "query": "Find privilege escalation attempts across all organizations in the past 24 hours",
        "expected_index": "*",
        "expected_sourcetype": "multiple",
        "description": "Enterprise-wide privilege escalation detection"
    },
    {
        "query": "Compare authentication success rates across all companies for the last 7 days", 
        "expected_index": "*",
        "expected_sourcetype": "multiple",
        "description": "Cross-company authentication analysis"
    },
    
    # Ambiguous Queries (should default appropriately)
    {
        "query": "Show recent registry changes on Windows systems",
        "expected_index": "should_pick_default_company_win",
        "expected_sourcetype": "WinEventLog",
        "description": "Generic Windows query without company specification"
    },
    {
        "query": "Monitor file permission changes on Linux servers",
        "expected_index": "should_pick_default_company_linux", 
        "expected_sourcetype": "linux_secure",
        "description": "Generic Linux query without company specification"
    }
]

def test_spl_service():
    """Test the SPL service with various query types"""
    try:
        from app.services.spl_service import SPLService
        service = SPLService()
        print("🔧 SPL Service initialized successfully!")
        print("=" * 80)
        
        for i, test_case in enumerate(TEST_QUERIES, 1):
            query = test_case["query"]
            expected_index = test_case["expected_index"]
            description = test_case["description"]
            
            print(f"\n📋 Test {i}: {description}")
            print(f"🔍 Query: {query}")
            print("-" * 60)
            
            # Test company selection
            try:
                company_result = service._pick_best_company(query)
                selected_index = company_result.get('index', 'unknown')
                selected_sourcetype = company_result.get('sourcetype', 'unknown')
                confidence = company_result.get('confidence_score', 0)
                method = company_result.get('method', 'unknown')
                
                print(f"🎯 Selected Index: {selected_index}")
                print(f"🔗 Sourcetype: {selected_sourcetype}")
                print(f"📊 Confidence: {confidence:.3f}")
                print(f"🔍 Method: {method}")
                
                # Validate result
                if expected_index == "*" and selected_index == "*":
                    print("✅ PASS: Correctly identified cross-company query")
                elif expected_index.startswith("should_pick_default"):
                    if "_win" in selected_index or "_linux" in selected_index:
                        print("✅ PASS: Selected appropriate default company")
                    else:
                        print("❌ FAIL: Should have selected a specific company")
                elif selected_index == expected_index:
                    print("✅ PASS: Perfect index match")
                else:
                    print(f"❌ FAIL: Expected {expected_index}, got {selected_index}")
                
            except Exception as e:
                print(f"❌ ERROR in company selection: {e}")
            
            # Test full SPL generation
            try:
                spl_result = service.generate_spl_query(query)
                if spl_result.success:
                    spl_query = spl_result.spl_query
                    print(f"\n📝 Generated SPL:")
                    print(f"   {spl_query.split(chr(10))[0]}")  # First line only
                    
                    # Basic validation
                    if expected_index == "*" and "index=*" in spl_query:
                        print("✅ Cross-company SPL format correct")
                    elif expected_index != "*" and f"index={expected_index}" in spl_query:
                        print("✅ Single-company SPL format correct")
                    elif expected_index.startswith("should_pick_default"):
                        if "index=" in spl_query and ("_win" in spl_query or "_linux" in spl_query):
                            print("✅ Default company SPL format correct")
                        else:
                            print("❌ Default company SPL format incorrect")
                    else:
                        print("❌ SPL index format incorrect")
                else:
                    print(f"❌ SPL generation failed: {spl_result.error}")
                    
            except Exception as e:
                print(f"❌ ERROR in SPL generation: {e}")
                
        print("\n" + "=" * 80)
        print("🏁 Testing completed!")
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're in the correct directory and dependencies are installed")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

def test_platform_detection():
    """Test the new LLM-based platform detection"""
    print("\n🧪 Testing Platform Detection...")
    print("-" * 40)
    
    platform_test_cases = [
        ("Windows Defender is disabled", "windows"),
        ("Check PowerShell execution logs", "windows"),
        ("Monitor registry changes", "windows"),
        ("Show sudo authentication attempts", "linux"),
        ("Check /etc/passwd modifications", "linux"),
        ("Analyze SSH login patterns", "linux"),
        ("Show system authentication events", "mixed/unknown")
    ]
    
    try:
        from app.services.spl_service import SPLService
        service = SPLService()
        
        for query, expected_platform in platform_test_cases:
            print(f"\n🔍 Query: {query}")
            try:
                company_result = service._pick_best_company(query)
                selected_index = company_result.get('index', 'unknown')
                
                if 'win' in selected_index:
                    detected_platform = "windows"
                elif 'linux' in selected_index:
                    detected_platform = "linux"
                else:
                    detected_platform = "unknown"
                
                print(f"📊 Expected: {expected_platform}, Detected: {detected_platform}")
                
                if expected_platform == detected_platform:
                    print("✅ Platform detection correct")
                elif expected_platform == "mixed/unknown":
                    print("ℹ️ Mixed/unknown case - any result acceptable")
                else:
                    print("❌ Platform detection incorrect")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                
    except Exception as e:
        print(f"❌ Platform detection test failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting SPL Service Testing...")
    test_spl_service()
    test_platform_detection()
    print("\n✨ All tests completed!")
