def test_create_activity(client, auth_headers):
    """Test creating an activity"""
    activity_data = {
        "title": "Test Activity",
        "description": "Test Description",
        "tags": ["test", "work"],
    }

    response = client.post("/activities/", json=activity_data, headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["title"] == activity_data["title"]
    assert data["description"] == activity_data["description"]
    assert len(data["tags"]) == 2
    assert data["tags"][0]["name"] in ["test", "work"]
    assert data["tags"][1]["name"] in ["test", "work"]
    assert data["timer_status"] == "stopped"
    assert data["recorded_time"] == 0


def test_get_activities_empty(client, auth_headers):
    """Test getting activities when none exist"""
    response = client.get("/activities/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_activities(client, auth_headers, test_activity):
    """Test getting activities when one exists"""
    response = client.get("/activities/", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == test_activity["id"]
    assert data[0]["title"] == test_activity["title"]


def test_get_activities_by_tag(client, auth_headers, test_activity):
    """Test getting activities filtered by tag"""
    # First tag from test_activity
    tag = test_activity["tags"][0]["name"]

    response = client.get(f"/activities/?tag={tag}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["id"] == test_activity["id"]

    # Non-existent tag
    response = client.get("/activities/?tag=randomtag", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_activity_by_id(client, auth_headers, test_activity):
    """Test getting a specific activity by ID"""
    response = client.get(f"/activities/{test_activity['id']}", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_activity["id"]
    assert data["title"] == test_activity["title"]
    assert data["description"] == test_activity["description"]


def test_get_activity_by_id_not_found(client, auth_headers):
    """Test getting a non-existent activity"""
    response = client.get("/activities/999", headers=auth_headers)

    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_update_activity(client, auth_headers, test_activity):
    """Test updating an activity"""
    update_data = {
        "title": "Updated Title",
        "description": "Updated Description",
        "tags": ["updated", "test"],
    }

    response = client.put(
        f"/activities/{test_activity['id']}", json=update_data, headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_activity["id"]
    assert data["title"] == update_data["title"]
    assert data["description"] == update_data["description"]
    assert len(data["tags"]) == 2
    assert data["tags"][0]["name"] in ["updated", "test"]
    assert data["tags"][1]["name"] in ["updated", "test"]


def test_update_activity_not_found(client, auth_headers):
    """Test updating a non-existent activity"""
    update_data = {"title": "Updated Title", "description": "Updated Description"}

    response = client.put("/activities/999", json=update_data, headers=auth_headers)

    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_delete_activity(client, auth_headers, test_activity):
    """Test deleting an activity"""
    response = client.delete(f"/activities/{test_activity['id']}", headers=auth_headers)

    assert response.status_code == 200
    assert "message" in response.json()
    assert "deleted successfully" in response.json()["message"]

    # Verify it's gone
    response = client.get(f"/activities/{test_activity['id']}", headers=auth_headers)
    assert response.status_code == 404


def test_delete_activity_not_found(client, auth_headers):
    """Test deleting a non-existent activity"""
    response = client.delete("/activities/999", headers=auth_headers)

    assert response.status_code == 404
    assert "Activity not found" in response.json()["detail"]


def test_timer_actions(client, auth_headers, test_activity):
    """Test activity timer operations"""
    activity_id = test_activity["id"]

    # Start timer
    response = client.post(
        f"/activities/{activity_id}/timer",
        json={"action": "start"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["timer_status"] == "running"

    # Pause timer
    response = client.post(
        f"/activities/{activity_id}/timer",
        json={"action": "pause"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["timer_status"] == "paused"

    # Restart timer
    response = client.post(
        f"/activities/{activity_id}/timer",
        json={"action": "start"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["timer_status"] == "running"

    # Stop timer
    response = client.post(
        f"/activities/{activity_id}/timer",
        json={"action": "stop"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    assert response.json()["timer_status"] == "stopped"

    # Save activity
    response = client.post(
        f"/activities/{activity_id}/timer",
        json={"action": "save"},
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["timer_status"] == "stopped"
    assert data["recorded_time"] >= 0
    assert "duration" in data


def test_timer_invalid_action(client, auth_headers, test_activity):
    """Test timer with invalid action"""
    response = client.post(
        f"/activities/{test_activity['id']}/timer",
        json={"action": "invalid_action"},
        headers=auth_headers,
    )

    assert response.status_code == 400
    assert "Invalid timer action" in response.json()["detail"]
