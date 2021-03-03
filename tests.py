from unittest import TestCase
from hashlib import sha256
from hasher import SHA256
from string import ascii_letters
from random import choice


class TestHashing(TestCase):

    @staticmethod
    def make_random_string(length):
        return ''.join([choice(ascii_letters) for _ in range(length)])

    def _test_strings(self, string_len, number=10):
        for i in range(1, number + 1):
            yield i, self.make_random_string(string_len)

    def test(self):
        for length in range(100):
            for i, string in self._test_strings(length):
                reference_hash = sha256(string.encode()).hexdigest()
                test_hash = SHA256().hash(string)

                self.assertEqual(reference_hash, test_hash, f'Testing word {string}')
