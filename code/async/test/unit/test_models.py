from django.test import TestCase
from ....backend_tmp.backend_django.models import Guest, RegisteredUsers, CustomUserManager


class GuestModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        Guest.objects.create(Username='testUser')

    def test_username_label(self):
        guest = Guest.objects.get(id=1)
        field_label = guest.__meta.get_field('Username').verbose_name
        self.assertEqual(field_label, 'Username')

    def test_username_max_length(self):
        guest = Guest.objects.get(id=1)
        max_length = guest.__meta.get_field('Username').max_length
        self.assertEqual(max_length, 255)

    def test_username_unique(self):
        guest = Guest.objects.get(id=1)
        unique = guest.__meta.get_field('Username').unique
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
        user = RegisteredUsers.objects.get(id=1)
        field_label = user.__meta.get_field('GamesWon').verbose_name
        self.assertEqual(field_label, 'GamesWon')

    def test_games_won_default(self):
        user = RegisteredUsers.objects.get(id=1)
        default = user.__meta.get_field('GamesWon').default
        self.assertEqual(default, 0)

    '''test_games_draw'''
    def test_games_draw_label(self):
        user = RegisteredUsers.objects.get(id=1)
        field_label = user.__meta.get_field('GamesDraw').verbose_name
        self.assertEqual(field_label, 'GamesDraw')

    def test_games_draw_default(self):
        user = RegisteredUsers.objects.get(id=1)
        default = user.__meta.get_field('GamesDraw').default
        self.assertEqual(default, 0)

    '''test_games_lost'''
    def test_games_lost_label(self):
        user = RegisteredUsers.objects.get(id=1)
        field_label = user.__meta.get_field('GamesLost').verbose_name
        self.assertEqual(field_label, 'GamesLost')

    def test_games_lost_default(self):
        user = RegisteredUsers.objects.get(id=1)
        default = user.__meta.get_field('GamesLost').default
        self.assertEqual(default, 0)

    '''test_elo_rbc'''
    def test_elo_rbc_label(self):
        user = RegisteredUsers.objects.get(id=1)
        field_label = user.__meta.get_field('EloReallyBadChess').verbose_name
        self.assertEqual(field_label, 'EloReallyBadChess')

    def test_elo_rbc_default(self):
        user = RegisteredUsers.objects.get(id=1)
        default = user.__meta.get_field('EloReallyBadChess').default
        self.assertEqual(default, 1000)

    '''test_elo_sc'''
    def test_elo_sc_label(self):
        user = RegisteredUsers.objects.get(id=1)
        field_label = user.__meta.get_field('EloSecondChess').verbose_name
        self.assertEqual(field_label, 'EloSecondChess')

    def test_elo_sc_default(self):
        user = RegisteredUsers.objects.get(id=1)
        default = user.__meta.get_field('EloSecondChess').default
        self.assertEqual(default, 1000)

    '''test_groups'''
    def test_groups_related_name(self):
        user = RegisteredUsers.objects.get(id=1)
        related_name = user.__meta.get_field('groups').related_name
        self.assertEqual(related_name, 'registered_users')

    def test_groups_blank(self):
        user = RegisteredUsers.objects.get(id=1)
        blank = user.__meta.get_field('groups').blank
        self.assertEqual(blank, True)

    '''test_user_permissions'''
    def test_user_permissions_related_name(self):
        user = RegisteredUsers.objects.get(id=1)
        related_name = user.__meta.get_field('user_permissions').related_name
        self.assertEqual(related_name, 'registered_users')

    def test_user_permissions_blank(self):
        user = RegisteredUsers.objects.get(id=1)
        blank = user.__meta.get_field('user_permissions').blank
        self.assertEqual(blank, True)
