# -*- coding: utf-8 -*-
'''
Copyright (C) Gabor Karsay 2021 <gabor.karsay@gmx.at>

This program is free software: you can redistribute it and/or
modify it under the terms of the GNU General Public License as published
by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful, but
WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program.  If not, see <https://www.gnu.org/licenses/>.
'''

import unittest
import uno
from unotest import UnoRemoteConnection

from Parlatype import getDocumentLink
from Parlatype import setDocumentLink
from Parlatype import removeDocumentLink


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

    def test_empty_get(self):
        """
        Get empty custom property "Parlatype"
        """

        doc = self.__class__._uno.getDoc()

        # Initially empty document has no custom property
        self.assertIsNone(getDocumentLink(doc))

    def test_set_and_get(self):
        """
        Set custom property "Parlatype"
        """

        doc = self.__class__._uno.getDoc()

        setDocumentLink(doc, "http://test")
        self.assertEqual(getDocumentLink(doc), "http://test")

    def test_remove_and_get(self):
        """
        Remove custom property "Parlatype"
        """

        doc = self.__class__._uno.getDoc()

        setDocumentLink(doc, "http://test")
        self.assertEqual(getDocumentLink(doc), "http://test")

        removeDocumentLink(doc)
        self.assertIsNone(getDocumentLink(doc))


if __name__ == '__main__':
    unittest.main()
