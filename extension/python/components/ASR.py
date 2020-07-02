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

import unohelper
import sys
from com.sun.star.task import XJob
import threading
import parlatype_utils as pt_utils
if sys.platform == "linux":
    import dbus
    from gi.repository import GLib
    from dbus.mainloop.glib import DBusGMainLoop
    import dbus.mainloop.glib

loop = None
hypothesis_range = None


class ASRJob(unohelper.Base, XJob):
    def __init__(self, ctx):
        self.ctx = ctx
        smgr = self.ctx.getServiceManager()
        self.desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)

    def dbus_signal_handler(self, message, signal):
        # The TextRange representing the last hypothesis
        global hypothesis_range

        doc = self.desktop.getCurrentComponent()
        try:
            controller = doc.getCurrentController()
        except AttributeError:
            return

        # Signal may be "ASRHypothesis" or "ASRFinal".
        # A hypothesis is a probable result that will be replaced by the next
        # hypothesis or by the final result.
        # That means: If we had a hypothesis before, it must be replaced by
        # the current message.

        if signal == "ASRCancel":
            hypothesis_range = None
            return

        if hypothesis_range is None:
            # Get current cursor position
            textrange = pt_utils.getTextRange(controller)
        else:
            textrange = hypothesis_range

        # Insert message
        if signal == "ASRFinal":
            message = message + " "
        try:
            textrange.setString(message)
        except Exception as e:
            print(str(e))
        if signal == "ASRHypothesis":
            hypothesis_range = textrange
        else:
            hypothesis_range = None

    def execute(self, args):
        # There should be only one loop running
        global loop

        # Get the event which triggered this job
        if not args:
            return

        for arg in args:
            if arg.Name == "Environment":
                subargs = arg.Value
                for subarg in subargs:
                    if subarg.Name == "EventName":
                        event = subarg.Value

        if event == "OnStartApp":
            if loop:
                return
            # Default context will cause deadlocks when opening other windows,
            # e.g. Options.
            context = GLib.MainContext.new()
            loop = GLib.MainLoop(context)
            DBusGMainLoop(set_as_default=True)
            bus = dbus.SessionBus()
            bus.add_signal_receiver(self.dbus_signal_handler,
                                    bus_name='org.parlatype.Parlatype',
                                    dbus_interface='org.parlatype.Parlatype',
                                    member_keyword='signal')

            # Listen in a thread. LibreOffice will not start up until this
            # job is finished.
            threading.Thread(target=loop.run).start()
            return

        if event == "OnUnload":
            global hypothesis_range
            # Will crash if not cleared
            hypothesis_range = None

        if event == "OnCloseApp":
            if loop:
                loop.quit()
                loop = None


ImplementationName = "org.parlatype.ASRListener"

g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ASRJob, ImplementationName, (ImplementationName,),)
