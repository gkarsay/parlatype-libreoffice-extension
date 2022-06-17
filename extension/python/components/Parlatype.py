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

import sys
import os
import subprocess
import threading
import uno
import unohelper
from com.sun.star.lang import XServiceInfo
from com.sun.star.frame import XDispatchProvider
from com.sun.star.frame import XDispatch
from com.sun.star.frame import FeatureStateEvent
from com.sun.star.awt import XKeyHandler
from com.sun.star.awt import XMouseClickHandler
from com.sun.star.document import XDocumentEventListener
from com.sun.star.beans import PropertyValue
from com.sun.star.beans import XPropertyChangeListener
from com.sun.star.beans.PropertyAttribute import MAYBEVOID
from com.sun.star.beans.PropertyAttribute import BOUND
from com.sun.star.beans.PropertyAttribute import REMOVEABLE
import gettext
import parlatype_utils as pt_utils
from parlatype_utils import Cmd, showMessage

if sys.platform == 'win32':
    from winreg import ConnectRegistry, OpenKey, QueryValueEx, CloseKey
    from winreg import HKEY_LOCAL_MACHINE, KEY_READ


_ = gettext.gettext

ImplementationName = "org.parlatype.ProtocolHandler"
ServiceName = "com.sun.star.frame.ProtocolHandler"
Protocol = "org.parlatype.loextension:"


current_timestamp = ''


class OptionsListener(unohelper.Base, XPropertyChangeListener):
    def __init__(self, parent, controller):
        self.parent = parent
        self.controller = controller
        # print("Optionslistener init for", self.controller.getTitle())

    def propertyChange(self, Event):
        # Event.OldValue, Event.NewValue and Event.Further seem to be always
        # None and can't be used for anything.

        # print("Property \"{}\" changed".format(Event.PropertyName))

        self.parent.updateTimestampOptions(self.controller)

        return False

    def disposing(self, source):
        # print("Parlatype Extension: OptionsListener removed")
        pass


class KeyHandler(unohelper.Base, XKeyHandler):

    def __init__(self, parent):
        self.parent = parent

    def keyPressed(self, oEvent):
        return False

    def keyReleased(self, oEvent):
        self.parent._checkCursorforTimestamp()
        return False

    def disposing(self, source):
        pass


class MouseHandler(unohelper.Base, XMouseClickHandler):

    def __init__(self, parent):
        self.parent = parent

    def mousePressed(self, oEvent):
        return False

    def mouseReleased(self, oEvent):
        self.parent._checkCursorforTimestamp(goto_current_timestamp=True)
        return False

    def disposing(self, source):
        pass


def removeDocumentLink(doc):
    '''Remove custom document property "Parlatype".'''
    doc_prop = doc.getDocumentProperties()
    doc_uprop = doc_prop.getUserDefinedProperties()
    doc_uprop.removeProperty('Parlatype')


def setDocumentLink(doc, link):
    '''Create custom document property "Parlatype", if it doesn't exist,
       and set its value.'''
    doc_prop = doc.getDocumentProperties()
    doc_uprop = doc_prop.getUserDefinedProperties()
    set = doc_uprop.getPropertySetInfo()
    if set.hasPropertyByName('Parlatype') is False:
        doc_uprop.addProperty('Parlatype',
                              MAYBEVOID + BOUND + REMOVEABLE,
                              "")  # default value
    doc_uprop.setPropertyValue('Parlatype', link)


def getDocumentLink(doc):
    '''Get value of custom document property "Parlatype".'''
    doc_prop = doc.getDocumentProperties()
    doc_uprop = doc_prop.getUserDefinedProperties()
    set = doc_uprop.getPropertySetInfo()
    if set.hasPropertyByName('Parlatype') is False:
        return None
    else:
        return doc_uprop.getPropertyValue('Parlatype')


def insertTimestamp(ctx):
    smgr = ctx.getServiceManager()
    desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()
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


