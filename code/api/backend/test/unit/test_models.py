from django.test import TestCase
from ...models import (
    Guest,
    RegisteredUsers,
    Games,
    DailyLeaderboard,
    WeeklyLeaderboard,
)
from datetime import date


today = date.today()
formatted_date_daily = today.strftime("%d%m%Y")
formatted_date_weekly = today.strftime("%U%Y")


class GuestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Guest.objects.create(Username="test_guest")

    def test_username_label(self):
        guest = Guest.objects.get(id=1)
        field_label = guest._meta.get_field("Username").verbose_name
        self.assertEqual(field_label, "Username")

    def test_username_max_length(self):
        guest = Guest.objects.get(id=1)
        max_length = guest._meta.get_field("Username").max_length
        self.assertEqual(max_length, 255)

    def test_username_unique(self):
        guest = Guest.objects.get(id=1)
        unique = guest._meta.get_field("Username").unique
        self.assertEqual(unique, True)


class CustomUserManagerTest(TestCase):
    def test_create_user(self):
        user = RegisteredUsers.objects.create_user("username", "password123")
        self.assertTrue(isinstance(user, RegisteredUsers))

    def test_create_superuser(self):
        user = RegisteredUsers.objects.create_superuser("username", "password123")
        self.assertTrue(isinstance(user, RegisteredUsers))


class RegisteredUsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        RegisteredUsers.objects.create(username="test_user")

    """test_games_won"""

    def test_games_won_label(self):
        user = RegisteredUsers.objects.get(username="test_user")
        field_label = user._meta.get_field("GamesWon").verbose_name
        self.assertEqual(field_label, "GamesWon")

    def test_games_won_default(self):
        user = RegisteredUsers.objects.get(username="test_user")
        default = user._meta.get_field("GamesWon").default
        self.assertEqual(default, 0)

    """test_game_draw"""

    def test_game_draw_label(self):
        user = RegisteredUsers.objects.get(username="test_user")
        field_label = user._meta.get_field("GamesDrawn").verbose_name
        self.assertEqual(field_label, "GamesDrawn")

    def test_game_draw_default(self):
        user = RegisteredUsers.objects.get(username="test_user")
        default = user._meta.get_field("GamesDrawn").default
        self.assertEqual(default, 0)

    """test_games_lost"""

    def test_games_lost_label(self):
        user = RegisteredUsers.objects.get(username="test_user")
        field_label = user._meta.get_field("GamesLost").verbose_name
        self.assertEqual(field_label, "GamesLost")

    def test_games_lost_default(self):
        user = RegisteredUsers.objects.get(username="test_user")
        default = user._meta.get_field("GamesLost").default
        self.assertEqual(default, 0)

    """test_elo_rbc"""

    def test_elo_rbc_label(self):
        user = RegisteredUsers.objects.get(username="test_user")
        field_label = user._meta.get_field("EloReallyBadChess").verbose_name
        self.assertEqual(field_label, "EloReallyBadChess")

    def test_elo_rbc_default(self):
        user = RegisteredUsers.objects.get(username="test_user")
        default = user._meta.get_field("EloReallyBadChess").default
        self.assertEqual(default, 400)

    """test_session_id"""

    def test_session_id_label(self):
        user = RegisteredUsers.objects.get(username="test_user")
        field_label = user._meta.get_field("session_id").verbose_name
        self.assertEqual(field_label, "session id")

    def test_session_id_max_length(self):
        user = RegisteredUsers.objects.get(username="test_user")
        max_length = user._meta.get_field("session_id").max_length
        self.assertEqual(max_length, 255)

    def test_session_id_default(self):
        user = RegisteredUsers.objects.get(username="test_user")
        default = user._meta.get_field("session_id").default
        self.assertEqual(default, "")

    """test __str__"""

    def test_correct_name(self):
        user = RegisteredUsers.objects.get(username="test_user")
        expected_user_name = user.username
        self.assertEqual(expected_user_name, str(user))


class GamesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Games.objects.create(username1="player1", username2="player2", png="test_png")

    def test_username1_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field("username1").verbose_name
        self.assertEqual(field_label, "username1")

    def test_username2_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field("username2").verbose_name
        self.assertEqual(field_label, "username2")

    def test_username1_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field("username1").max_length
        self.assertEqual(max_length, 255)

    def test_username2_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field("username2").max_length
        self.assertEqual(max_length, 255)

    def test_png_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field("png").verbose_name
        self.assertEqual(field_label, "png")

    def test_png_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field("png").max_length
        self.assertEqual(max_length, 255)


class DailyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        DailyLeaderboard.objects.create(
            username="test_user",
            challenge_date=formatted_date_daily,
            moves_count=1,
            result="win",
            attempts=1,
        )

    def test_username_label(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        field_label = lb._meta.get_field("username").verbose_name
        self.assertEqual(field_label, "username")

    def test_username_max_length(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        max_length = lb._meta.get_field("username").max_length
        self.assertEqual(max_length, 255)

    def test_challenge_date_label(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        field_label = lb._meta.get_field("challenge_date").verbose_name
        self.assertEqual(
            field_label, "challenge date"
        )  # Use space instead of underscore

    def test_moves_count_label(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        field_label = lb._meta.get_field("moves_count").verbose_name
        self.assertEqual(field_label, "moves count")  # Use space instead of underscore

    def test_result_label(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        field_label = lb._meta.get_field("result").verbose_name
        self.assertEqual(field_label, "result")

    def test_result_max_length(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        max_length = lb._meta.get_field("result").max_length
        self.assertEqual(max_length, 10)

    def test_attemps_label(self):
        lb = DailyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_daily
        )
        field_label = lb._meta.get_field("attempts").verbose_name
        self.assertEqual(field_label, "attempts")


class WeeklyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        WeeklyLeaderboard.objects.create(
            username="test_user",
            challenge_date=formatted_date_weekly,
            moves_count=1,
            result="win",
        )

    def test_username_label(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        field_label = lb._meta.get_field("username").verbose_name
        self.assertEqual(field_label, "username")

    def test_username_max_length(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        max_length = lb._meta.get_field("username").max_length
        self.assertEqual(max_length, 255)

    def test_moves_count_label(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        field_label = lb._meta.get_field("moves_count").verbose_name
        self.assertEqual(field_label, "moves count")

    def test_challenge_date_label(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        field_label = lb._meta.get_field("challenge_date").verbose_name
        self.assertEqual(field_label, "challenge date")

    def test_result_label(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        field_label = lb._meta.get_field("result").verbose_name
        self.assertEqual(field_label, "result")

    def test_result_max_length(self):
        lb = WeeklyLeaderboard.objects.get(
            username="test_user", challenge_date=formatted_date_weekly
        )
        max_length = lb._meta.get_field("result").max_length
        self.assertEqual(max_length, 10)
