from django.test import TestCase
from ...models import Guest, RegisteredUsers, Games


class GuestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Guest.objects.create(Username='test_guest')

    def test_username_label(self):
        guest = Guest.objects.get(id=1)
        field_label = guest._meta.get_field('Username').verbose_name
        self.assertEqual(field_label, 'Username')

    def test_username_max_length(self):
        guest = Guest.objects.get(id=1)
        max_length = guest._meta.get_field('Username').max_length
        self.assertEqual(max_length, 255)

    def test_username_unique(self):
        guest = Guest.objects.get(id=1)
        unique = guest._meta.get_field('Username').unique
        self.assertEqual(unique, True)


class CustomUserManagerTest(TestCase):
    def test_create_user(self):
        user = RegisteredUsers.objects.create_user('username', 'password123')
        self.assertTrue(isinstance(user, RegisteredUsers))

    def test_create_superuser(self):
        user = RegisteredUsers.objects.create_superuser('username', 'password123')
        self.assertTrue(isinstance(user, RegisteredUsers))


class RegisteredUsersModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        RegisteredUsers.objects.create(username='test_user')

    '''test_games_won'''
    def test_games_won_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('GamesWon').verbose_name
        self.assertEqual(field_label, 'GamesWon')

    def test_games_won_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('GamesWon').default
        self.assertEqual(default, 0)

    '''test_game_draw'''
    def test_game_draw_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('GameDraw').verbose_name
        self.assertEqual(field_label, 'GameDraw')

    def test_game_draw_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('GameDraw').default
        self.assertEqual(default, 0)

    '''test_games_lost'''
    def test_games_lost_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('GamesLost').verbose_name
        self.assertEqual(field_label, 'GamesLost')

    def test_games_lost_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('GamesLost').default
        self.assertEqual(default, 0)

    '''test_elo_rbc'''
    def test_elo_rbc_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('EloReallyBadChess').verbose_name
        self.assertEqual(field_label, 'EloReallyBadChess')

    def test_elo_rbc_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('EloReallyBadChess').default
        self.assertEqual(default, 1000)

    '''test_elo_sc'''
    def test_elo_sc_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('EloSecondChess').verbose_name
        self.assertEqual(field_label, 'EloSecondChess')

    def test_elo_sc_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('EloSecondChess').default
        self.assertEqual(default, 1000)

    '''test_session_id'''
    def test_session_id_label(self):
        user = RegisteredUsers.objects.get(username='test_user')
        field_label = user._meta.get_field('session_id').verbose_name
        self.assertEqual(field_label, 'session id')

    def test_session_id_max_length(self):
        user = RegisteredUsers.objects.get(username='test_user')
        max_length = user._meta.get_field('session_id').max_length
        self.assertEqual(max_length, 255)

    def test_session_id_default(self):
        user = RegisteredUsers.objects.get(username='test_user')
        default = user._meta.get_field('session_id').default
        self.assertEqual(default, '')

    '''test __str__'''
    def test_correct_name(self):
        user = RegisteredUsers.objects.get(username='test_user')
        expected_user_name = user.username
        self.assertEqual(expected_user_name, str(user))


class GamesModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Games.objects.create(username1='player1', username2='player2', png='test_png')

    def test_username1_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field('username1').verbose_name
        self.assertEqual(field_label, 'username1')

    def test_username2_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field('username2').verbose_name
        self.assertEqual(field_label, 'username2')

    def test_username1_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field('username1').max_length
        self.assertEqual(max_length, 255)

    def test_username2_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field('username2').max_length
        self.assertEqual(max_length, 255)

    def test_png_label(self):
        game = Games.objects.get(id=1)
        field_label = game._meta.get_field('png').verbose_name
        self.assertEqual(field_label, 'png')

    def test_png_max_length(self):
        game = Games.objects.get(id=1)
        max_length = game._meta.get_field('png').max_length
        self.assertEqual(max_length, 255)
