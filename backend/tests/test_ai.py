import pytest
from app.services.ai.provider import extract_json_from_llm_response, DemoAIService

def test_json_extractor_valid_json():
    raw = '{"name": "Metro Clinic", "score": 85}'
    parsed = extract_json_from_llm_response(raw)
    assert parsed["name"] == "Metro Clinic"
    assert parsed["score"] == 85

def test_json_extractor_markdown_block():
    raw = """
    Here is the requested output:
    ```json
    {
      "analysis": {"business_type": "Dental Clinic"},
      "score": {"score": 90, "category": "High"}
    }
    ```
    Thank you.
    """
    parsed = extract_json_from_llm_response(raw)
    assert parsed["analysis"]["business_type"] == "Dental Clinic"
    assert parsed["score"]["score"] == 90

def test_json_extractor_invalid_raises_error():
    with pytest.raises(ValueError):
        extract_json_from_llm_response("This is not JSON at all")

@pytest.mark.asyncio
async def test_demo_ai_service_analysis():
    service = DemoAIService()
    lead_data = {
        "name": "Beacon Dental Care",
        "business_type": "Dental Clinic",
        "city": "Boston",
        "services": ["Invisalign", "Teeth Whitening", "Implants"],
        "phone": "+1 617-555-0100",
        "description": "Comprehensive cosmetic and restorative dental practice."
    }
    result = await service.analyze_lead(lead_data)
    assert "analysis" in result
    assert result["analysis"]["business_type"] == "Dental Clinic"
    assert "Beacon Dental Care" in result["score"]["reason"] or "Boston" in result["score"]["reason"]
    assert len(result["opportunities"]) <= 3
    assert result["score"]["score"] >= 80
    assert result["score"]["category"] == "High"

def test_lead_analyze_api_endpoint(client):
    # 1. Create a lead
    create_res = client.post("/api/v1/leads", json={
        "name": "Austin Spine & Sports Therapy",
        "business_type": "Physiotherapy & Rehab",
        "city": "Austin",
        "state": "TX",
        "country": "United States",
        "phone": "+1 512-555-0199",
        "services": ["Spinal Decompression", "Sports Injury Recovery"],
        "source_url": "https://austinspine.com",
        "description": "Orthopedic physical therapy clinic in downtown Austin."
    })
    assert create_res.status_code == 201
    lead_id = create_res.json()["id"]

    # 2. Trigger AI analysis
    analyze_res = client.post(f"/api/v1/leads/{lead_id}/analyze")
    assert analyze_res.status_code == 200
    lead = analyze_res.json()

    assert lead["ai_analysis"] is not None
    b_type = lead["ai_analysis"]["business_type"].lower()
    assert "physio" in b_type or "physical therapy" in b_type or "rehab" in b_type or "clinic" in b_type
    assert len(lead["ai_opportunities"]) > 0
    assert len(lead["ai_opportunities"]) <= 3
    assert lead["ai_score"] is not None
    assert lead["ai_score_category"] in ["High", "Medium", "Low"]
    assert lead["ai_score_reason"] is not None
    assert lead["ai_analyzed_at"] is not None

def test_generate_outreach_api_endpoint(client):
    # 1. Create a lead
    create_res = client.post("/api/v1/leads", json={
        "name": "DermaGlow Skin Clinic",
        "business_type": "Dermatology & Skin",
        "city": "Miami",
        "state": "FL",
        "services": ["Laser Skin Resurfacing", "Acne Therapy"],
        "source_url": "https://dermaglow.com",
        "description": "Boutique medical dermatology and cosmetic laser treatments."
    })
    lead_id = create_res.json()["id"]

    # 2. Trigger outreach generation directly (should analyze automatically if needed)
    outreach_res = client.post(f"/api/v1/leads/{lead_id}/generate-outreach")
    assert outreach_res.status_code == 200
    lead = outreach_res.json()

    assert lead["ai_outreach_subject"] is not None
    assert "dermaglow" in lead["ai_outreach_subject"].lower() or "skin" in lead["ai_outreach_subject"].lower() or "laser" in lead["ai_outreach_subject"].lower()
    assert lead["ai_outreach_body"] is not None
    assert len(lead["ai_outreach_body"].split()) >= 50
    assert "CareIntel AI Team" in lead["ai_outreach_body"]

def test_stats_endpoint_includes_ai_metrics(client):
    # Seed a lead and analyze it
    create_res = client.post("/api/v1/leads", json={
        "name": "Kensington Child Wellness",
        "city": "London",
        "source_url": "https://kensingtonwellness.co.uk",
        "services": ["Pediatrics", "Nutrition"]
    })
    lead_id = create_res.json()["id"]
    client.post(f"/api/v1/leads/{lead_id}/analyze")

    stats_res = client.get("/api/v1/leads/stats")
    assert stats_res.status_code == 200
    stats = stats_res.json()
    assert stats["total_leads"] >= 1
    assert stats["ai_analyzed"] >= 1
    assert "high_potential" in stats
    assert "outreach_ready" in stats

