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
from parlatype_utils import Cmd


def InsertTimestamp(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    textrange = pt_utils.getTextRange(controller)
    if (textrange is None):
        return

    try:
        timestamp = pt_utils.getParlatypeString("GetTimestamp")
        if timestamp is not None:
            textrange.setString(timestamp)
    except Exception:
        pass


def InsertTimestampOnNewLine(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    textrange = pt_utils.getTextRange(controller)
    if (textrange is None):
        return

    try:
        timestamp = pt_utils.getParlatypeString("GetTimestamp")
        if timestamp is not None:
            textrange.setString("\n" + timestamp + " ")
    except Exception:
        pass


def GotoTimestamp(*args):
    doc = XSCRIPTCONTEXT.getDocument()
    controller = doc.getCurrentController()
    timestamp = pt_utils.extractTimestamp(controller)
    if (timestamp is None):
        return

    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.GOTO_TIMESTAMP.value, timestamp)


def PlayPause(*args):
    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.PLAY_PAUSE.value, None)


def JumpBack(*args):
    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.JUMP_BACK.value, None)


def JumpForward(*args):
    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.JUMP_FORWARD.value, None)


def IncreaseSpeed(*args):
    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.INCREASE_SPEED.value, None)


def DecreaseSpeed(*args):
    pt_utils.sendParlatypeCommand(XSCRIPTCONTEXT.getComponentContext(),
                                  Cmd.DECREASE_SPEED.value, None)


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
