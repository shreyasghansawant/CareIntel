def test_create_and_get_lead(client):
    payload = {
        "name": "Beacon Hill Dental",
        "business_type": "Dental Clinic",
        "address": "120 Charles St",
        "city": "Boston",
        "state": "MA",
        "country": "United States",
        "postal_code": "02114",
        "phone": "+1 617-555-0133",
        "email": "hello@beaconhilldental.com",
        "website": "https://www.beaconhilldental.com",
        "services": ["Teeth Whitening", "Invisalign", "Dental Crowns"],
        "source_url": "https://www.beaconhilldental.com",
        "description": "General and cosmetic dental practice in Beacon Hill.",
        "status": "NEW"
    }

    create_res = client.post("/api/v1/leads", json=payload)
    assert create_res.status_code == 201
    lead_data = create_res.json()
    assert lead_data["name"] == "Beacon Hill Dental"
    assert lead_data["normalized_website"] == "beaconhilldental.com"
    lead_id = lead_data["id"]

    # Retrieve by ID
    get_res = client.get(f"/api/v1/leads/{lead_id}")
    assert get_res.status_code == 200
    retrieved = get_res.json()
    assert retrieved["id"] == lead_id
    assert retrieved["city"] == "Boston"
    assert "Invisalign" in retrieved["services"]

def test_get_nonexistent_lead_returns_404(client):
    res = client.get("/api/v1/leads/999999")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()

def test_validation_empty_name(client):
    payload = {
        "name": "   ",
        "source_url": "https://example.com"
    }
    res = client.post("/api/v1/leads", json=payload)
    assert res.status_code == 422

def test_deduplication_by_website(client):
    payload1 = {
        "name": "Metro Physio Clinic",
        "website": "https://www.metrophysioclinic.com",
        "source_url": "https://www.metrophysioclinic.com/about",
        "city": "Chicago",
        "services": ["Physical Therapy"]
    }
    res1 = client.post("/api/v1/leads", json=payload1)
    assert res1.status_code == 201
    lead1_id = res1.json()["id"]

    # Same website with different path and protocol
    payload2 = {
        "name": "Metro Physiotherapy Chicago",
        "website": "http://metrophysioclinic.com/contact-us",
        "source_url": "http://metrophysioclinic.com/contact-us",
        "city": "Chicago",
        "services": ["Sports Rehab"]
    }
    res2 = client.post("/api/v1/leads", json=payload2)
    assert res2.status_code == 201
    lead2_data = res2.json()
    # Should resolve to the existing lead rather than creating a duplicate
    assert lead2_data["id"] == lead1_id

    # Verify total leads count remains 1
    stats_res = client.get("/api/v1/leads/stats")
    assert stats_res.json()["total_leads"] == 1

def test_pagination_and_search(client):
    # Seed 3 distinct clinics
    clinics = [
        {"name": "Alpha Health Clinic", "city": "Austin", "country": "United States", "source_url": "https://alpha.com", "services": ["General Practice"]},
        {"name": "Beta Skin Centre", "city": "Denver", "country": "United States", "source_url": "https://beta.com", "services": ["Dermatology"]},
        {"name": "Gamma Eye Care", "city": "London", "country": "United Kingdom", "source_url": "https://gamma.co.uk", "services": ["Optometry"]}
    ]
    for c in clinics:
        client.post("/api/v1/leads", json=c)

    # Test pagination: page 1, size 2
    res_p1 = client.get("/api/v1/leads?page=1&page_size=2")
    assert res_p1.status_code == 200
    data_p1 = res_p1.json()
    assert len(data_p1["items"]) == 2
    assert data_p1["total"] == 3
    assert data_p1["total_pages"] == 2

    # Test search by clinic name
    res_search = client.get("/api/v1/leads?search=Alpha")
    assert res_search.status_code == 200
    assert len(res_search.json()["items"]) == 1
    assert res_search.json()["items"][0]["name"] == "Alpha Health Clinic"

    # Test filter by city
    res_city = client.get("/api/v1/leads?city=London")
    assert res_city.status_code == 200
    assert len(res_city.json()["items"]) == 1
    assert res_city.json()["items"][0]["city"] == "London"

def test_delete_lead(client):
    payload = {
        "name": "Temporary Health Practice",
        "source_url": "https://temp-practice.com"
    }
    res = client.post("/api/v1/leads", json=payload)
    lead_id = res.json()["id"]

    del_res = client.delete(f"/api/v1/leads/{lead_id}")
    assert del_res.status_code == 200

    # Verify 404 after deletion
    get_res = client.get(f"/api/v1/leads/{lead_id}")
    assert get_res.status_code == 404

def test_seed_demo_leads(client):
    res = client.post("/api/v1/leads/seed-demo")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "success"
    assert data["created"] > 0

    # Check that leads are now present
    list_res = client.get("/api/v1/leads")
    assert list_res.status_code == 200
    assert list_res.json()["total"] >= 5
