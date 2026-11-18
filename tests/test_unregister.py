"""
Tests for the unregister (delete) functionality.

These tests verify participant removal, error handling,
and data consistency. Following the AAA pattern.
"""


class TestUnregister:
    """Test suite for unregister endpoint."""

    def test_unregister_existing_participant_success(self, client, sample_activity, existing_participant):
        """
        Test that an existing participant can be successfully unregistered.
        
        ARRANGE: Get activity and existing participant from fixtures
        ACT: Delete request to unregister participant
        ASSERT: Verify 200 status and participant was removed
        """
        # ARRANGE
        # Get initial participant list
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)
        
        # Verify participant is in the list
        assert existing_participant in initial_participants
        
        # ACT
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": existing_participant}
        )
        
        # ASSERT
        # Check HTTP response
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        final_response = client.get("/activities")
        final_participants = final_response.json()[sample_activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count - 1
        assert existing_participant not in final_participants

    def test_unregister_nonexistent_participant_error(self, client, sample_activity, sample_email):
        """
        Test that unregistering a non-existent participant returns 404 error.
        
        ARRANGE: Get activity and email that's not registered
        ACT: Try to delete unregistered participant
        ASSERT: Verify 404 error and participant list unchanged
        """
        # ARRANGE
        # Get initial participant list
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)
        
        # Verify participant is not in the list
        assert sample_email not in initial_participants
        
        # ACT
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        
        # ASSERT
        # Check error response
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
        
        # Verify participant list is unchanged
        final_response = client.get("/activities")
        final_participants = final_response.json()[sample_activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count
        assert final_participants == initial_participants

    def test_unregister_nonexistent_activity_error(self, client, existing_participant):
        """
        Test that unregistering from a non-existent activity returns 404 error.
        
        ARRANGE: Get participant and use fake activity name
        ACT: Try to delete from non-existent activity
        ASSERT: Verify 404 error
        """
        # ARRANGE
        fake_activity = "Nonexistent Activity"
        
        # ACT
        response = client.delete(
            f"/activities/{fake_activity}/unregister",
            params={"email": existing_participant}
        )
        
        # ASSERT
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_updates_availability(self, client, sample_activity, existing_participant):
        """
        Test that unregister correctly updates the availability counter.
        
        ARRANGE: Get initial availability info
        ACT: Unregister a participant
        ASSERT: Verify availability increased by 1
        """
        # ARRANGE
        initial_response = client.get("/activities")
        activity_data = initial_response.json()[sample_activity]
        initial_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        # ACT
        client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": existing_participant}
        )
        
        # ASSERT
        final_response = client.get("/activities")
        activity_data = final_response.json()[sample_activity]
        final_spots = activity_data["max_participants"] - len(activity_data["participants"])
        
        assert final_spots == initial_spots + 1

    def test_unregister_does_not_affect_other_activities(self, client, sample_activity, another_activity, existing_participant):
        """
        Test that unregistering from one activity doesn't affect other activities.
        
        ARRANGE: Get initial state of both activities
        ACT: Unregister from one activity
        ASSERT: Verify other activity was not modified
        """
        # ARRANGE
        initial_response = client.get("/activities")
        other_activity_initial = initial_response.json()[another_activity]["participants"].copy()
        
        # ACT
        client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": existing_participant}
        )
        
        # ASSERT
        final_response = client.get("/activities")
        other_activity_final = final_response.json()[another_activity]["participants"]
        
        # Verify other activity's participant list is unchanged
        assert other_activity_final == other_activity_initial

    def test_unregister_then_signup_again(self, client, sample_activity, existing_participant):
        """
        Test that a participant can re-register after being unregistered.
        
        ARRANGE: Get initial state
        ACT: Unregister, then signup again
        ASSERT: Verify participant can be re-added
        """
        # ARRANGE
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[sample_activity]["participants"])
        
        # ACT - Unregister
        delete_response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": existing_participant}
        )
        assert delete_response.status_code == 200
        
        # ACT - Signup again
        signup_response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": existing_participant}
        )
        
        # ASSERT
        assert signup_response.status_code == 200
        
        # Verify participant is back in list
        final_response = client.get("/activities")
        final_participants = final_response.json()[sample_activity]["participants"]
        final_count = len(final_participants)
        
        assert final_count == initial_count
        assert existing_participant in final_participants
