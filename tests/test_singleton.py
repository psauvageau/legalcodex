import unittest

from legalcodex._singleton import Singleton, SingletonMeta


class SampleSingleton(Singleton):
    def __init__(self) -> None:
        # Track how many times __init__ runs to ensure the singleton guards it.
        self.init_calls = getattr(self, "init_calls", 0) + 1


class TestSingleton(unittest.TestCase):
    def tearDown(self) -> None:
        # Clear the cached instance to avoid leaking state across tests.
        SingletonMeta._instances.pop(SampleSingleton, None)

    def test_repeated_instantiation_returns_same_object(self) -> None:
        first = SampleSingleton()
        second = SampleSingleton()

        self.assertIs(first, second)
        self.assertEqual(first.init_calls, 1)
        self.assertEqual(second.init_calls, 1)
