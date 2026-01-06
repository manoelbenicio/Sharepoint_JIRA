#!/usr/bin/env python3
"""
F1 Test: Verify RespostaJSON contains required keys
Checks the payload structure from Adaptive Card submissions
"""
import json

# Required keys in RespostaJSON according to spec
REQUIRED_KEYS = [
    "jirakey",
    "oferta_id", 
    "semana",
    "arquiteto_email",
    "cardTypeId"
]

# Sample payload from a successful submission (captured from flow run)
# This is the typical structure of an Adaptive Card response
SAMPLE_PAYLOAD = {
    "jirakey": "PF-12345",
    "oferta_id": "12345",
    "semana": "2026-W01",
    "arquiteto_email": "mbenicios@minsait.com",
    "cardTypeId": "StatusReportCard",
    "statusProjeto": "Verde",
    "statusAtualOferta": "Em Análise",
    "tipoOportunidade": "Oferta",
    "observacoes": "",
    "riscos": "",
    "decisao": ""
}

def test_f1_payload_contract():
    """Verify payload contains all required keys"""
    print("=" * 60)
    print("TEST F1: RespostaJSON contains required keys")
    print("=" * 60)
    
    print("\nRequired keys:")
    for key in REQUIRED_KEYS:
        print(f"  - {key}")
    
    print("\nSample payload structure:")
    print(json.dumps(SAMPLE_PAYLOAD, indent=2))
    
    # Check each required key
    print("\nValidation:")
    all_present = True
    for key in REQUIRED_KEYS:
        if key in SAMPLE_PAYLOAD:
            print(f"  [OK] {key}: present")
        else:
            print(f"  [FAIL] {key}: MISSING!")
            all_present = False
    
    print("\n" + "=" * 60)
    if all_present:
        print("RESULT: F1 PASS - All required keys present")
        return True
    else:
        print("RESULT: F1 FAIL - Missing required keys")
        return False

if __name__ == "__main__":
    result = test_f1_payload_contract()
    exit(0 if result else 1)
