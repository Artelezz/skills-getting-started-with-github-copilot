from copy import deepcopy
from urllib.parse import quote

import pytest


def test_root_redirects_to_frontend(client):
    # Arrange
    url = "/"

    # Act
    response = client.get(url, follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_activity_details(client, activity_data):
    # Arrange
    expected_activities = deepcopy(activity_data)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == expected_activities


def test_signup_adds_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "new+student@mergington.edu"
    expected_activities = deepcopy(activity_data)
    expected_activities[activity_name]["participants"].append(email)
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.post(url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    participants = activities_response.json()[activity_name]["participants"]
    assert participants.count(email) == 1
    assert expected_activities[activity_name]["max_participants"] - len(participants) == 0


@pytest.mark.parametrize("email", ["michael@mergington.edu", "new@mergington.edu"])
def test_signup_rejects_duplicate_participant(client, activity_data, email):
    # Arrange
    url = "/activities/Chess%20Club/signup"
    if email not in activity_data["Chess Club"]["participants"]:
        client.post(url, params={"email": email})
    expected_activities = deepcopy(activity_data)

    # Act
    response = client.post(url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already registered for this activity"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    assert activity_data["Chess Club"]["participants"].count(email) == 1


def test_unregister_removes_only_selected_participant(client, activity_data):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"
    expected_activities = deepcopy(activity_data)
    expected_activities[activity_name]["participants"].remove(email)
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    participants = activities_response.json()[activity_name]["participants"]
    assert participants == ["daniel@mergington.edu"]
    assert expected_activities[activity_name]["max_participants"] - len(participants) == 2


@pytest.mark.parametrize("activity_name", ["Chess Club", "Art Club"])
def test_unregister_rejects_unregistered_participant(client, activity_data, activity_name):
    # Arrange
    email = "absent@mergington.edu"
    expected_activities = deepcopy(activity_data)
    url = f"/activities/{quote(activity_name, safe='')}/signup"

    # Act
    response = client.delete(url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities


def test_unregister_rejects_repeated_removal(client, activity_data):
    # Arrange
    email = "michael@mergington.edu"
    url = "/activities/Chess%20Club/signup"
    client.delete(url, params={"email": email})
    expected_activities = deepcopy(activity_data)

    # Act
    response = client.delete(url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 400
    assert response.json() == {"detail": "Student is not registered for this activity"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities
    assert email not in activity_data["Chess Club"]["participants"]


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_registration_rejects_unknown_activity(client, activity_data, method):
    # Arrange
    expected_activities = deepcopy(activity_data)
    url = "/activities/Missing%20Club/signup"
    email = "student@mergington.edu"

    # Act
    response = client.request(method, url, params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities


@pytest.mark.parametrize("method", ["POST", "DELETE"])
def test_registration_requires_email(client, activity_data, method):
    # Arrange
    expected_activities = deepcopy(activity_data)
    url = "/activities/Chess%20Club/signup"

    # Act
    response = client.request(method, url)
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 422
    assert any(error["loc"] == ["query", "email"] for error in response.json()["detail"])
    assert activities_response.status_code == 200
    assert activities_response.json() == expected_activities


def test_participant_can_signup_again_after_unregistering(client, activity_data):
    # Arrange
    email = "returning@mergington.edu"
    activity_name = "Art Club"
    url = f"/activities/{quote(activity_name, safe='')}/signup"
    original_activities = deepcopy(activity_data)
    registered_activities = deepcopy(original_activities)
    registered_activities[activity_name]["participants"].append(email)

    # Act
    signup_response = client.post(url, params={"email": email})
    after_signup = client.get("/activities").json()
    unregister_response = client.delete(url, params={"email": email})
    after_unregister = client.get("/activities").json()
    second_signup_response = client.post(url, params={"email": email})
    after_second_signup = client.get("/activities").json()

    # Assert
    assert signup_response.status_code == 200
    assert signup_response.json() == {"message": f"Signed up {email} for {activity_name}"}
    assert unregister_response.status_code == 200
    assert unregister_response.json() == {"message": f"Unregistered {email} from {activity_name}"}
    assert second_signup_response.status_code == 200
    assert second_signup_response.json() == signup_response.json()
    assert after_signup == registered_activities
    assert after_unregister == original_activities
    assert after_second_signup == registered_activities