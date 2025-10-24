"""
Example script demonstrating TrueMesh Provider Intelligence API usage
"""
import requests
import json
from datetime import datetime

# Base URL - update if running on different host/port
BASE_URL = "http://localhost:8000/api/v1"

def print_section(title):
    """Print section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_response(response):
    """Print formatted response"""
    print(f"\nStatus: {response.status_code}")
    try:
        data = response.json()
        print(json.dumps(data, indent=2))
    except:
        print(response.text)

def main():
    """Demonstrate TrueMesh API usage"""
    
    print_section("TrueMesh Provider Intelligence - API Demo")
    
    # 1. Check system health
    print_section("1. System Health Check")
    response = requests.get(f"{BASE_URL.replace('/api/v1', '')}/health")
    print_response(response)
    
    # 2. Get system overview
    print_section("2. System Overview")
    response = requests.get(f"{BASE_URL}/admin/stats/overview")
    print_response(response)
    
    # 3. Create a new provider
    print_section("3. Create New Provider")
    provider_data = {
        "registration_number": "MCI123456",
        "name": "Dr. Amit Sharma",
        "provider_type": "doctor",
        "specialization": "Cardiology",
        "email": "amit.sharma@example.com",
        "phone": "+919876543210",
        "address_line1": "123 Medical Street",
        "city": "Mumbai",
        "state": "Maharashtra",
        "postal_code": "400001",
        "country": "India"
    }
    response = requests.post(f"{BASE_URL}/providers/", json=provider_data)
    print_response(response)
    
    if response.status_code == 200:
        workflow_data = response.json()
        workflow_id = workflow_data.get("workflow_id")
        print(f"\n✓ Provider registration workflow initiated: {workflow_id}")
    
    # 4. Verify provider data
    print_section("4. Verify Provider Data")
    verification_request = {
        "provider_id": "sample-provider-id",
        "verification_type": "full"
    }
    response = requests.post(f"{BASE_URL}/verification/", json=verification_request)
    print_response(response)
    
    # 5. Run fraud check
    print_section("5. Fraud Detection Check")
    response = requests.post(f"{BASE_URL}/verification/sample-provider-id/fraud-check")
    print_response(response)
    
    # 6. Calculate confidence score
    print_section("6. Calculate Confidence Score")
    response = requests.post(f"{BASE_URL}/verification/sample-provider-id/confidence-score")
    print_response(response)
    
    # 7. Run compliance check
    print_section("7. Compliance Check")
    response = requests.post(f"{BASE_URL}/verification/sample-provider-id/compliance-check")
    print_response(response)
    
    # 8. Submit provider update via PITL
    print_section("8. Provider-Initiated Update (PITL)")
    update_request = {
        "provider_id": "sample-provider-id",
        "updates": {
            "email": "new.email@example.com",
            "phone": "+919999999999"
        }
    }
    response = requests.post(f"{BASE_URL}/pitl/update", json=update_request)
    print_response(response)
    
    # 9. Submit challenge
    print_section("9. Submit Provider Challenge")
    challenge_request = {
        "provider_id": "sample-provider-id",
        "challenge_data": {
            "field": "specialization",
            "current_value": "General Medicine",
            "correct_value": "Cardiology"
        },
        "challenge_reason": "My specialization was incorrectly recorded during registration"
    }
    response = requests.post(f"{BASE_URL}/pitl/challenge", json=challenge_request)
    print_response(response)
    
    # 10. Get blockchain info
    print_section("10. Provenance Blockchain Information")
    response = requests.get(f"{BASE_URL}/admin/provenance/chain-info")
    print_response(response)
    
    # 11. Get agent status
    print_section("11. Agent Status")
    response = requests.get(f"{BASE_URL}/admin/agents/status")
    print_response(response)
    
    # 12. Get federation status
    print_section("12. Federation Network Status")
    response = requests.get(f"{BASE_URL}/federation/status")
    print_response(response)
    
    # Summary
    print_section("Demo Complete!")
    print("\n✅ TrueMesh Provider Intelligence API demonstration complete!")
    print("\n📚 For more information:")
    print("  - API Documentation: http://localhost:8000/docs")
    print("  - README: See README.md in the repository")
    print("  - Source Code: https://github.com/harshith-varma07/TrueMesh")
    print("=" * 70)

if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to TrueMesh API")
        print("   Make sure the application is running:")
        print("   docker-compose up -d")
        print("   OR")
        print("   python main.py")
    except Exception as e:
        print(f"\n❌ Error: {e}")
