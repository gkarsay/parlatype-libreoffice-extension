import unittest

import parlatype_utils as pt_utils


class TestUtils(unittest.TestCase):
    def test_isValidCharacter(self):
        """
        Test _isValidCharacter()
        """

        # Complete list of valid characters
        valid_characters = ['.', ':', '-',
                            '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
        for character in valid_characters:
            self.assertTrue(pt_utils._isValidCharacter(character))

        # Selection of invalid characters
        invalid_characters = ['A', 'a', 'z', 'Z', '#', ';', ' ']
        for character in invalid_characters:
            self.assertFalse(pt_utils._isValidCharacter(character))


if __name__ == '__main__':
    unittest.main()
