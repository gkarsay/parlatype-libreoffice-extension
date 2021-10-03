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
import sys
import gettext
from enum import Enum, auto
from com.sun.star.awt.MessageBoxType import MESSAGEBOX

if sys.platform == "linux":
    import dbus

if sys.platform == "win32":
    from parlatype_win32api import *

MAX_TIMESTAMP_CHARS = 11
MIN_TIMESTAMP_CHARS = 4

_ = gettext.gettext


# Defined in Parlatype: src/pt-win32-copydata.h
class Cmd(Enum):
    PLAY_PAUSE = 0
    GOTO_TIMESTAMP = auto()
    JUMP_BACK = auto()
    JUMP_FORWARD = auto()
    DECREASE_SPEED = auto()
    INCREASE_SPEED = auto()
    OPEN_FILE = auto()
    PRESENT_WINDOW = auto()
    GET_TIMESTAMP = auto()
    GET_URI = auto()
    RESPONSE_TIMESTAMP = auto()
    RESPONSE_URI = auto()


def showMessage(ctx, message):
    toolkit = ctx.ServiceManager.createInstance('com.sun.star.awt.Toolkit')
    parent = toolkit.getDesktopWindow()
    dlg = toolkit.createMessageBox(
        parent, MESSAGEBOX, 1, _("Parlatype"), message)
    return dlg.execute()


def _getErrorMessage():
    msgbuffer = LPWSTR()
    FormatMessage(FORMAT_MESSAGE_FROM_SYSTEM | FORMAT_MESSAGE_ALLOCATE_BUFFER,
                  None,
                  GetLastError(),
                  0,
                  cast(byref(msgbuffer), LPWSTR),
                  0,
                  None)
    msg = msgbuffer.value.rstrip()
    LocalFree(msgbuffer)
    return msg


def _getParlatypeWin32String(request_string):
    pipe = CreateFile(pipename,
                      GENERIC_READ | GENERIC_WRITE,
                      0,
                      None,
                      OPEN_EXISTING,
                      0,
                      None)

    if (pipe == INVALID_HANDLE_VALUE):
        raise Exception("CreateFile: {}".format(_getErrorMessage()))

    mode = c_ulong(PIPE_READMODE_MESSAGE)
    success = SetNamedPipeHandleState(pipe,
                                      byref(mode),
                                      None,
                                      None)
    if (not success):
        CloseHandle(pipe)
        raise Exception("SetNamedPipeHandleState: {}".format(
            _getErrorMessage()))

    request_bytes = request_string.encode('utf-8')
    read_buffer = create_string_buffer(READBUFSIZE)
    num_read = c_ulong(0)

    success = TransactNamedPipe(pipe,
                                c_char_p(request_bytes),
                                len(request_bytes),
                                read_buffer,
                                READBUFSIZE,
                                byref(num_read),
                                None)

    if success == 0 and GetLastError() != ERROR_MORE_DATA:
        CloseHandle(pipe)
        raise Exception("TransactNamedPipe: {}".format(_getErrorMessage()))

    result = read_buffer.value[:num_read.value]

    while True:
        if success:
            break

        success = ReadFile(pipe,
                           read_buffer,
                           READBUFSIZE,
                           byref(num_read),
                           None)
        if (success == 0 and GetLastError() != ERROR_MORE_DATA):
            CloseHandle(pipe)
            raise Exception("ReadFile: {}".format(_getErrorMessage()))

        result += read_buffer.value[:num_read.value]

    CloseHandle(pipe)
    result = result.decode('utf-8')
    if result == "Unknown request":
        raise Exception("Unknown Parlatype request: {}".format(result))
    elif result == "NONE":
        return None
    return result


def _getParlatypeLinuxString(request):
    iface = _getDBUSService()
    if request == "GetURI":
        result = iface.GetURI()
    elif request == "GetTimestamp":
        result = iface.GetTimestamp()
    else:
        raise Exception("Unknown Parlatype request: {}".format(request))
    if result == "":
        return None
    else:
        return result


def setGettextDomain(ctx):
    info = ctx.getByName(
        "/singletons/com.sun.star.deployment.PackageInformationProvider")

    extension_uri = info.getPackageLocation("org.parlatype.loextension")
    extension_path = uno.fileUrlToSystemPath(extension_uri)
    locale_path = os.path.join(extension_path, 'locale')

    gettext.bindtextdomain('parlatype_lo', locale_path)
    gettext.textdomain('parlatype_lo')


