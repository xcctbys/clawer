import unittest
import doctest
import os
from django.test import TestCase
from django.test._doctest import DocTestSuite


LIST_OF_DOCTESTS= []

def suite():
    suite = unittest.TestSuite()
    for t in LIST_OF_DOCTESTS:
        suite.addTest(DocTestSuite(
            __import__(t, globals(), locals(), fromlist=["*"])
        ))
    # add unit test case
    start_dir = os.path.dirname(__file__)
    mods = unittest.TestLoader().discover(start_dir, "*.py")
    suite.addTests(mods)
    return suite