def launchFlatpak(ctx, url):
    cmdline = ["flatpak", "run", "org.parlatype.Parlatype"]
    if url is not None:
        cmdline.append(url)

    try:
        p = subprocess.Popen(cmdline, universal_newlines=True,
                             stderr=subprocess.PIPE)
    except FileNotFoundError:
        # This assumes we tried to launch a regular binary first.
        # Neither regular Parlatype nor flatpak is installed.
        showMessage(ctx, _("Parlatype is not installed."))
        return

    err = p.stderr.readline()
    if err == "" or err is None:
        return

    # AppArmor profile for LibreOffice may prevent launching flatpak:
    # bwrap: Can't open /proc/self/mountinfo: Permission denied
    # bwrap: Can't read from privileged_op_socket
    if "bwrap" in err:
        showMessage(ctx, _("It seems like the AppArmor profile for "
                           "LibreOffice prevents launching Flatpak."))
        return

    # If not installed, we get a localized error message.
    # Lets see, if it is installed via flatpak info.
    try:
        p = subprocess.run(["flatpak", "info", "org.parlatype.Parlatype"],
                           check=True)
    except subprocess.CalledProcessError:
        showMessage(ctx, _("Parlatype is not installed."))
        return

    # Whatever that may be ...
    showMessage(ctx, err)


def openParlatype(ctx):
    if sys.platform == 'win32':
        registry = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        try:
            key = OpenKey(registry,
                          r'SOFTWARE\Microsoft\Windows' +
                          r'\CurrentVersion\Uninstall\Parlatype',
                          0, KEY_READ)
        except FileNotFoundError:
            CloseKey(registry)
            # TODO add a clickable download link
            showMessage(ctx, _("Parlatype is not installed."))
            return
        [path, regtype] = (QueryValueEx(key, "InstallLocation"))
        CloseKey(key)
        CloseKey(registry)
        cmd = os.path.join(path, 'bin', 'parlatype.exe')
        cmdline = [cmd]
    else:
        cmdline = ["parlatype"]

    smgr = ctx.getServiceManager()
    desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", ctx)
    doc = desktop.getCurrentComponent()
    url = getDocumentLink(doc)
    if url is not None and len(url) > 0:
        cmdline.append(url)

    try:
        subprocess.Popen(cmdline)
    except FileNotFoundError:
        # Try Flatpak in a different thread, because we're waiting for its
        # return code/stderr and that would keep the button pressed.
        t = threading.Thread(target=launchFlatpak, args=(self.ctx, url,))
        t.daemon = True
        t.start()


