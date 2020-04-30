# -*- coding: utf-8 -*-
'''
Copyright (C) Gabor Karsay 2016-2020 <gabor.karsay@gmx.at>

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

import uno
import os
import gettext
import dbus
from com.sun.star.awt.MessageBoxType import MESSAGEBOX


MAX_TIMESTAMP_CHARS = 11
MIN_TIMESTAMP_CHARS = 4

_ = gettext.gettext


def showMessage(ctx, message):
    toolkit = ctx.ServiceManager.createInstance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    dlg = toolkit.createMessageBox(
        parent, MESSAGEBOX, 1, _("Parlatype"), message)
    return dlg.execute()


def setGettextDomain(ctx):
    info = ctx.getByName(
        "/singletons/com.sun.star.deployment.PackageInformationProvider")

    extension_uri = info.getPackageLocation("org.parlatype.loextension")
    extension_path = uno.fileUrlToSystemPath(extension_uri)
    locale_path = os.path.join(extension_path, 'locale')

    gettext.bindtextdomain('parlatype_lo', locale_path)
    gettext.textdomain('parlatype_lo')


def getDBUSService():
    bus = dbus.SessionBus()
    if bus.name_has_owner('org.parlatype.Parlatype') is False:
        return None

    proxy = dbus.SessionBus().get_object(
            "org.parlatype.Parlatype",
            "/org/parlatype/parlatype")
    return dbus.Interface(proxy, "org.parlatype.Parlatype")


def getTextRange(controller):
    # the writer controller impl supports
    # the css.view.XSelectionSupplier interface
    xSelectionSupplier = controller

    xIndexAccess = xSelectionSupplier.getSelection()
    count = xIndexAccess.getCount()

    # don't mess around with multiple selections
    if (count != 1):
        return None

    textrange = xIndexAccess.getByIndex(0)

    # don't mess around with selections, just plain cursor
    if (len(textrange.getString()) == 0):
        return textrange
    else:
        return None


def _isValidCharacter(char):
    if (char.isdigit() or char == ":" or char == "." or char == "-"):
        return True
    return False


def extractTimestamp(controller):
    textrange = getTextRange(controller)
    if (textrange is None):
        return None

    xText = textrange.getText()
    cursor = xText.createTextCursorByRange(textrange)

    # select first char on the left, no success if at start of document
    success = cursor.goLeft(1, True)

    if (success):
        i = 0
        while (_isValidCharacter(cursor.getString()[0])
               and i < MAX_TIMESTAMP_CHARS):
            success = cursor.goLeft(1, True)
            i += 1
        if (success):
            cursor.goRight(1, True)
        cursor.collapseToStart()

    cursor.goRight(2, True)

    i = 0
    while (_isValidCharacter(cursor.getString()[-1:])
           and i < MAX_TIMESTAMP_CHARS):
        success = cursor.goRight(1, True)
        i += 1
    if (success):
        cursor.goLeft(1, True)

    candidate = cursor.getString()
    if (len(candidate) < MIN_TIMESTAMP_CHARS
            or len(candidate) > MAX_TIMESTAMP_CHARS):
        return None
    else:
        return candidate
