import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_root_redirect():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    activities = response.json()
    assert isinstance(activities, dict)
    assert "Chess Club" in activities
    assert "Programming Class" in activities
    assert len(activities) > 0

def test_signup_for_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First signup
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    
    # Verify student is in participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email in activities[activity_name]["participants"]
    
    # Try signing up again (should fail)
    response = client.post(f"/activities/{activity_name}/signup?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is already signed up"

def test_signup_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/signup?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"

def test_unregister_from_activity():
    activity_name = "Chess Club"
    email = "test@mergington.edu"
    
    # First make sure the student is signed up
    client.post(f"/activities/{activity_name}/signup?email={email}")
    
    # Unregister
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    
    # Verify student is not in participants
    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities[activity_name]["participants"]
    
    # Try unregistering again (should fail)
    response = client.post(f"/activities/{activity_name}/unregister?email={email}")
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"

def test_unregister_nonexistent_activity():
    response = client.post("/activities/NonexistentClub/unregister?email=test@mergington.edu")
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"