class ParlatypeController(object):
    """ Controls Parlatype. """

    def __init__(self, ctx):
        self.ctx = ctx
        self.key_handler = KeyHandler(self)
        self.mouse_handler = MouseHandler(self)
        self.options_listener = None
        self.link_url = None
        self.linked = False
        smgr = self.ctx.getServiceManager()
        self.desktop = smgr.createInstanceWithContext(
            "com.sun.star.frame.Desktop", self.ctx)

    def _checkCursorforTimestamp(self, goto_current_timestamp=False):
        global current_timestamp
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()
        timestamp = pt_utils.extractTimestamp(controller)

        if (timestamp is None):
            current_timestamp = ''
            return
        if (timestamp == current_timestamp
                and goto_current_timestamp is False):
            return
        current_timestamp = timestamp

        pt_utils.sendParlatypeCommand(self.ctx,
                                      Cmd.GOTO_TIMESTAMP.value,
                                      timestamp)

    def _getOptionsReader(self):
        smgr = self.ctx.getServiceManager()
        cfg = smgr.createInstanceWithContext(
            'com.sun.star.configuration.ConfigurationProvider', self.ctx)
        node = PropertyValue()
        node.Name = 'nodepath'
        node.Value = '/org.parlatype.config'
        return cfg.createInstanceWithArguments(
             'com.sun.star.configuration.ConfigurationAccess', (node,))

    def updateTimestampOptions(self, controller):
        # Get options
        reader = self._getOptionsReader()
        keys = reader.getPropertyValue('TimestampKeys')
        mouse = reader.getPropertyValue('TimestampMouse')

        # Add or remove Key and Mouse event listeners to document
        doc = self.desktop.getCurrentComponent()
        if (keys == 1):
            controller.addKeyHandler(self.key_handler)
        else:
            controller.removeKeyHandler(self.key_handler)

        if (mouse == 1):
            controller.addMouseClickHandler(self.mouse_handler)
        else:
            controller.removeMouseClickHandler(self.mouse_handler)

    def deactivateTimestampScanner(self):
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()
        controller.removeKeyHandler(self.key_handler)
        controller.removeMouseClickHandler(self.mouse_handler)
        reader = self._getOptionsReader()
        reader.removePropertyChangeListener('TimestampKeys',
                                            self.options_listener)
        reader.removePropertyChangeListener('TimestampMouse',
                                            self.options_listener)

    def activateTimestampScanner(self):
        doc = self.desktop.getCurrentComponent()
        controller = doc.getCurrentController()

        # Get options
        reader = self._getOptionsReader()
        self.updateTimestampOptions(controller)

        # Attach Options listener
        try:
            if self.options_listener is None:
                self.options_listener = OptionsListener(self, controller)
            reader.addPropertyChangeListener('TimestampKeys',
                                             self.options_listener)
            reader.addPropertyChangeListener('TimestampMouse',
                                             self.options_listener)
        except Exception as e:
            showMessage(self.ctx, str(e))

    def setLinkedStatus(self, status):
        self.linked = status

    def unlinkMedia(self):
        try:
            doc = self.desktop.getCurrentComponent()
            removeDocumentLink(doc)
            self.linked = False
            return True
        except Exception as e:
            showMessage(self.ctx, "{}: {}".format(e.__class__.__name__,
                                                  str(e)))
            return False

    def linkMedia(self):
        doc = self.desktop.getCurrentComponent()
        previous = getDocumentLink(doc)
        if previous is not None and len(previous) > 0:
            showMessage(self.ctx, "Already linked to {}.".format(previous))
            return

        try:
            if pt_utils.ParlatypeIsRunning(self.ctx) is False:
                showMessage(self.ctx, _("Please open Parlatype first."))
                return
        except Exception as e:
            showMessage(self.ctx, str(e))
            return
        try:
            media = pt_utils.getParlatypeString("GetURI")
        except Exception as e:
            showMessage(self.ctx, str(e))
            return
        if media is None:
            showMessage(self.ctx, _("Please open a media file first."))
            return

        setDocumentLink(doc, media)
        self.linked = True

    def link(self):
        ''' This is a toggle type method, it can mean link or unlink. '''
        if self.linked:
            if self.unlinkMedia():
                self.deactivateTimestampScanner()
                return True
            else:
                return False
        else:
            self.linkMedia()
            if self.linked:
                self.activateTimestampScanner()
                return True
            else:
                return False


class EventListener(unohelper.Base, XDocumentEventListener):
    def __init__(self, parent):
        self.parent = parent
        pass

    # Sequence of events if a document is opened or created:
    # 1) OnViewCreated
    # 2) OnPageCountChange
    # 3) OnNew or OnLoad
    # 4) OnLayoutFinished
    #
    # Sequence of events if a new window is opened (with the same content
    # as the currently open window) in the menu: Window > New Window
    # 1) OnViewCreated
    # 2) OnPageCountChange
    #
    # OnViewCreated we still get the LinkStatus of the previously opened
    # document, not the new one!

    def documentEventOccured(self, event):
        if event.EventName == "OnLayoutFinished":
            self.parent.updateLinkButton()
            self.parent.removeDocumentListener()

        if event.EventName == "OnViewCreated":
            self.parent.updateLinkButton()

    def disposing(event):
        pass


