"""
Tests for the signup functionality.

These tests verify participant registration, duplicate prevention,
and error handling. Following the AAA pattern.
"""


class TestSignup:
    """Test suite for signup endpoint."""

    def test_signup_new_participant_success(self, client, sample_activity, sample_email):
        """
        Test that a new participant can successfully sign up for an activity.
        
        ARRANGE: Get sample activity and unique email from fixtures
        ACT: Post signup request with new email
        ASSERT: Verify 200 status and participant was added
        """
        # ARRANGE
        # Get initial participant list
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)
        
        # Verify test email is not already signed up
        assert sample_email not in initial_participants
        
        # ACT
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        # Check HTTP response
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        
        # Verify participant count increased
        final_response = client.get("/activities")
        final_participants = final_response.json()[sample_activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count + 1
        assert sample_email in final_participants

    def test_signup_duplicate_participant_error(self, client, sample_activity, existing_participant):
        """
        Test that signing up with an email already registered returns 400 error.
        
        ARRANGE: Get activity and existing participant from fixtures
        ACT: Try to post signup with already-registered email
        ASSERT: Verify 400 error and participant not duplicated
        """
        # ARRANGE
        # Get initial participant list
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)
        
        # Verify participant is in the list
        assert existing_participant in initial_participants
        
        # ACT
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": existing_participant}
        )
        
        # ASSERT
        # Check error response
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
        
        # Verify participant was NOT added (count didn't change)
        final_response = client.get("/activities")
        final_participants = final_response.json()[sample_activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count
        # Verify only one instance of the email exists
        assert final_participants.count(existing_participant) == 1

    def test_signup_nonexistent_activity_error(self, client, sample_email):
        """
        Test that signing up for a non-existent activity returns 404 error.
        
        ARRANGE: Get sample email and use fake activity name
        ACT: Try to post signup for non-existent activity
        ASSERT: Verify 404 error
        """
        # ARRANGE
        fake_activity = "Nonexistent Activity"
        
        # ACT
        response = client.post(
            f"/activities/{fake_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_updates_availability(self, client, sample_activity, sample_email):
        """
        Test that signup correctly updates the availability counter.
        
        ARRANGE: Get initial availability info
        ACT: Sign up a new participant
        ASSERT: Verify availability decreased by 1
        """
        # ARRANGE
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[sample_activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # ACT
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        final_response = client.get("/activities")
        activity_data = final_response.json()[sample_activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        assert final_spots == initial_spots - 1

    def test_signup_does_not_affect_other_activities(self, client, sample_activity, another_activity, sample_email):
        """
        Test that signing up for one activity doesn't affect other activities.
        
        ARRANGE: Get initial state of both activities
        ACT: Sign up for one activity
        ASSERT: Verify other activity was not modified
        """
        # ARRANGE
        initial_response = client.get("/activities")
        other_activity_initial = initial_response.json()[another_activity]["participants"].copy()
        
        # ACT
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # ASSERT
        final_response = client.get("/activities")
        other_activity_final = final_response.json()[another_activity]["participants"]
        
        # Verify other activity's participant list is unchanged
        assert other_activity_final == other_activity_initial
