#coding=utf-8
""" test form
"""

from django.utils import unittest
from html5helper.forms import *


class TestBasisForm(unittest.TestCase):
    def test_init(self):
        form = BasisForm()
        self.assertIsNotNone(form)