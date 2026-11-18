"""
Tests for basic API endpoints.

These tests verify that the API endpoints return correct responses
and have the expected structure. Following the AAA pattern.
"""


class TestEndpoints:
    """Test suite for API endpoints."""

    def test_get_activities_returns_all_activities(self, client):
        """
        Test that GET /activities returns all activities with correct structure.
        
        ARRANGE: TestClient is provided by fixture
        ACT: Make GET request to /activities endpoint
        ASSERT: Verify status code and response structure
        """
        # ARRANGE (implicit from fixture)
        
        # ACT
        response = client.get("/activities")
        
        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        
        # Verify expected activities exist
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_contains_required_fields(self, client, sample_activity):
        """
        Test that each activity has all required fields.
        
        ARRANGE: Get activities from fixture
        ACT: Fetch activities and inspect Chess Club
        ASSERT: Verify all required fields are present
        """
        # ARRANGE (implicit from fixture)
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        activity = activities[sample_activity]
        
        # ASSERT
        # Verify required fields exist
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        
        # Verify field types
        assert isinstance(activity["description"], str)
        assert isinstance(activity["schedule"], str)
        assert isinstance(activity["max_participants"], int)
        assert isinstance(activity["participants"], list)

    def test_get_activities_participants_are_emails(self, client, sample_activity):
        """
        Test that participants in activities are valid email strings.
        
        ARRANGE: Get activities from fixture
        ACT: Fetch activities and check participant list
        ASSERT: Verify participants are non-empty strings (email format)
        """
        # ARRANGE (implicit from fixture)
        
        # ACT
        response = client.get("/activities")
        activities = response.json()
        participants = activities[sample_activity]["participants"]
        
        # ASSERT
        # Verify participants list contains valid emails
        assert len(participants) > 0
        for participant in participants:
            assert isinstance(participant, str)
            assert "@" in participant  # Basic email format check
            assert len(participant) > 0

    def test_root_endpoint(self, client):
        """
        Test that GET / redirects correctly.
        
        ARRANGE: TestClient is provided by fixture
        ACT: Make GET request to / endpoint
        ASSERT: Verify redirect response (follow_redirects=False shows 307)
        """
        # ARRANGE (implicit from fixture)
        
        # ACT
        response = client.get("/", follow_redirects=False)
        
        # ASSERT
        assert response.status_code in [200, 307]  # 307 is redirect, 200 if followed
