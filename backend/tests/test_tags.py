def test_create_tag(client, auth_headers):
    """Test creating a tag"""
    response = client.post("/tags/", json={"name": "newtag"}, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "newtag"
    assert "id" in data


def test_get_tags_empty(client, auth_headers):
    """Test getting tags when none exist"""
    response = client.get("/tags/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_tags(client, auth_headers, test_activity):
    """Test getting tags when activity with tags exists"""
    response = client.get("/tags/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Tags from test_activity should be present
    tag_names = [tag["name"] for tag in data]
    for activity_tag in test_activity["tags"]:
        assert activity_tag["name"] in tag_names
