from django.test import TestCase
from django.urls import reverse
from ...views import is_nickname_in_database, generate_random_nickname, MAX_DAILY_GAMES
from ...models import RegisteredUsers, Guest, DailyLeaderboard, WeeklyLeaderboard, MultiplayerLeaderboard
import json
from datetime import date


class IsNicknameInDatabaseTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Guest.objects.create(Username='test_user')

    def test_existing_nickname_is_found(self):
        self.assertTrue(is_nickname_in_database('test_user'))

    def test_non_existing_nickname_is_not_found(self):
        self.assertFalse(is_nickname_in_database('wrong_user'))


class GenerateRandomNicknameTest(TestCase):
    def test_random_is_not_in_database(self):
        self.assertFalse(is_nickname_in_database(generate_random_nickname()))


class AddGuestViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/backend/add_guest/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('add_guest'))
        self.assertEqual(response.status_code, 200)

    def test_view_correct_response(self):
        response = self.client.get(reverse('add_guest'))
        self.assertJSONEqual(response.content, {'message': 'Guest added successfully!'})


class UserSignupViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.post(
            '/backend/signup/',
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_view_response_with_wrong_request_type(self):
        response = self.client.get(reverse('user_signup'))
        self.assertEqual(response.status_code, 405)

    def test_view_response_with_already_existing_user(self):
        RegisteredUsers.objects.create_user(username='test_user', password='secret')
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 500)

    def test_correct_signup_response(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertJSONEqual(response.content, {'message': 'Signup successful'})

    def test_signup_with_missing_username_response(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Missing required fields'})

    def test_signup_with_missing_password_response(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Missing required fields'})

    def test_signup_with_missing_elorbc_response(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Missing required fields'})

    def test_signup_with_missing_elost_response(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        self.assertJSONEqual(response.content, {'message': 'Missing required fields'})

    def test_user_is_in_database(self):
        response = self.client.post(
            reverse('user_signup'),
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
            }),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(RegisteredUsers.objects.filter(username='test_user').exists())

class UserLoginViewTest(TestCase):
    def setUp(self):
        RegisteredUsers.objects.create_user(
            username='test_user', password='secret'
        )

    def test_view_url_exists_at_correct_location(self):
        response = self.client.post(
            '/backend/login/',
            json.dumps({'username': 'test_user', 'password': 'secret'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.post(
            reverse('user_login'),
            json.dumps({'username': 'test_user', 'password': 'secret'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

    def test_login_with_correct_credentials_response(self):
        response = self.client.post(
            reverse('user_login'),
            json.dumps({'username': 'test_user', 'password': 'secret'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {'message': 'Login successful'})

    def test_login_with_wrong_username_response(self):
        response = self.client.post(
            reverse('user_login'),
            json.dumps({'username': 'wrong_user', 'password': 'secret'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {'message': 'Invalid credentials'})

    def test_login_with_wrong_password_response(self):
        response = self.client.post(
            reverse('user_login'),
            json.dumps({'username': 'test_user', 'password': 'wrong'}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 401)
        self.assertJSONEqual(response.content, {'message': 'Invalid credentials'})


class UserSignoutViewTest(TestCase):
    def setUp(self):
        self.user = RegisteredUsers.objects.create_user(username='test_user', password='secret')

    def test_view_redirects_if_not_logged_in(self):
        response = self.client.post(reverse('user_signout'))
        self.assertRedirects(
            response,
            '/backend/login/?next=/backend/signout/',
            fetch_redirect_response=False
        )

    '''
    def test_view_url_exists_at_desired_location(self):
        # Assert the user is logged in
        self.assertTrue(self.client.login(username='test_user', password='secret'))

        response = self.client.post('/backend/signout/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        # Check that user is logged in
        self.assertTrue(self.client.login(username='test_user', password='secret'))

        response = self.client.post(reverse('user_signout'))
        self.assertEqual(response.status_code, 200)

    def test_logout_correct_response(self):
        # Check that user is logged in
        self.assertTrue(self.client.login(username='test_user', password='secret'))

        response = self.client.post(reverse('user_signout'))
        self.assertJSONEqual(response.content, {'message': 'Logout successful'})
    '''


class GetDailyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        DailyLeaderboard.objects.create(username='test_user1',
                                        challenge_date=date.today(),
                                        moves_count=10)
        DailyLeaderboard.objects.create(username='test_user2',
                                        challenge_date=date.today(),
                                        moves_count=15)

    def test_view_exists_at_desired_location(self):
        response = self.client.get('/backend/get_daily_leaderboard/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('get_daily_leaderboard'))
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse('get_daily_leaderboard'))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'message': 'Invalid request method'})

    def test_view_returns_correct_data(self):
        response = self.client.get(reverse('get_daily_leaderboard'))
        self.assertEqual(response.content, {'daily_leaderboard': [
            {'username': 'test_user1', 'moves_count': 10},
            {'username': 'test_user2', 'moves_count': 15}
        ]})


class GetWeeklyLeaderboardTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        WeeklyLeaderboard.objects.create(username='test_user1',
                                         challenge_date=date.today(),
                                         moves_count=10)
        WeeklyLeaderboard.objects.create(username='test_user2',
                                         challenge_date=date.today(),
                                         moves_count=15)

    def test_view_exists_at_desired_location(self):
        response = self.client.get('/backend/get_weekly_leaderboard/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('get_weekly_leaderboard'))
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse('get_weekly_leaderboard'))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'message': 'Invalid request method'})

    def test_view_returns_correct_data(self):
        response = self.client.get(reverse('get_weekly_leaderboard'))
        self.assertEqual(response.content, {'weekly_leaderboard': [
            {'username': 'test_user1', 'moves_count': 10},
            {'username': 'test_user2', 'moves_count': 15}
        ]})


class CheckStartDailyTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        DailyLeaderboard.objects.create(username='test_user',
                                        challenge_date=date.today(),
                                        moves_count=10)

    def test_view_exists_at_desired_location(self):
        response = self.client.get('/backend/check_start_daily/',
                                   json.dumps({'username': 'test_user'})
                                   )
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('check_start_daily'),
                                   json.dumps({'username': 'test_user'})
                                   )
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse('check_start_daily'))
        self.assertEqual(response.status_code, 405)
        self.assertJSONEqual(response.content, {'message': 'invalid request'})

    '''
    def test_max_number_of_games_played(self):
        daily_leaderboard = DailyLeaderboard.objects.filter(username='test_user').values(
            'username', 'attempts')
        daily_leaderboard[0]['attempts'] = MAX_DAILY_GAMES
        response = self.client.get(reverse('check_start_daily'),
                                   json.dumps({'username': 'test'})
                                   )
        self.assertEqual(response.status_code, 500)
        self.assertJSONEqual(response.content, {'message': 'You have already played the maximum number of games today'})
    '''


class GetMultiplayerLeaderboardTests(TestCase):
    @classmethod
    def setUpClass(cls):
        MultiplayerLeaderboard.objects.create(username='test_user1',
                                              elo=10)
        MultiplayerLeaderboard.objects.create(username='test_user2',
                                              elo=15)

    def test_view_exists_at_desired_location(self):
        response = self.client.get('/backend/get_multiplayer_leaderboard/')
        self.assertEqual(response.status_code, 200)

    def test_view_url_accessible_by_name(self):
        response = self.client.get(reverse('get_multiplayer_leaderboard'))
        self.assertEqual(response.status_code, 200)

    def test_response_405_on_post_request(self):
        response = self.client.post(reverse('get_multiplayer_leaderboard'))
        self.assertEqual(response.status_code, 405)

    def test_view_returns_correct_data(self):
        response = self.client.get(reverse('get_multiplayer_leaderboard'))
        self.assertEqual(response.content, {'weekly_leaderboard': [
            {'username': 'test_user1', 'elo': 10},
            {'username': 'test_user2', 'elo': 15}
        ]})