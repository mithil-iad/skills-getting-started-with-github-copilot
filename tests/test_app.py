import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestGetActivities:
    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        assert isinstance(response.json(), dict)
        assert len(response.json()) > 0

    def test_get_activities_has_required_fields(self):
        """Test that activities have required fields"""
        # Arrange
        # (no setup needed)

        # Act
        response = client.get("/activities")
        activities = response.json()

        # Assert
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)


class TestSignupForActivity:
    def test_signup_success(self):
        """Test successful signup for an activity"""
        # Arrange
        email = "test@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_activity_not_found(self):
        """Test signup for non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_signup_duplicate_email(self):
        """Test duplicate signup is prevented"""
        # Arrange
        email = "duplicate@mergington.edu"
        activity = "Programming Class"

        # Act - First signup
        response1 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Act - Second signup with same email
        response2 = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 400

    def test_participants_list_updated(self):
        """Test that participants list is updated after signup"""
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Drama Club"

        # Act
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email in activities[activity]["participants"]


class TestRemoveFromActivity:
    def test_remove_participant_success(self):
        """Test successful removal of participant"""
        # Arrange
        email = "toremove@mergington.edu"
        activity = "Art Studio"
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 200
        assert "Removed" in response.json()["message"]

    def test_remove_nonexistent_participant(self):
        """Test removing a participant not signed up"""
        # Arrange
        email = "nonexistent@mergington.edu"
        activity = "Tennis Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 400

    def test_remove_from_nonexistent_activity(self):
        """Test removing from non-existent activity"""
        # Arrange
        email = "test@mergington.edu"
        nonexistent_activity = "Nonexistent Activity"

        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/signup",
            params={"email": email}
        )

        # Assert
        assert response.status_code == 404

    def test_participants_list_updated_after_removal(self):
        """Test that participants list updates after removal"""
        # Arrange
        email = "testremove@mergington.edu"
        activity = "Science Club"
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )

        # Act - Remove participant
        client.delete(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        response = client.get("/activities")
        activities = response.json()

        # Assert
        assert email not in activities[activity]["participants"]
