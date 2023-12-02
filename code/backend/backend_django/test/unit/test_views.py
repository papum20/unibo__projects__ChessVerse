from django.test import TestCase, Client
from django.urls import reverse
from ...models import RegisteredUsers
import json


class AddGuestViewTest(TestCase):
    def test_view_url_exists_at_desired_location(self):
        response = self.client.get('/backend_django/add_guest/')
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
            '/backend_django/signup/',
            json.dumps({
                'username': 'test_user',
                'password': 'secret',
                'eloReallyBadChess': '1000',
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
                'eloSecondType': '1000'
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
            '/backend_django/login/',
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
            '/backend_django/login/?next=/backend_django/signout/',
            fetch_redirect_response=False
        )

    '''
    def test_view_url_exists_at_desired_location(self):
        # Assert the user is logged in
        self.assertTrue(self.client.login(username='test_user', password='secret'))

        response = self.client.post('/backend_django/signout/')
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