class ToolbarHandler(unohelper.Base, XServiceInfo,
                     XDispatchProvider, XDispatch):

    ''' This class is called for each new view and in each view for each
        command ("open", "link", "timestamp"). '''

    def __init__(self, ctx):
        self.ctx = ctx
        self.listener = None
        self.status = False
        self.ev = None
        self.doc_listener = None
        self.pt = ParlatypeController(ctx)
        self.GEB = self.ctx.getValueByName(
            "/singletons/com.sun.star.frame.theGlobalEventBroadcaster")
        pt_utils.setGettextDomain(ctx)

    # XServiceInfo
    def supportsService(self, name):
        return (name == ServiceName)

    def getImplementationName(self):
        return ImplementationName

    def getSupportedServiceNames(self):
        return (ServiceName,)

    # XDispatchProvider
    def queryDispatch(self, url, target_frame_name, search_flags):
        if url.Protocol != Protocol:
            return None
        if url.Path == "link":
            ''' Add a DocumentEventListener. On event "OnLoad" we want to
                check, if the document is already linked and set the toolbar
                button appropriately.
                We don't add the listener to our document, because
                queryDispatch is called even before there is a document object.
                Therefore we use the Global Event Broadcaster which notifies of
                all documents. It removes itself "OnLayoutFinished" which
                happens after "OnLoad" or "OnNew" respectively.
                An alternative approach didn't work: A Job triggered on event
                "OnLoad". I was not able to change the button's state. '''
            self.doc_listener = EventListener(self)
            self.GEB.addDocumentEventListener(self.doc_listener)
        return self

    def queryDispatches(self, requests):
        # This is actually never called
        dispatches = \
            [self.queryDispatch(r.FeatureURL, r.FrameName, r.SearchFlags)
                for r in requests]
        return dispatches

    # XDispatch
    def dispatch(self, url, args):
        if url.Protocol == Protocol:
            if url.Path == "open":
                openParlatype(self.ctx)
            elif url.Path == "link":
                if self.pt.link() is True:
                    self.status = not self.status
                    self.ev.State = self.status
                    self.listener.statusChanged(self.ev)
            elif url.Path == "timestamp":
                insertTimestamp(self.ctx)

    def addStatusListener(self, control, url):
        ''' The StatusListener enables controlling toolbar items. We are only
            interested in the "link" item to control its toggle state. State
            false means unpressed, state true is pressed in. To change the
            state, a FeatureEventState has to be sent via the listener's
            statusChanged method. This is done in self.dispatch. '''
        self.listener = control
        self.ev = FeatureStateEvent()
        self.ev.FeatureURL = url
        self.ev.IsEnabled = True
        self.ev.Requery = False
        self.ev.Source = self
        self.ev.State = self.status

    def removeStatusListener(self, control, url):
        pass

    def removeDocumentListener(self):
        self.GEB.removeDocumentEventListener(self.doc_listener)

    def updateLinkButton(self):
        smgr = self.ctx.getServiceManager()
        desktop = smgr.createInstanceWithContext(
                "com.sun.star.frame.Desktop", self.ctx)
        doc = desktop.getCurrentComponent()
        url = getDocumentLink(doc)
        if url is None or len(url) == 0:
            self.pt.setLinkedStatus(False)
            self.pt.deactivateTimestampScanner()
            self.status = False
            self.ev.State = self.status
            self.listener.statusChanged(self.ev)
        else:
            self.pt.setLinkedStatus(True)
            self.pt.activateTimestampScanner()
            self.status = True
            self.ev.State = self.status
            self.listener.statusChanged(self.ev)


# uno implementation
g_ImplementationHelper = unohelper.ImplementationHelper()
g_ImplementationHelper.addImplementation(
    ToolbarHandler,
    ImplementationName,
    (ServiceName,),)
