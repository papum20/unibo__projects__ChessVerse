import unittest
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest import mock
from unittest.mock import AsyncMock, PropertyMock

import sys
import random
import chess
import socketio

sys.path.append("../..")
from Game import Game, expected_score, update_rating, calc_K

import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = "/".join(project_root.split("/")[:-1])
os.chdir(target_dir)


class TestExpectedScore(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3

    def test_method_returns_correctly(self):
        correct_result = 1.0 / (1 + 10 ** ((self.rating_b - self.rating_a) / 400))
        self.assertEqual(expected_score(self.rating_a, self.rating_b), correct_result)


class TestUpdateRating(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3
        self.risultato = 15

    @mock.patch('Game.expected_score', return_value=10)
    @mock.patch('Game.calc_K', return_value=17.5)
    def test_method_returns_correctly(self, mock_calc_k, mock_expected_score):
        correct_result = (self.rating_a + 17.5 * (15 - 10), self.rating_b + 17.5 * (1 - 15 - 10))
        self.assertEqual(update_rating(self.rating_a, self.rating_b, self.risultato), correct_result)


class TestCalculateK(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3

    def test_method_returns_correctly(self):
        correct_result = round(60 - 0.0167 * (self.rating_a + self.rating_b) / 2)
        self.assertEqual(correct_result, calc_K(self.rating_a, self.rating_b))
