"""
Edge testing script for different report types.
Tests queries for WLC, LFP, DATO, and CPI reports to ensure they work correctly.
"""
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.main import query

# Test queries for different report types
test_queries = [
    # WLC (Wireline Logging Composite) reports
    "What information is in the WLC composite report for well 15/9-F-5?",
    "What does the WLC report say about well 15/9-F-7?",
    "Show me the wireline logging composite report for 15/9-F-9",
    "What is in the composite report for well 15/9-F-10?",
    
    # LFP (Low Frequency Permeability) reports
    "What information is in the LFP report for well 15/9-19A?",
    "What does the low frequency permeability report say about 15/9-19BT2?",
    "Show me the LFP report for well 15/9-19SR",
    
    # DATO reports
    "What information is in the DATO report for well 15/9-F-10?",
    "Show me the DATO report for 15/9-F-12",
    
    # CPI (Composite Petrophysical Interpretation) reports
    "What is in the CPI report for well 15/9-F-5?",
    "Show me the composite petrophysical interpretation for 15/9-F-4",
    
    # General queries that should work across report types
    "What reports are available for well 15/9-F-5?",
    "Compare the WLC and petrophysical reports for well 15/9-F-5",
    "What information is available about well 15/9-F-7?",
]

def test_report_type_queries():
    """Test queries for different report types."""
    print("=" * 80)
    print("EDGE TESTING: Different Report Types")
    print("=" * 80)
    print()
    
    results = []
    for i, test_query in enumerate(test_queries, 1):
        print(f"\n{'='*80}")
        print(f"Test {i}/{len(test_queries)}: {test_query}")
        print(f"{'='*80}")
        
        try:
            # Query the system
            response = query(test_query)
            
            # Handle None response
            if response is None:
                response = ""
            
            # Check if response contains relevant information
            response_lower = response.lower() if response else ""
            has_wlc = "wlc" in response_lower or "wireline" in response_lower or "composite" in response_lower
            has_lfp = "lfp" in response_lower or "low frequency" in response_lower or "permeability" in response_lower
            has_dato = "dato" in response_lower
            has_cpi = "cpi" in response_lower or "composite petrophysical interpretation" in response_lower
            has_error = "error" in response_lower or "not found" in response_lower or "no information" in response_lower
            
            # Determine if query was successful
            query_type = test_query.lower()
            if "wlc" in query_type or "wireline" in query_type or "composite" in query_type:
                success = has_wlc and not has_error
            elif "lfp" in query_type or "low frequency" in query_type:
                success = has_lfp and not has_error
            elif "dato" in query_type:
                success = has_dato and not has_error
            elif "cpi" in query_type:
                success = has_cpi and not has_error
            else:
                # General query - just check it doesn't error
                success = not has_error
            
            status = "[PASS]" if success else "[FAIL]"
            print(f"\n{status}")
            print(f"Response length: {len(response)} chars")
            print(f"Response preview: {response[:200] if response else 'None'}...")
            
            results.append({
                "query": test_query,
                "status": "PASS" if success else "FAIL",
                "response_length": len(response) if response else 0,
                "has_relevant_content": success
            })
            
        except Exception as e:
            print(f"\n[ERROR]: {e}")
            results.append({
                "query": test_query,
                "status": "ERROR",
                "error": str(e)
            })
    
    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    passed = sum(1 for r in results if r.get("status") == "PASS")
    failed = sum(1 for r in results if r.get("status") == "FAIL")
    errors = sum(1 for r in results if r.get("status") == "ERROR")
    
    print(f"Total tests: {len(test_queries)}")
    print(f"[PASS] Passed: {passed}")
    print(f"[FAIL] Failed: {failed}")
    print(f"[ERROR] Errors: {errors}")
    print()
    
    if failed > 0 or errors > 0:
        print("Failed/Error queries:")
        for r in results:
            if r.get("status") in ["FAIL", "ERROR"]:
                print(f"  - {r['query']}")
    
    return results

if __name__ == "__main__":
    test_report_type_queries()