def _getDBUSService():
    bus = dbus.SessionBus()
    if bus.name_has_owner('org.parlatype.Parlatype') is False:
        return None

    proxy = dbus.SessionBus().get_object(
            "org.parlatype.Parlatype",
            "/org/parlatype/parlatype")
    return dbus.Interface(proxy, "org.parlatype.Parlatype")


def ParlatypeIsRunning(ctx):
    if sys.platform == 'linux':
        iface = _getDBUSService()
        if iface is None:
            return False
        else:
            return True

    if sys.platform == 'win32':
        try:
            hwnd = FindWindow("ParlatypeHiddenWindowClass",
                              "ParlatypeHiddenWindowTitle")
        except Exception as e:
            showMessage(ctx, str(e))
        return hwnd > 0


def getParlatypeString(request):
    if sys.platform == 'linux':
        return _getParlatypeLinuxString(request)

    if sys.platform == 'win32':
        return _getParlatypeWin32String(request)


def _sendParlatypeWin32Command(command_id, string):
    hwnd = FindWindow("ParlatypeHiddenWindowClass",
                      "ParlatypeHiddenWindowTitle")
    if hwnd == 0:
        return

    cds = COPYDATASTRUCT()
    cds.dwData = command_id
    if string:
        string = string.encode('ansi')
        cds.cbData = ctypes.sizeof(ctypes.create_string_buffer(string))
        cds.lpData = cast(c_char_p(string), c_void_p)
    else:
        cds.cbData = 0
        cds.lpData = None

    SendMessage(hwnd, WM_COPYDATA, 0, byref(cds))


def sendParlatypeCommand(ctx, command_id, arg):
    if sys.platform == 'linux':
        service = _getDBUSService()
        if service is None:
            # Parlatype is not running, return silently
            return
        try:
            if command_id == Cmd.PLAY_PAUSE.value:
                service.PlayPause()
            elif command_id == Cmd.GOTO_TIMESTAMP.value:
                service.GotoTimestamp(arg)
            elif command_id == Cmd.JUMP_BACK.value:
                service.JumpBack()
            elif command_id == Cmd.JUMP_FORWARD.value:
                service.JumpForward()
            elif command_id == Cmd.DECREASE_SPEED.value:
                service.DecreaseSpeed()
            elif command_id == Cmd.INCREASE_SPEED.value:
                service.IncreaseSpeed()
        except Exception as e:
            showMessage(ctx, str(e))

    if sys.platform == 'win32':
        try:
            if command_id == Cmd.PLAY_PAUSE.value:
                _sendParlatypeWin32Command(Cmd.PLAY_PAUSE.value, None)
            elif command_id == Cmd.GOTO_TIMESTAMP.value:
                _sendParlatypeWin32Command(Cmd.GOTO_TIMESTAMP.value, arg)
            elif command_id == Cmd.JUMP_BACK.value:
                _sendParlatypeWin32Command(Cmd.JUMP_BACK.value, None)
            elif command_id == Cmd.JUMP_FORWARD.value:
                _sendParlatypeWin32Command(Cmd.JUMP_FORWARD.value, None)
            elif command_id == Cmd.DECREASE_SPEED.value:
                _sendParlatypeWin32Command(Cmd.DECREASE_SPEED.value, None)
            elif command_id == Cmd.INCREASE_SPEED.value:
                _sendParlatypeWin32Command(Cmd.INCREASE_SPEED.value, None)
        except Exception as e:
            showMessage(ctx, str(e))


def getTextRange(controller):
    # the writer controller impl supports
    # the css.view.XSelectionSupplier interface
    xSelectionSupplier = controller

    selection = xSelectionSupplier.getSelection()

    # selection can be a XTextRange, XTextTableCursor and possibly others.
    # We want XTextRange with an XIndexAccess interface to use .getCount() and
    # .getByIndex().
    try:
        count = selection.getCount()
    except AttributeError:
        # ignore selection without XIndexAccess interface
        return None

    # don't mess around with multiple selections
    if (count != 1):
        return None

    textrange = selection.getByIndex(0)

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
