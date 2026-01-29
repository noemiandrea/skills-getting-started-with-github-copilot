from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)

def test_read_root():
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"

def test_get_activities():
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "participants" in data["Chess Club"]

def test_signup_flow():
    activity = "Chess Club"
    email = "test_user@mergington.edu"
    
    # 1. Signup
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity}"}
    
    # 2. Verify added
    activities = client.get("/activities").json()
    assert email in activities[activity]["participants"]

    # 3. Duplicate signup should fail
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 400
    
    # 4. Delete participant
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    assert response.status_code == 200
    assert response.json() == {"message": f"Removed {email} from {activity}"}
    
    # 5. Verify removed
    activities = client.get("/activities").json()
    assert email not in activities[activity]["participants"]
    
def test_signup_invalid_activity():
    response = client.post("/activities/InvalidClub/signup?email=test@test.com")
    assert response.status_code == 404

def test_delete_invalid_participant():
    activity = "Chess Club"
    email = "nonexistent@mergington.edu"
    response = client.delete(f"/activities/{activity}/participants?email={email}")
    assert response.status_code == 400
