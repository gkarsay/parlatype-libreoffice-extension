import unittest
import uno
from unotest import UnoRemoteConnection

import parlatype_utils as pt_utils


class TestUtils(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._uno = UnoRemoteConnection({'program': 'soffice',
                                        'verbose': False})
        cls._uno.setUp()
        cls.document = cls._uno.openEmptyWriterDoc()

    @classmethod
    def tearDownClass(cls):
        cls._uno.tearDown()

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

    def test_extractTimestamp(self):
        """
        Test extractTimestamp()
        """

        # Get the empty document and insert a string (overwriting)
        doc = self.__class__._uno.getDoc()
        text = doc.Text
        cursor = text.createTextCursor()
        text.insertString(cursor, "#2:48#", True)

        # Get current selections
        controller = doc.getCurrentController()
        selections = controller.getSelection()

        # Get first (and in this case only) selection
        sel = selections.getByIndex(0)

        # Get cursor of selection (it is at the end of the inserted text)
        cursor = sel.getText().createTextCursorByRange(sel)

        # Move cursor (without expanding selection)
        cursor.goLeft(1, False)

        # Set selection
        controller.select(cursor)

        timestamp = pt_utils.extractTimestamp(controller)
        self.assertEqual(timestamp, '2:48')


if __name__ == '__main__':
    unittest.main()
