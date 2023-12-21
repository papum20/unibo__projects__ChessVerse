import unittest
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest import mock
from unittest.mock import AsyncMock, PropertyMock

import sys
import random
import chess
import socketio

sys.path.append("../..")
from Game import Game
from code.game.Game import expected_score

import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
target_dir = "/".join(project_root.split("/")[:-1])
os.chdir(target_dir)


class TestExpectedScore(TestCase):
    def setUp(self) -> None:
        self.rating_a = 2
        self.rating_b = 3

    def method_returns_correctly(self):
        correct_result = 1.0 / (1 + 10 ** ((self.rating_b - self.rating_a) / 400))
        self.assertEqual(expected_score(self.rating_a, self.rating_b), correct_result)
