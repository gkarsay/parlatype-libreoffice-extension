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

import parlatype_utils as pt_utils


def InsertTimestamp(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    textrange = pt_utils.getTextRange(controller)
    if (textrange is None):
        return

    service = pt_utils.getDBUSService()

    try:
        textrange.setString(service.GetTimestamp())
    except Exception:
        pass


def InsertTimestampOnNewLine(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    textrange = pt_utils.getTextRange(controller)
    if (textrange is None):
        return

    service = pt_utils.getDBUSService()

    try:
        textrange.setString("\n" + service.GetTimestamp() + " ")
    except Exception:
        pass


def GotoTimestamp(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    timestamp = pt_utils.extractTimestamp(controller)
    if (timestamp is None):
        return

    service = pt_utils.getDBUSService()

    try:
        service.GotoTimestamp(timestamp)
    except Exception:
        pass


def PlayPause(*args):
    service = pt_utils.getDBUSService()

    try:
        service.PlayPause()
    except Exception:
        pass


def JumpBack(*args):
    service = pt_utils.getDBUSService()

    try:
        service.JumpBack()
    except Exception:
        pass


def JumpForward(*args):
    service = pt_utils.getDBUSService()

    try:
        service.JumpForward()
    except Exception:
        pass


def IncreaseSpeed(*args):
    service = pt_utils.getDBUSService()

    try:
        service.IncreaseSpeed()
    except Exception:
        pass


def DecreaseSpeed(*args):
    service = pt_utils.getDBUSService()

    try:
        service.DecreaseSpeed()
    except Exception:
        pass


# Lists the scripts, that shall be visible inside LibreOffice.
g_exportedScripts = \
    InsertTimestamp,\
    InsertTimestampOnNewLine,\
    GotoTimestamp,\
    PlayPause,\
    JumpBack,\
    JumpForward,\
    IncreaseSpeed,\
    DecreaseSpeed,
