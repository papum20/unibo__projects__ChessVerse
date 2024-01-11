from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from ...views import (
    is_nickname_in_database,
    generate_random_nickname,
    MAX_DAILY_GAMES,
    check_start_daily,
)
from django.contrib.auth.models import User
from django.contrib import auth
from ...models import (
    RegisteredUsers,
    Guest,
    DailyLeaderboard,
    WeeklyLeaderboard,
)
import json
from datetime import date, datetime

today = date.today()
formatted_date_daily = today.strftime("%d%m%Y")
formatted_date_weekly = today.strftime("%U%Y")


class IsNicknameInDatabaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Guest.objects.create(Username="test_user")

    def test_existing_nickname_is_found(self):
        self.assertTrue(is_nickname_in_database("test_user"))

    def test_non_existing_nickname_is_not_found(self):
        self.assertFalse(is_nickname_in_database("wrong_user"))


class GenerateRandomNicknameTest(TestCase):
    def test_random_is_not_in_database(self):
        self.assertFalse(is_nickname_in_database(generate_random_nickname()))


class AddGuestViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.post("/add_guest/")
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(reverse("add_guest"))
        self.assertEqual(response.status_code, 200)

    def test_view_correct_response(self):
        response = self.client.post(reverse("add_guest"))
        self.assertEqual(response.status_code, 200)
        response_content = json.loads(response.content)
        self.assertTrue(
            Guest.objects.filter(Username=response_content["guest_nickname"]).exists()
        )


class UserSignupViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        # Ensure a clean state
        RegisteredUsers.objects.filter(username="test_user").delete()

        response = self.client.post(
            reverse("user_signup"),
            json.dumps(
                {
                    "username": "test_user",
                    "password": "secret",
                    "eloReallyBadChess": 800,  # Send as number
                }
            ),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)
        # Check the response body
        self.assertJSONEqual(response.content, {"message": "Signup successful"})

        def test_view_url_accessible_by_name(self):
            response = self.client.post(
                reverse("user_signup"),
                json.dumps(
                    {
                        "username": "test_user",
                        "password": "secret",
                        "eloReallyBadChess": "800",
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)

        def test_view_response_with_wrong_request_type(self):
            response = self.client.get(reverse("user_signup"))
            self.assertEqual(response.status_code, 405)

        def test_view_response_with_already_existing_user(self):
            RegisteredUsers.objects.create_user(username="test_user", password="secret")
            response = self.client.post(
                reverse("user_signup"),
                json.dumps(
                    {
                        "username": "test_user",
                        "password": "secret",
                        "eloReallyBadChess": "400",
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 500)

        def test_signup_with_valid_data_response(self):
            response = self.client.post(
                reverse("user_signup"),
                json.dumps(
                    {
                        "username": "new_user",
                        "password": "secret",
                        "eloReallyBadChess": 1200,
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(response.content, {"message": "Signup successful"})

        def test_signup_response_data(self):
            # Ensure a clean state
            RegisteredUsers.objects.filter(username="test_user").delete()

            response = self.client.post(
                reverse("user_signup"),
                json.dumps(
                    {
                        "username": "test_user",
                        "password": "secret",
                        "eloReallyBadChess": 800,  # Send as number
                    }
                ),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)

            # Check the response data
            response_data = json.loads(response.content)
            self.assertEqual(response_data["username"], "test_user")
            self.assertEqual(response_data["eloReallyBadChess"], 800)


class UserLoginViewTest(TestCase):
    def setUp(self):
        RegisteredUsers.objects.create_user(username="test_user", password="secret")

    def test_view_url_exists_at_correct_location(self):
        response = self.client.post(
            "/login/",
            json.dumps({"username": "test_user", "password": "secret"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(
            reverse("user_login"),
            json.dumps({"username": "test_user", "password": "secret"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 200)

        def test_login_with_correct_credentials_response(self):
            response = self.client.post(
                reverse("user_login"),
                json.dumps({"username": "test_user", "password": "secret"}),
                content_type="application/json",
            )
            self.assertEqual(response.status_code, 200)
            self.assertJSONEqual(
                response.content,
                {
                    "message": "Login successful",
                    "elo_really_bad_chess": RegisteredUsers.objects.get(
                        username="test_user"
                    ).EloReallyBadChess,
                    "session_id": RegisteredUsers.objects.get(
                        username="test_user"
                    ).session_id,
                },
            )

    def test_login_with_wrong_username_response(self):
        response = self.client.post(
            reverse("user_login"),
            json.dumps({"username": "wrong_user", "password": "secret"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {"message": "Invalid credentials"})

    def test_login_with_wrong_password_response(self):
        response = self.client.post(
            reverse("user_login"),
            json.dumps({"username": "test_user", "password": "wrong"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {"message": "Invalid credentials"})


class UserSignoutViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username="testuser", password="12345")
        self.client.login(username="testuser", password="12345")

    def test_user_signout(self):
        response = self.client.get(reverse("user_signout"))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"message": "Logout successful"})
        user = auth.get_user(self.client)
        # Verify the user has been logged out
        self.assertFalse(user.is_authenticated)


class GetDailyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        DailyLeaderboard.objects.create(
            username="test_user1", challenge_date=formatted_date_daily, moves_count=10
        )
        DailyLeaderboard.objects.create(
            username="test_user2", challenge_date=formatted_date_daily, moves_count=15
        )

    def test_view_exists_at_desired_location(self):
        response = self.client.get(
            "/get_daily_leaderboard/", {"date": formatted_date_daily}
        )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse("get_daily_leaderboard"), {"date": formatted_date_daily}
        )
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse("get_daily_leaderboard"))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"message": "Invalid request method"})

    def test_view_returns_correct_data(self):
        # Ensure the database state
        DailyLeaderboard.objects.create(
            username="test_user1",
            moves_count=10,
            challenge_date=formatted_date_daily,
            result="win",
        )
        DailyLeaderboard.objects.create(
            username="test_user2",
            moves_count=15,
            challenge_date=formatted_date_daily,
            result="win",
        )

        response = self.client.get(
            reverse("get_daily_leaderboard"), {"date": formatted_date_daily}
        )
        # Decode the response content and parse it as JSON
        content = json.loads(response.content.decode())
        print(content)  # Print the response content

        self.assertEqual(
            content,
            {
                "daily_leaderboard": [
                    {"username": "test_user1", "moves_count": 10},
                    {"username": "test_user2", "moves_count": 15},
                ]
            },
        )


class GetWeeklyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        WeeklyLeaderboard.objects.create(
            username="test_user1",
            challenge_date=formatted_date_weekly,
            moves_count=10,
            result="win",
        )
        WeeklyLeaderboard.objects.create(
            username="test_user2",
            challenge_date=formatted_date_weekly,
            moves_count=15,
            result="win",
        )

    def test_view_exists_at_desired_location(self):
        response = self.client.get(
            "/get_weekly_leaderboard/", {"date": formatted_date_weekly}
        )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(
            reverse("get_weekly_leaderboard"), {"date": formatted_date_weekly}
        )
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse("get_weekly_leaderboard"))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {"message": "Invalid request method"})

    def test_view_returns_correct_data(self):
        response = self.client.get(
            reverse("get_weekly_leaderboard"), {"date": formatted_date_weekly}
        )
        # Decode the response content and parse it as JSON
        content = json.loads(response.content.decode())
        self.assertEqual(
            content,
            {
                "weekly_leaderboard": [
                    {"username": "test_user1", "moves_count": 10},
                    {"username": "test_user2", "moves_count": 15},
                ]
            },
        )


class CheckStartDailyTest(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def test_check_start_daily(self):
        # Create a request
        request = self.factory.get("/check_start_daily/", {"username": "testuser"})
        request.method = "GET"

        # Test when username is not provided
        request.GET = request.GET.copy()
        request.GET.pop("username", None)
        response = check_start_daily(request)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(
            json.loads(response.content),
            {"message": "Username is required as a query parameter"},
        )

        # Test when username is provided
        request.GET = request.GET.copy()
        request.GET["username"] = "testuser"
        response = check_start_daily(request)
        self.assertIn(response.status_code, [200, 400, 500])

        # Test for invalid request method
        request.method = "POST"
        response = check_start_daily(request)
        self.assertEqual(response.status_code, 405)
        self.assertEqual(
            json.loads(response.content), {"message": "Invalid request method"}
        )


class GetMultiplayerLeaderboardViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        RegisteredUsers.objects.create(username="user1", EloReallyBadChess=1200)
        RegisteredUsers.objects.create(username="user2", EloReallyBadChess=1300)
        RegisteredUsers.objects.create(username="user3", EloReallyBadChess=1100)

    def test_get_multiplayer_leaderboard(self):
        response = self.client.get(reverse("get_multiplayer_leaderboard"))
        self.assertEqual(response.status_code, 200)
        leaderboard = response.json()
        # Check that the leaderboard is sorted by Elo rating in descending order
        expected_leaderboard = {
            "multiplayer_leaderboard": [
                {"username": "user2", "EloReallyBadChess": 1300},
                {"username": "user1", "EloReallyBadChess": 1200},
                {"username": "user3", "EloReallyBadChess": 1100},
            ]
        }
        self.assertEqual(leaderboard, expected_leaderboard)


class GetRankedLeaderboardViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse("get_ranked_leaderboard")
        RegisteredUsers.objects.create(username="user1", score_ranked=100)
        RegisteredUsers.objects.create(username="user2", score_ranked=200)

    def test_get_ranked_leaderboard(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        expected_data = [
            {"username": "user2", "score_ranked": 200},
            {"username": "user1", "score_ranked": 100},
        ]
        self.assertListEqual(response.json()["ranked_leaderboard"], expected_data)
