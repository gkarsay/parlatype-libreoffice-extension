# -*- coding: utf-8 -*-
'''
Copyright (C) Gabor Karsay 2020 <gabor.karsay@gmx.at>

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


import ctypes
from ctypes import c_int, c_uint, c_long, c_ulong
from ctypes import c_char_p, c_wchar_p, c_void_p
from ctypes import cast, byref, Structure, WINFUNCTYPE, POINTER
from ctypes import create_string_buffer, create_unicode_buffer
from ctypes.wintypes import HINSTANCE, LPARAM, DWORD, LPWSTR


''' Copydata '''

GetModuleHandle = ctypes.windll.kernel32.GetModuleHandleW
FindWindow = ctypes.windll.user32.FindWindowW
SendMessage = ctypes.windll.user32.SendMessageW
RegisterClass = ctypes.windll.user32.RegisterClassW
CreateWindow = ctypes.windll.user32.CreateWindowExW
DefWindowProc = ctypes.windll.user32.DefWindowProcW
GetMessage = ctypes.windll.user32.GetMessageW
TranslateMessage = ctypes.windll.user32.TranslateMessage
DispatchMessage = ctypes.windll.user32.DispatchMessageW

WM_COPYDATA = 74
WNDPROC = WINFUNCTYPE(c_long, c_int, c_uint, c_int, c_int)


class WNDCLASS(Structure):
    _fields_ = [
        ('style', c_uint),
        ('lpfnWndProc', WNDPROC),
        ('cbClsExtra', c_int),
        ('cbWndExtra', c_int),
        ('hInstance', HINSTANCE),
        ('hIcon', c_int),
        ('hCursor', c_int),
        ('hbrBackground', c_int),
        ('lpszMenuName', c_char_p),
        ('lpszClassName', c_char_p)
    ]


class COPYDATASTRUCT(Structure):
    _fields_ = [
        ('dwData', LPARAM),
        ('cbData', DWORD),
        ('lpData', c_void_p)
    ]


PCOPYDATASTRUCT = POINTER(COPYDATASTRUCT)


''' Named Pipe '''

CreateFile = ctypes.windll.kernel32.CreateFileW
SetNamedPipeHandleState = ctypes.windll.kernel32.SetNamedPipeHandleState
TransactNamedPipe = ctypes.windll.kernel32.TransactNamedPipe
ReadFile = ctypes.windll.kernel32.ReadFile
CloseHandle = ctypes.windll.kernel32.CloseHandle

GENERIC_READ = 0x80000000
GENERIC_WRITE = 0x40000000
OPEN_EXISTING = 0x3
INVALID_HANDLE_VALUE = -1
PIPE_READMODE_MESSAGE = 0x2
ERROR_PIPE_BUSY = 231
ERROR_MORE_DATA = 234
BUFSIZE = 512
READBUFSIZE = 5

pipename = "\\\\.\\pipe\\xyz.parlatype.ipc"


''' Error handling '''

GetLastError = ctypes.windll.kernel32.GetLastError
FormatMessage = ctypes.windll.kernel32.FormatMessageW
LocalFree = ctypes.windll.kernel32.LocalFree

FORMAT_MESSAGE_ALLOCATE_BUFFER = 0x100
FORMAT_MESSAGE_FROM_SYSTEM = 0x1000
