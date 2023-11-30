from django.test import TestCase
from ...models import RegisteredUsers


class AuthViewsTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        RegisteredUsers.objects.create_user(
            username='foo',
            password='foo123'
        )

    def test_is_nickname_in_database(self):
        ...

    def test_generate_random_nickname(self):
        ...

    def test_get_guest_name(self):
        response = self.client.post('/get-guest-name')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'guest_nickname': 'username'}
        )

    def test_add_guest(self):
        ...
        response = self.client.post('/add-guest')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'message': 'Guest added successfully'}
        )

    def test_user_login(self):
        ...

    def test_user_signup(self):
        ...

    def test_user_signout(self):
        self.client.logout()

        response = self.client.post('/user-signout')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {'message': 'Logout successful'}
        )
