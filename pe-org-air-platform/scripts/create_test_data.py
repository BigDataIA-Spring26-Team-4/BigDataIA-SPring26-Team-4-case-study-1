"""
Create sample companies for testing.

Uses PDF-compliant field names and generates diverse test data.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.services.snowflake import SessionLocal
from app.models.company import CompanyCreate
from app.services import snowflake


def create_test_companies():
    """Create 10 test companies for pagination and testing."""
    
    print("=" * 70)
    print("Creating Test Companies (PDF-Compliant)")
    print("=" * 70)
    
    # Test companies with position_factor (PDF field name)
    companies = [
        {
            "name": "Acme Manufacturing Corp",
            "ticker": "ACME",
            "industry_id": "550e8400-e29b-41d4-a716-446655440001",  # Manufacturing
            "position_factor": 0.5
        },
        {
            "name": "TechVision Solutions",
            "ticker": "TECH",
            "industry_id": "550e8400-e29b-41d4-a716-446655440003",  # Business Services
            "position_factor": 0.7
        },
        {
            "name": "HealthFirst Medical Group",
            "ticker": "HFM",
            "industry_id": "550e8400-e29b-41d4-a716-446655440002",  # Healthcare
            "position_factor": 0.6
        },
        {
            "name": "Global Retail Partners",
            "ticker": "GRP",
            "industry_id": "550e8400-e29b-41d4-a716-446655440004",  # Retail
            "position_factor": 0.4
        },
        {
            "name": "FinTech Innovations Inc",
            "ticker": "FTI",
            "industry_id": "550e8400-e29b-41d4-a716-446655440005",  # Financial
            "position_factor": 0.8
        },
        {
            "name": "Smart Manufacturing Co",
            "ticker": "SMC",
            "industry_id": "550e8400-e29b-41d4-a716-446655440001",  # Manufacturing
            "position_factor": 0.3
        },
        {
            "name": "CloudOps Services",
            "ticker": "COS",
            "industry_id": "550e8400-e29b-41d4-a716-446655440003",  # Business Services
            "position_factor": 0.9
        },
        {
            "name": "MediCare Plus",
            "ticker": "MCP",
            "industry_id": "550e8400-e29b-41d4-a716-446655440002",  # Healthcare
            "position_factor": 0.5
        },
        {
            "name": "E-Commerce Giants",
            "ticker": "ECG",
            "industry_id": "550e8400-e29b-41d4-a716-446655440004",  # Retail
            "position_factor": 0.7
        },
        {
            "name": "Investment Pro Partners",
            "ticker": "IPP",
            "industry_id": "550e8400-e29b-41d4-a716-446655440005",  # Financial
            "position_factor": 0.6
        }
    ]
    
    db = SessionLocal()
    created = []
    
    try:
        for i, company_data in enumerate(companies, 1):
            print(f"\n{i}. Creating: {company_data['name']} ({company_data['ticker']})")
            
            company = CompanyCreate(**company_data)
            result = snowflake.create_company(db, company)
            created.append(result)
            
            print(f"   ✅ Created with ID: {result.id}")
        
        print("\n" + "=" * 70)
        print(f"✅ Successfully created {len(created)} companies!")
        print("=" * 70)
        
        print("\n📊 Created Companies:")
        for company in created:
            print(f"   • {company.name:30s} ({company.ticker:5s}) - ID: {company.id}")
        
        print("\n🎯 Ready to test pagination!")
        print("   Try these in Swagger (GET /api/v1/companies):")
        print("   1. skip=0, limit=3  → First 3 companies")
        print("   2. skip=3, limit=3  → Next 3 companies")
        print("   3. skip=6, limit=3  → Next 3 companies")
        print("   4. skip=0, limit=10 → All 10 companies")
        
    except Exception as e:
        print(f"\n❌ Error creating companies: {str(e)}")
        return False
    finally:
        db.close()
    
    return True


if __name__ == "__main__":
    success = create_test_companies()
    sys.exit(0 if success else 1)
